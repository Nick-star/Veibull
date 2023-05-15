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
    electrolyzer_types = ElectrolyzerType.objects.all()

    electrolyzers_data = serializers.serialize('json', electrolyzers)
    electrolyzer_types_data = [{'id': et.id, 'name': et.name} for et in electrolyzer_types]

    response = {
        'electrolyzers': electrolyzers_data,
        'electrolyzer_types': electrolyzer_types_data,
    }

    return JsonResponse(response, safe=False)


