import pandas as pd
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import Electrolyzer
from django.core import serializers


def upload_file(request):
    message = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                file = request.FILES['file']
                file_extension = file.name.split('.')[-1]

                if file_extension == 'csv':
                    data = pd.read_csv(file)
                elif file_extension in ['xls', 'xlsx']:
                    data = pd.read_excel(file)
                else:
                    message = f"Недоступимый формат файла"

                # Extract data and save Electrolyzer instances
                for index, row in data.iterrows():
                    electrolyzer = Electrolyzer(
                        electrolyzer_number=row['№ electrolyzer'],
                        release_date=row['Release date'],
                        shutdown_date=row['Shutdown date'],
                        shutdown_life=row['Shutdown life'],
                        average_lifetime=row['Average lifetime']
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
    return JsonResponse(data, safe=False)
