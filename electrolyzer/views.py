import math

import numpy as np
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from reliability.Fitters import Fit_Weibull_2P

from .forms import UploadFileForm, BuildingForm, ElectrolyzerTypeForm, ElectrolyzerForm
from .models import Electrolyzer, PartType, Building, Part, Factory
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


def get_factories(request):
    factories = Factory.objects.all()
    data = [{'id': f.id, 'name': f.name} for f in factories]
    return JsonResponse(data, safe=False)


def get_buildings(request):
    factory_id = request.GET.get('factory_id')
    buildings = Factory.objects.get(id=factory_id).building_set.all()
    data = [{'id': b.id, 'name': b.name} for b in buildings]
    return JsonResponse(data, safe=False)


def get_part_types(request):
    part_types = PartType.objects.all()
    data = [{'id': et.id, 'name': et.name} for et in part_types]
    return JsonResponse(data, safe=False)


def get_oldest_date(request):
    # TODO replace with actual
    return JsonResponse({"date": "2010-01-01"})


def get_electrolyzer_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    forecast_date = request.GET.get('forecast_date')
    part_type = request.GET.get('part_type')
    building = request.GET.get('building')

    values = Part.objects.filter(
        Q(part_type_id=part_type, building_id=building, history__launch_date__range=[start_date, end_date]) & (
                Q(history__failure_date__isnull=True) |
                Q(history__failure_date__range=[start_date, end_date]))).distinct().values("history__launch_date",
                                                                                           "avg_days")

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

    empirical_curve = empirical_cdf(np.array(df['days'].dropna()), np.array(df['running_days'].dropna()))
    empirical_curve = optimize_curve(empirical_curve, 0.01)

    count = len(df[df['days'].isnull()].index)
    failed_percent = 1 - math.exp(-math.pow(days / fit.alpha, fit.beta))
    response = {
        'weibull': {
            'x': list(weibull_curve[:, 0] / 30.4167),
            'y': list(weibull_curve[:, 1] * 100)
        },
        'empirical': {
            'x': list(empirical_curve[:, 0] / 30.4167),
            'y': list(empirical_curve[:, 1] * 100)
        },
        'type': str(PartType.objects.get(id=part_type)),
        'working_count': count,
        'failed_count': f'{count * failed_percent:.2f}',
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
