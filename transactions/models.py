from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('base', '🏠 База'),
        ('wants', '✨ Хотелки'),
        ('invest', '📈 Инвестиции'),
    ]
    TYPE_CHOICES = [
        ('income', 'Доход'),
        ('expense', 'Расход'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200, verbose_name='Название')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name='Категория')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Тип')
    note = models.TextField(blank=True, null=True, verbose_name='Заметка')
    created_at = models.DateTimeField(auto_now_add=True)
    is_pending = models.BooleanField(default=False, verbose_name='Ожидает 24ч')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.amount}'