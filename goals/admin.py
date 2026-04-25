from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'target_amount', 'current_amount', 'is_completed']