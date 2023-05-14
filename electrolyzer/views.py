import pandas as pd
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import Electrolyzer, ElectrolyzerType, Building
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

                if file_extension == 'csv':
                    data = pd.read_csv(file)
                elif file_extension in ['xls', 'xlsx']:
                    data = pd.read_excel(file)
                else:
                    message = "Недоступимый формат файла"

                # Extract data and save Electrolyzer instances
                for index, row in data.iterrows():
                    electrolyzer = Electrolyzer(
                        number=row['№ эл-ра'],
                        launch_date=row['Дата пуска'],
                        failure_date=row['Дата откл.'],
                        days_up=(row['Дата откл.'] - row['Дата пуска']).days,
                        electrolyzer_type=electrolyzer_type,
                        building=building
                    )
                    electrolyzer.save()

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
    electrolyzers = Electrolyzer.objects.all()
    data = serializers.serialize('json', electrolyzers)

    # Extract days_up values
    days_up_values = [e.days_up for e in electrolyzers]

    # Fit the Weibull distribution parameters
    shape, loc, scale = weibull_min.fit(days_up_values, floc=0)

    # Compute the Weibull CDF array
    x_weibull = np.linspace(min(days_up_values), max(days_up_values), 100)
    y_weibull = weibull_min.cdf(x_weibull, shape, loc, scale)

    # Compute the empirical CDF array
    x_empirical = np.sort(days_up_values)
    y_empirical = np.arange(1, len(x_empirical) + 1) / len(x_empirical)

    response = {
        'electrolyzers': data,
        'weibull_cdf': {
            'x': x_weibull.tolist(),
            'y': y_weibull.tolist(),
        },
        'empirical_cdf': {
            'x': x_empirical.tolist(),
            'y': y_empirical.tolist(),
        },
    }

    return JsonResponse(response, safe=False)
