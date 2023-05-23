import math

import numpy as np
import pandas as pd
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from reliability.Fitters import Fit_Weibull_2P

from .forms import UploadFileForm, BuildingForm, ElectrolyzerTypeForm, ElectrolyzerForm
from .models import Electrolyzer, ElectrolyzerType, Building
from .utils import censor_dates, optimize_curve, weibull_cdf, cumulative_function_y


def edit_electrolyzer(request, electrolyzer_id):
    electrolyzer = get_object_or_404(Electrolyzer, id=electrolyzer_id)

    if request.method == 'POST':
        form = ElectrolyzerForm(request.POST, instance=electrolyzer)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ElectrolyzerForm(instance=electrolyzer)

    electrolyzer_types = ElectrolyzerType.objects.all()
    buildings = Building.objects.all()

    context = {
        'form': form,
        'electrolyzer': electrolyzer,
        'buildings': buildings,
        'electrolyzer_types': electrolyzer_types,
    }
    return render(request, 'edit_electrolyzer.html', context)


def upload_file(request):
    message = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                file = request.FILES['file']
                file_extension = file.name.split('.')[-1]

                electrolyzer_type = form.cleaned_data['electrolyzer_type']
                building = form.cleaned_data['building']

                important_cols = ['№ эл-ра', 'Дата пуска', 'Дата откл.']
                if file_extension == 'csv':
                    data = pd.read_csv(file, usecols=important_cols)
                elif file_extension in ['xls', 'xlsx']:
                    data = pd.read_excel(file, usecols=important_cols)
                else:
                    raise ValueError("Недопустимый формат файла")

                data.columns = ['id', 'launch_date', 'failure_date']
                data.loc[data['failure_date'].notnull(), 'days_up'] = (
                        data['failure_date'] - data['launch_date']).dt.days
                Electrolyzer.objects.all().delete()
                els_to_create = []
                for row in data.itertuples(index=False):
                    failure_date, days_up = row[2], row[3]
                    if math.isnan(days_up):
                        failure_date, days_up = None, None
                    els_to_create.append(Electrolyzer(
                        number=row[0],
                        launch_date=row[1],
                        failure_date=failure_date,
                        days_up=days_up,
                        electrolyzer_type=electrolyzer_type,
                        building=building
                    ))

                print(f'Created {len(els_to_create)} electrolyzers.')
                Electrolyzer.objects.bulk_create(els_to_create)

                return redirect('chart')
        except Exception as e:
            message = f"Ошибка во время обработки файла: {str(e)}"

    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form, 'message': message})


def index(request):
    electrolyzers = Electrolyzer.objects.select_related('electrolyzer_type', 'building').all()
    return render(request, 'index.html', {'electrolyzers': electrolyzers})


def chart(request):
    return render(request, 'chart.html')


def get_electrolyzer_types(request):
    electrolyzer_types = ElectrolyzerType.objects.all()
    data = [{'id': et.id, 'name': et.name} for et in electrolyzer_types]
    return JsonResponse(data, safe=False)


def get_buildings(request):
    building = Building.objects.all()
    data = [{'id': b.id, 'name': b.name} for b in building]
    return JsonResponse(data, safe=False)


def get_electrolyzer_data(request):
    start_search_date = request.GET.get('start_date')
    end_search_date = request.GET.get('end_date')
    censor_date = request.GET.get('forecast_date')
    electrolyzer_type_id = request.GET.get('electrolyzer_type')
    building = request.GET.get('building')

    value_list = ["launch_date", "failure_date", "days_up"]
    values = Electrolyzer.objects.filter(
        Q(electrolyzer_type=electrolyzer_type_id) & Q(building=building) & Q(
            launch_date__range=[start_search_date, end_search_date])
    ).values(*value_list)

    df = pd.DataFrame.from_records(values)
    df = censor_dates(df, censor_date)

    fit = Fit_Weibull_2P(failures=np.array(df[df['days_up'].notnull()]['days_up']),
                         print_results=False,
                         show_probability_plot=False)

    days = (pd.to_datetime(censor_date) - pd.to_datetime(end_search_date)).days * 1.5
    x, y = weibull_cdf(fit.beta, fit.alpha)
    x, y = optimize_curve(x, y, 0.01)
    y *= 100

    x_2 = np.array(df['days_up'].dropna())

    # x_2_cut = x_2[x_2 <= ]
    y_2 = cumulative_function_y(x_2, len(x_2)) * 100
    x_2, y_2 = optimize_curve(x_2, y_2, 0.01)

    name = ElectrolyzerType.objects.get(pk=electrolyzer_type_id).name
    count = len(df[df['days_up'].isnull()])
    failed_percent = 1 - np.exp(-np.power(days / fit.alpha, fit.beta))
    response = {
        'weibull': {
            'name': name + ' рассчитанный',
            'x': list(x / 30.4167),
            'y': list(y)
        },
        'empirical': {
            'name': name,
            'x': list(x_2 / 30.4167),
            'y': list(y_2)
        },
        'building': Building.objects.get(pk=building).name,
        'type': name,
        'working_count': count,
        'failed_count': f'{count * float(failed_percent):.2f}',
        'dates': {
            'date_start': start_search_date,
            'date_end': end_search_date,
            'censor_date': censor_date
        }
    }

    return JsonResponse(response, safe=False)


def tb_add(request):
    building_form = BuildingForm()
    electrolyzer_type_form = ElectrolyzerTypeForm()
    return render(request, 'tb_add.html',
                  {'building_form': building_form, 'electrolyzer_type_form': electrolyzer_type_form})


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
