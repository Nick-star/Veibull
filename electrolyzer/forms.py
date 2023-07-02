from django import forms

from electrolyzer.models import PartType, Part, Factory, Building, Electrolyzer


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Выберите csv, xlsx или json файл')
    part_type = forms.ModelChoiceField(queryset=PartType.objects.all(),
                                       label='Выберите тип электролизёра', empty_label='(Пусто)')
    building = forms.ModelChoiceField(queryset=Building.objects.all(), label='Выберите здание', empty_label='(Пусто)')


class ElectrolyzerForm(forms.ModelForm):
    class Meta:
        # TODO

        model = Electrolyzer
        fields = ['number', 'launch_date', 'failure_date', 'days_up', 'electrolyzer_type', 'building']
        # model = Part
        # fields = ['number', 'launch_date', 'failure_date', 'days_up', 'electrolyzer_type', 'factory_name']
        # fields = ['number']


class BuildingForm(forms.ModelForm):
    factory = forms.ModelChoiceField(
        queryset=Factory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Building
        fields = ['name', 'factory']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ElectrolyzerTypeForm(forms.ModelForm):
    class Meta:
        # TODO

        model = PartType
        fields = ['name']

class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = ['name']
