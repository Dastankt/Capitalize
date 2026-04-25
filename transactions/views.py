from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Transaction
from .forms import TransactionForm

# Порог суммы для правила 24 часов (в сомах)
PENDING_THRESHOLD = 500


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user, is_pending=False)
    pending = Transaction.objects.filter(user=request.user, is_pending=True)

    # Фильтрация
    category = request.GET.get('category', '')
    tx_type = request.GET.get('type', '')

    if category:
        transactions = transactions.filter(category=category)
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)

    stats = {
        'base': sum(t.amount for t in Transaction.objects.filter(user=request.user, is_pending=False, category='base', transaction_type='expense')),
        'wants': sum(t.amount for t in Transaction.objects.filter(user=request.user, is_pending=False, category='wants', transaction_type='expense')),
        'invest': sum(t.amount for t in Transaction.objects.filter(user=request.user, is_pending=False, category='invest', transaction_type='expense')),
    }

    context = {
        'transactions': transactions,
        'pending': pending,
        'stats': stats,
        'current_category': category,
        'current_type': tx_type,
    }
    return render(request, 'transactions/list.html', context)


@login_required
def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user

            # Правило 24 часов: крупные расходы уходят на ожидание
            if (transaction.transaction_type == 'expense' and
                    transaction.amount >= PENDING_THRESHOLD and
                    transaction.category == 'wants'):
                transaction.is_pending = True
                transaction.save()
                messages.warning(
                    request,
                    f'⏳ Трата "{transaction.title}" на {transaction.amount} сом '
                    f'отложена на 24 часа. Подтверди завтра!'
                )
            else:
                # Обычная транзакция — сразу списываем
                profile = request.user.profile
                if transaction.transaction_type == 'income':
                    profile.balance += transaction.amount
                else:
                    profile.balance -= transaction.amount
                profile.save()
                transaction.save()
                messages.success(request, f'✅ Транзакция "{transaction.title}" добавлена!')

            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'transactions/add.html', {'form': form})


@login_required
def transaction_confirm(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)

    if not transaction.is_pending:
        messages.error(request, 'Эта транзакция уже подтверждена.')
        return redirect('transaction_list')

    # Проверяем: прошло ли 24 часа?
    time_passed = timezone.now() - transaction.created_at
    hours_passed = time_passed.total_seconds() / 3600

    if hours_passed < 24:
        hours_left = int(24 - hours_passed)
        minutes_left = int((24 - hours_passed) * 60 % 60)
        messages.error(
            request,
            f'⏳ Ещё рано! Осталось подождать {hours_left}ч {minutes_left}мин.'
        )
        return redirect('transaction_list')

    # 24 часа прошло — подтверждаем
    profile = request.user.profile
    profile.balance -= transaction.amount
    profile.save()

    transaction.is_pending = False
    transaction.save()
    messages.success(request, f'✅ Покупка "{transaction.title}" подтверждена и списана!')
    return redirect('transaction_list')


@login_required
def transaction_cancel(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)

    if transaction.is_pending:
        transaction.delete()
        messages.success(request, f'🚫 Покупка отменена. Хорошее решение!')
    return redirect('transaction_list')


@login_required
def transaction_delete(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)

    if not transaction.is_pending:
        profile = request.user.profile
        if transaction.transaction_type == 'income':
            profile.balance -= transaction.amount
        else:
            profile.balance += transaction.amount
        profile.save()

    transaction.delete()
    messages.success(request, '🗑️ Транзакция удалена.')
    return redirect('transaction_list')