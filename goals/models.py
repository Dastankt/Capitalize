from django.db import models
from django.contrib.auth.models import User


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200, verbose_name='Название цели')
    description = models.TextField(blank=True, verbose_name='Описание')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма цели')
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Накоплено')
    image = models.ImageField(upload_to='goals/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.current_amount}/{self.target_amount}'

    @property
    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return int((self.current_amount / self.target_amount) * 100)