from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Goal
from .forms import GoalForm, ContributeForm


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'goals/list.html', {'goals': goals})


@login_required
def goal_add(request):
    if request.method == 'POST':
        form = GoalForm(request.POST, request.FILES)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, f'🎯 Цель "{goal.title}" создана!')
            return redirect('goal_list')
    else:
        form = GoalForm()

    return render(request, 'goals/add.html', {'form': form})


@login_required
def goal_contribute(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ContributeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            profile = request.user.profile

            if amount > profile.balance:
                messages.error(request, '❌ Недостаточно средств на балансе!')
            else:
                profile.balance -= amount
                profile.save()

                goal.current_amount += amount
                if goal.current_amount >= goal.target_amount:
                    goal.current_amount = goal.target_amount
                    goal.is_completed = True
                    messages.success(request, f'🏆 Поздравляем! Цель "{goal.title}" достигнута!')
                else:
                    messages.success(request, f'✅ Пополнено на {amount} сом!')
                goal.save()

            return redirect('goal_list')
    else:
        form = ContributeForm()

    return render(request, 'goals/contribute.html', {'goal': goal, 'form': form})


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, '🗑️ Цель удалена.')
    return redirect('goal_list')