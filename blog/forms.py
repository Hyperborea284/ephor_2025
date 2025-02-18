from django import forms
from .models import FlaskInstance

class FlaskInstanceForm(forms.ModelForm):
    class Meta:
        model = FlaskInstance
        fields = ['name']  # Campos editáveis pelo usuário