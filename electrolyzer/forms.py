from django import forms

from electrolyzer.models import ElectrolyzerType, Building


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Выбери .csv или .xlsx файл')
    electrolyzer_type = forms.ModelChoiceField(queryset=ElectrolyzerType.objects.all(),
                                               label='Выбери тип электролизёра')
    building = forms.ModelChoiceField(queryset=Building.objects.all(), label='Выбери здание')


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name']


class ElectrolyzerTypeForm(forms.ModelForm):
    class Meta:
        model = ElectrolyzerType
        fields = ['name']
