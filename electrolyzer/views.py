import math

import pandas as pd
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import Electrolyzer, ElectrolyzerType, Building
from .utils import censor_dates, optimize_curve, weibull_cdf, cumulative_function_y
from reliability.Fitters import Fit_Weibull_2P
from django.core import serializers
from scipy.optimize import curve_fit
from scipy.stats import weibull_min


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
    return render(request, 'index.html')


def chart(request):
    return render(request, 'chart.html')


def get_electrolyzer_data(request):
    # electrolyzers = Electrolyzer.objects.all()
    # electrolyzer_types = ElectrolyzerType.objects.all()
    start_search_date, end_search_date = '2012-08-20', '2019-10-10'
    censor_date = '2019-12-10'

    obeme = ElectrolyzerType.objects.first()
    date__range = [start_search_date, end_search_date]
    value_list = ["launch_date", "failure_date", "days_up"]
    values = obeme.electrolyzer_set.filter(launch_date__range=date__range).values(*value_list)
    df = pd.DataFrame.from_records(values)
    df = censor_dates(df, censor_date)
    print(df)

    fit = Fit_Weibull_2P(failures=np.array(df[df['days_up'].notnull()]['days_up']),
                         right_censored=np.array(df[df['running_days'].notnull()]['running_days']), print_results=False,
                         show_probability_plot=False)

    x, y = weibull_cdf(fit.beta, fit.alpha)
    x, y = optimize_curve(x, y, 0.01)
    y *= 100

    x_2 = np.array(df['days_up'].dropna())
    y_2 = cumulative_function_y(x_2) * 100
    x_2, y_2 = optimize_curve(x_2, y_2, 0.01)

    # ax = plt.gca()
    # plt.plot(x, y * 100)
    # plt.plot(x_2, y_2)

    # electrolyzers_data = serializers.serialize('json', electrolyzers)
    # electrolyzer_types_data = [{'id': et.id, 'name': et.name} for et in electrolyzer_types]

    response = {
        'weibull': {
            'x': list(x),
            'y': list(y)
        },
        'empirical': {
            'x': list(x_2),
            'y': list(y_2)
        }
        # 'electrolyzers': electrolyzers_data,
        # 'electrolyzer_types': electrolyzer_types_data,
    }

    return JsonResponse(response, safe=False)
