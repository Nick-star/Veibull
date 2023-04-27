from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Выбери .csv или .xlsx файл')
