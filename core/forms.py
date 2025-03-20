from django import forms
from .models import TreeType, PlantingSite, TreeServiceProvider

class TreeSelectionForm(forms.Form):
    """Форма для выбора вида дерева"""
    tree_type = forms.ModelChoiceField(
        queryset=TreeType.objects.all(),
        empty_label="Выберите вид дерева",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class PlantingSiteForm(forms.ModelForm):
    """Форма для добавления участка для посадки"""
    class Meta:
        model = PlantingSite
        fields = ['site_type', 'image', 'location']
        widgets = {
            'site_type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите адрес или координаты'})
        }

class TreePriceForm(forms.Form):
    """Форма для установки цены дерева"""
    price = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите цену'
        })
    )

class TreeQuantityForm(forms.Form):
    """Форма для установки количества деревьев"""
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите количество'
        })
    )

class ServiceProviderForm(forms.ModelForm):
    """Форма для добавления услуг по продаже и посадке деревьев"""
    class Meta:
        model = TreeServiceProvider
        fields = ['name', 'description', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название услуги'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание ваших услуг'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Контактный телефон'})
        }