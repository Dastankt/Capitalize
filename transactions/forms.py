from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'category', 'transaction_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Кофе, Зарплата...'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Название',
            'amount': 'Сумма (сом)',
            'category': 'Категория',
            'transaction_type': 'Тип',
        }