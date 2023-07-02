import base64
import io
import math

import numpy as np
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from openpyxl.workbook import Workbook
from reliability.Fitters import Fit_Weibull_2P
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadFileForm, BuildingForm, ElectrolyzerTypeForm, ElectrolyzerForm, FactoryForm
from .models import Electrolyzer, PartType, Building, Part, Factory, History
from .utils import weibull_cdf, censor_dates, empirical_cdf, optimize_curve, DAYS_TO_MONTHS


@login_required
def edit_electrolyzer(request, electrolyzer_id):
    electrolyzer = get_object_or_404(Electrolyzer, id=electrolyzer_id)

    if request.method == 'POST':
        form = ElectrolyzerForm(request.POST, instance=electrolyzer)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ElectrolyzerForm(instance=electrolyzer)

    electrolyzer_types = PartType.objects.all()
    # TODO
    buildings = Building.objects.all()

    context = {
        'form': form,
        'electrolyzer': electrolyzer,
        'buildings': buildings,
        'electrolyzer_types': electrolyzer_types,
    }
    return render(request, 'edit_electrolyzer.html', context)


@login_required
def upload_file(request):
    message = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                file = request.FILES['file']
                file_extension = file.name.split('.')[-1]

                part_type = form.cleaned_data['part_type']
                building = form.cleaned_data['building']

                important_cols = ['№', 'Дата запуска', 'Дата поломки']

                if file_extension == 'csv':
                    data = pd.read_csv(file, usecols=important_cols)
                elif file_extension in ['xls', 'xlsx']:
                    data = pd.read_excel(file, usecols=important_cols)
                elif file_extension == 'json':
                    data = pd.read_json(file)
                    if not set(important_cols).issubset(data.columns):
                        raise ValueError("JSON файл не содержит необходимых столбцов")
                else:
                    raise ValueError("Недопустимый формат файла")

                data.columns = ['number', 'launch_date', 'failure_date']

                if data[['number', 'launch_date']].isnull().values.any():
                    raise ValueError('Столбцы "Номер" "Дата запуска" не должны содержать пропущенных значений.')

                data['number'] = data['number'].astype(int)
                data[['launch_date', 'failure_date']] = data[['launch_date', 'failure_date']].apply(pd.to_datetime)

                for row in data.itertuples(index=False):
                    new_part, _ = Part.objects.get_or_create(number=row[0], part_type=part_type,
                                                             building=building)
                    if pd.isnull(row[2]):
                        new_part.history_set.create(launch_date=row[1])
                    else:
                        new_part.history_set.create(launch_date=row[1], failure_date=row[2])

                return redirect('chart')
        except Exception as e:
            message = f"Ошибка во время обработки файла: {str(e)}"

    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form, 'message': message})


def index(request):
    return render(request, 'index.html')


def chart(request):
    return render(request, 'chart.html')


def get_factories(request):
    factories = Factory.objects.all()
    data = [{'id': f.id, 'name': f.name} for f in factories]
    return JsonResponse(data, safe=False)


def get_buildings(request):
    buildings = Building.objects.all().select_related('factory')
    data = [{'id': b.id, 'name': b.name, 'factory': {'name': b.factory.name}} for b in buildings]
    return JsonResponse(data, safe=False)


def get_part_types(request):
    part_types = PartType.objects.all()
    data = [{'id': et.id, 'name': et.name} for et in part_types]
    return JsonResponse(data, safe=False)


def get_oldest_date(request):
    launch_date = History.objects.values_list('launch_date').aggregate(Min('launch_date'))['launch_date__min']
    return JsonResponse({"date": str(launch_date)})


# TODO find a way around this csrf shit
@csrf_exempt
def get_chart(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    forecast_date = request.POST.get('forecast_date')
    part_types = request.POST.getlist('part_type')
    building = request.POST.get('building')

    queue = Part.objects.filter(
        Q(building_id=building, history__launch_date__range=[start_date, end_date]) & (
                Q(history__failure_date__isnull=True) |
                Q(history__failure_date__range=[start_date, end_date])))

    response = {
        'start_date': start_date,
        'end_date': end_date,
        'forecast_date': forecast_date,
        'results': []
    }

    result_data = pd.DataFrame(columns=['Завод', 'Корпус', 'Тип', 'Действующих, шт', 'Отключений, шт'])
    for part_type in part_types:
        values = queue.filter(part_type_id=part_type).values("history__launch_date", "avg_days")
        df = pd.DataFrame.from_records(values)
        df.columns = ['launch_date', 'days']
        df = censor_dates(df, end_date, failure_column='days')

        fit = Fit_Weibull_2P(failures=np.array(df[df['days'].notnull()]['days']),
                             # right_censored=np.array(df[df['running_days'].notnull()]['running_days']),
                             print_results=False,
                             show_probability_plot=False)

        days = (pd.to_datetime(forecast_date) - pd.to_datetime(end_date)).days
        weibull_curve = weibull_cdf(fit.beta, fit.alpha)
        weibull_curve = optimize_curve(weibull_curve, 0.01)

        empirical_curve = empirical_cdf(np.array(df['days'].dropna()))
        empirical_curve = optimize_curve(empirical_curve, 0.01)

        all_count = len(df[df['days'].notnull()].index)
        working_count = len(df[df['days'].isnull()].index)
        failed_percent = 1 - math.exp(-math.pow(days / fit.alpha, fit.beta))
        building_model = Building.objects.get(id=building)
        response['results'].append({
            'weibull_x': list(weibull_curve[:, 0] / DAYS_TO_MONTHS),
            'weibull_y': list(weibull_curve[:, 1] * 100),
            'empirical_x': list(empirical_curve[:, 0] / DAYS_TO_MONTHS),
            'empirical_y': list(empirical_curve[:, 1] * 100),
            'factory': building_model.factory.name,
            'building': building_model.name,
            'type': PartType.objects.get(id=part_type).name,
            'all_count': all_count,
            'working_count': working_count,
            'failed_count': f'{working_count * failed_percent:.2f}',
        })
        result_data.loc[len(result_data.index)] = [building_model.factory.name, building_model.name,
                                                   PartType.objects.get(id=part_type).name, working_count,
                                                   f'{working_count * failed_percent:.2f}']

    workbook = Workbook()
    sheet = workbook.active

    sheet.append(result_data.columns.tolist())  # Write column headers
    for row in result_data.values.tolist():
        sheet.append(row)

    sheet.column_dimensions['D'].width = 30
    sheet.column_dimensions['E'].width = 30

    buffer = io.BytesIO()

    workbook.save(buffer)
    buffer.seek(0)
    file_content = base64.b64encode(buffer.getvalue()).decode('utf-8')
    response['excel_file'] = file_content
    return JsonResponse(response, safe=False)


@login_required
def fb_add(request):
    building_form = BuildingForm()
    factory_form = FactoryForm()
    return render(request, 'fb_add.html',
                  {'building_form': building_form, 'factory_form': factory_form})


def add_building(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Здание добавлено'})
    return JsonResponse({'message': 'Invalid data'}, status=400)


def add_electrolyzer_type(request):
    if request.method == 'POST':
        form = ElectrolyzerTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Тип добавлен'})
    return JsonResponse({'message': 'Invalid data'}, status=400)


def add_factory(request):
    if request.method == 'POST':
        form = FactoryForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Фабрика добавлена'})
    return JsonResponse({'message': 'Invalid data'}, status=400)


def delete_building(request, building_id):
    if request.method == 'POST':
        building = get_object_or_404(Building, id=building_id)
        building.delete()
        return JsonResponse({'message': 'Здание удалено'})
    return JsonResponse({'message': 'Invalid data'}, status=400)


@csrf_exempt
def update_building(request, pk):
    if request.method == "POST":
        # get building instance
        building = get_object_or_404(Building, pk=pk)
        # update building details
        building.name = request.POST.get('name')
        # save changes
        building.save()
        return JsonResponse({"status": "success"})


@csrf_exempt
def delete_factory(request):
    if request.method == 'POST':
        factory_id = request.POST.get('factory_id')
        try:
            factory = Factory.objects.get(pk=factory_id)
            factory.delete()
            return JsonResponse({'message': 'Factory successfully deleted.'})
        except Factory.DoesNotExist:
            return JsonResponse({'message': 'Factory not found.'}, status=404)


def factory_details(request, factory_id):
    factory = get_object_or_404(Factory, pk=factory_id)
    return render(request, 'factory_details.html', {'factory': factory})


def get_factory_buildings(request, factory_id):
    buildings = Building.objects.filter(factory_id=factory_id)
    data = [{'id': b.id, 'name': b.name} for b in buildings]
    return JsonResponse(data, safe=False)


@csrf_exempt
def update_factory(request, factory_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        factory = Factory.objects.get(id=factory_id)
        factory.name = name
        factory.save()
        return JsonResponse({'message': 'Завод успешно обновлен.'})


def building_detail(request, pk):
    building = get_object_or_404(Building, pk=pk)
    return render(request, 'building_details.html', {'building': building})


@csrf_exempt
def update_building(request, building_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        building = Building.objects.get(id=building_id)
        building.name = name
        building.save()
        return JsonResponse({'message': 'Здание успешно обновлено.'})


def get_building_electrolyzers(request, building_id):
    electrolyzers = Electrolyzer.objects.filter(building_id=building_id)
    data = [{
        'id': e.id,
        'number': e.number,
        'launch_date': e.launch_date,
        'failure_date': e.failure_date,
        'days_up': e.days_up,
        'electrolyzer_type': e.electrolyzer_type.name,
    } for e in electrolyzers]
    return JsonResponse(data, safe=False)


@csrf_exempt
def delete_electrolyzer(request, electrolyzer_id):
    if request.method == 'POST':
        Electrolyzer.objects.filter(id=electrolyzer_id).delete()
        return JsonResponse({'message': 'Электролизер успешно удален.'})
    else:
        return JsonResponse({'message': 'Неверный запрос'}, status=400)


def pt_list(request):
    if request.method == 'GET':
        part_types = PartType.objects.all()
        return render(request, 'pt_list.html', {'part_types': part_types})


@csrf_exempt
def add_part_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        PartType.objects.create(name=name)
        return JsonResponse({'message': 'Тип успешно добавлен.'})


@csrf_exempt
def delete_part_type(request, part_type_id):
    if request.method == 'POST':
        PartType.objects.filter(id=part_type_id).delete()
        return JsonResponse({'message': 'Тип электролизёра удален'})


@csrf_exempt
def update_part_type(request, part_type_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        part_type = PartType.objects.get(id=part_type_id)
        part_type.name = name
        part_type.save()
        return JsonResponse({'message': 'Тип электролизёра успешно обновлен.'})


def part_type_details(request, part_type_id):
    part_type = get_object_or_404(PartType, id=part_type_id)
    return render(request, 'part_type_details.html', {'part_type': part_type})


def get_part_type_electrolyzers(request, part_type_id):
    electrolyzers = Electrolyzer.objects.filter(electrolyzer_type_id=part_type_id)
    data = [{
        'id': e.id,
        'number': e.number,
        'launch_date': e.launch_date,
        'failure_date': e.failure_date,
        'days_up': e.days_up,
    } for e in electrolyzers]
    return JsonResponse(data, safe=False)
