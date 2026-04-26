from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .forms import RegisterForm, ProfileEditForm, UserEditForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    from transactions.models import Transaction
    from goals.models import Goal
    from django.utils import timezone
    from datetime import timedelta
    import json

    transactions = Transaction.objects.filter(
        user=request.user, is_pending=False
    ).order_by('-created_at')[:5]

    pending = Transaction.objects.filter(
        user=request.user, is_pending=True
    )

    goals = Goal.objects.filter(
        user=request.user, is_completed=False
    )[:3]

    all_transactions = Transaction.objects.filter(
        user=request.user, is_pending=False
    )

    total_income = sum(t.amount for t in all_transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in all_transactions if t.transaction_type == 'expense')

    # Статистика по категориям
    expenses = [t for t in all_transactions if t.transaction_type == 'expense']
    stats = {
        'base': sum(t.amount for t in expenses if t.category == 'base'),
        'wants': sum(t.amount for t in expenses if t.category == 'wants'),
        'invest': sum(t.amount for t in expenses if t.category == 'invest'),
    }
    stats['total'] = stats['base'] + stats['wants'] + stats['invest'] or 1

    # Данные для графика — расходы за 7 дней
    today = timezone.now().date()
    labels = []
    values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = sum(
            t.amount for t in all_transactions
            if t.transaction_type == 'expense' and t.created_at.date() == day
        )
        labels.append(day.strftime('%d.%m'))
        values.append(float(day_total))

    chart_data = json.dumps({'labels': labels, 'values': values})

    context = {
        'transactions': transactions,
        'pending': pending,
        'goals': goals,
        'total_income': total_income,
        'total_expense': total_expense,
        'stats': stats,
        'chart_data': chart_data,
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def profile_view(request):
    from transactions.models import Transaction
    from goals.models import Goal

    # Статистика пользователя
    all_transactions = Transaction.objects.filter(
        user=request.user, is_pending=False
    )
    total_income = sum(t.amount for t in all_transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in all_transactions if t.transaction_type == 'expense')
    total_transactions = all_transactions.count()
    total_goals = Goal.objects.filter(user=request.user).count()
    completed_goals = Goal.objects.filter(user=request.user, is_completed=True).count()

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_transactions': total_transactions,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '✅ Профиль успешно обновлён!')
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def report_view(request):
    from transactions.models import Transaction
    from django.utils import timezone
    import json

    # Текущий месяц по умолчанию
    now = timezone.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    # Все транзакции за выбранный месяц
    transactions = Transaction.objects.filter(
        user=request.user,
        is_pending=False,
        created_at__month=month,
        created_at__year=year,
    )

    income_list = [t for t in transactions if t.transaction_type == 'income']
    expense_list = [t for t in transactions if t.transaction_type == 'expense']

    total_income = sum(t.amount for t in income_list)
    total_expense = sum(t.amount for t in expense_list)
    net = total_income - total_expense

    # Статистика по категориям
    stats = {
        'base': sum(t.amount for t in expense_list if t.category == 'base'),
        'wants': sum(t.amount for t in expense_list if t.category == 'wants'),
        'invest': sum(t.amount for t in expense_list if t.category == 'invest'),
    }
    stats['total'] = stats['base'] + stats['wants'] + stats['invest'] or 1

    # График расходов по дням месяца
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    daily_labels = [str(d) for d in range(1, days_in_month + 1)]
    daily_expenses = []
    daily_incomes = []

    for day in range(1, days_in_month + 1):
        day_expense = sum(
            t.amount for t in expense_list
            if t.created_at.day == day
        )
        day_income = sum(
            t.amount for t in income_list
            if t.created_at.day == day
        )
        daily_expenses.append(float(day_expense))
        daily_incomes.append(float(day_income))

    chart_data = json.dumps({
        'labels': daily_labels,
        'expenses': daily_expenses,
        'incomes': daily_incomes,
    })

    # Список месяцев для селектора
    months = [
        (1, 'Январь'), (2, 'Февраль'), (3, 'Март'),
        (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'),
        (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'),
        (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь'),
    ]

    context = {
        'transactions': transactions.order_by('-created_at'),
        'total_income': total_income,
        'total_expense': total_expense,
        'net': net,
        'stats': stats,
        'chart_data': chart_data,
        'months': months,
        'current_month': month,
        'current_year': year,
        'month_name': months[month - 1][1],
        'years': [2024, 2025, 2026],
    }
    return render(request, 'users/report.html', context)