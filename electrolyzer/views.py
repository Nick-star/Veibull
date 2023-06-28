import math

import numpy as np
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from reliability.Fitters import Fit_Weibull_2P

from .forms import UploadFileForm, BuildingForm, ElectrolyzerTypeForm, ElectrolyzerForm
from .models import Electrolyzer, PartType, Building, Part
from .utils import censor_dates, optimize_curve, weibull_cdf, empirical_cdf


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
    electrolyzers = Electrolyzer.objects.select_related('electrolyzer_type', 'building').all()
    return render(request, 'index.html', {'electrolyzers': electrolyzers})


def chart(request):
    return render(request, 'chart.html')


def get_electrolyzer_types(request):
    electrolyzer_types = PartType.objects.all()
    data = [{'id': et.id, 'name': et.name} for et in electrolyzer_types]
    return JsonResponse(data, safe=False)


def get_buildings(request):
    # TODO
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
                         right_censored=np.array(df[df['running_days'].notnull()]['running_days']),
                         print_results=False,
                         show_probability_plot=False)

    days = (pd.to_datetime(censor_date) - pd.to_datetime(end_search_date)).days
    print(days)
    weibull_curve = weibull_cdf(fit.beta, fit.alpha)
    weibull_curve = optimize_curve(weibull_curve, 0.01)

    empirical_curve = empirical_cdf(np.array(df['days_up'].dropna()), np.array(df['running_days'].dropna()))
    empirical_curve = optimize_curve(empirical_curve, 0.01)

    name = PartType.objects.get(pk=electrolyzer_type_id).name
    count = len(df[df['days_up'].isnull()].index)
    count_failed = len(df[df['days_up'].notnull()].index)
    failed_percent = 1 - math.exp(-math.pow(days / fit.alpha, fit.beta))
    response = {
        'weibull': {
            'name': name + ' рассчитанный',
            'x': list(weibull_curve[:, 0] / 30.4167),
            'y': list(weibull_curve[:, 1] * 100)
        },
        'empirical': {
            'name': name,
            'x': list(empirical_curve[:, 0] / 30.4167),
            'y': list(empirical_curve[:, 1] * 100)
        },
        # TODO
        'building': Building.objects.get(pk=building).name,
        'type': name,
        'date_range': f'{start_search_date} {end_search_date}',
        'working_count': count,
        'failed_count': f'{count * failed_percent:.2f}',
        'censor': censor_date,
        'dates': {
            'date_start': start_search_date,
            'date_end': end_search_date,
            'censor_date': censor_date
        }
    }

    return JsonResponse(response, safe=False)


@login_required
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
