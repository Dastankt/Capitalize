from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'amount', 'category', 'transaction_type', 'is_pending', 'created_at']
    list_filter = ['category', 'transaction_type', 'is_pending']