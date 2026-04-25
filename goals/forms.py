from django import forms
from .models import Goal


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'target_amount', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Видеокарта RTX 4070'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Зачем тебе это? (необязательно)'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '1',
                'step': '0.01'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Название цели',
            'description': 'Описание',
            'target_amount': 'Нужная сумма (сом)',
            'image': 'Картинка (необязательно)',
        }


class ContributeForm(forms.Form):
    amount = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        label='Пополнить на (сом)'
    )