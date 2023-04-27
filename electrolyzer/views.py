import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import Electrolyzer


def upload_file(request):
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
                    return JsonResponse({'error': 'Invalid file format'})

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

                return JsonResponse({'message': 'Data imported successfully'})
        except Exception as e:
            return JsonResponse({'error': f"An error occurred while processing the file: {str(e)}"})

    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form})


def index(request):
    return render(request, 'index.html')
