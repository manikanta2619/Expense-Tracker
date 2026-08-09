import json
from decimal import Decimal
from datetime import datetime, date
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db import IntegrityError


from .models import Category, Expense, MonthlyBudget
from .forms import (
    RegisterForm,
    ExpenseForm,
    CategoryForm,
    MonthlyBudgetForm,
    ExpenseFilterForm,
)


def register_view(request):
    """
    View to register a new user and automatically log them in upon successful registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to Expense Tracker, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'tracker/register.html', {'form': form})


def login_view(request):
    """
    View for user authentication and login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request) -> HttpResponse:
    """
    View to log out current user session.
    """
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')




@login_required
def dashboard_view(request):
    """
    Main Dashboard View:
    - User-isolated spending summary card
    - Monthly budget limit indicator with percentage progress bar
    - Expenditure breakdown grouped by category using Django aggregation
    - Filterable transaction history by category, date range, search query
    """
    user = request.user
    today = date.today()
    current_year = today.year
    current_month = today.month

    # Initialize filter form
    filter_form = ExpenseFilterForm(request.GET, user=user)
    
    # Base user expenses queryset
    user_expenses = Expense.objects.filter(user=user).select_related('category')
    filtered_expenses = user_expenses

    # Apply search filters if valid
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if search_query:
        filtered_expenses = filtered_expenses.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    if category_id:
        filtered_expenses = filtered_expenses.filter(category_id=category_id)
    if start_date:
        filtered_expenses = filtered_expenses.filter(date__gte=start_date)
    if end_date:
        filtered_expenses = filtered_expenses.filter(date__lte=end_date)

    # 1. Spending Aggregations
    total_filtered_spent = filtered_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Current month spending calculation
    current_month_expenses = user_expenses.filter(date__year=current_year, date__month=current_month)
    current_month_spent = current_month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # 2. Monthly Budget Progress
    first_of_month = date(current_year, current_month, 1)
    monthly_budget = MonthlyBudget.objects.filter(user=user, month_year=first_of_month).first()

    budget_limit = monthly_budget.monthly_limit if monthly_budget else None
    budget_percentage = 0
    budget_remaining = Decimal('0.00')
    is_over_budget = False

    if budget_limit and budget_limit > Decimal('0.00'):
        raw_pct = (current_month_spent / budget_limit) * Decimal('100')
        budget_percentage = min(float(raw_pct), 100.0)
        budget_remaining = budget_limit - current_month_spent
        if budget_remaining < Decimal('0.00'):
            is_over_budget = True

    # 3. Category Breakdown via Django Aggregation & Annotation
    category_breakdown = filtered_expenses.values(
        'category__id', 'category__name', 'category__icon', 'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Build chart data structures
    chart_labels = []
    chart_data = []
    chart_colors = []

    for item in category_breakdown:
        cat_name = item['category__name'] or 'Uncategorized'
        chart_labels.append(cat_name)
        chart_data.append(float(item['total']))
        chart_colors.append(item['category__color'] or '#6c757d')

    chart_payload = {
        'labels': chart_labels,
        'data': chart_data,
        'colors': chart_colors
    }

    # Forms for quick modal actions
    budget_form = MonthlyBudgetForm(initial={'monthly_limit': budget_limit or 1000.00, 'month_year_input': first_of_month.strftime('%Y-%m')})
    category_form = CategoryForm()

    context = {
        'filtered_expenses': filtered_expenses[:50],  # Latest 50 transactions
        'total_filtered_spent': total_filtered_spent,
        'transaction_count': filtered_expenses.count(),
        'current_month_spent': current_month_spent,
        'current_month_name': today.strftime('%B %Y'),
        'monthly_budget': monthly_budget,
        'budget_limit': budget_limit,
        'budget_percentage': round(budget_percentage, 1),
        'budget_remaining': budget_remaining,
        'is_over_budget': is_over_budget,
        'category_breakdown': category_breakdown,
        'chart_payload_json': json.dumps(chart_payload),
        'filter_form': filter_form,
        'budget_form': budget_form,
        'category_form': category_form,
        'is_filtered': bool(search_query or category_id or start_date or end_date),
    }

    return render(request, 'tracker/dashboard.html', context)


@login_required
def expense_create_view(request):
    """
    View to create a new expense entry. Supports selecting an existing category or typing a new custom category on the fly.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user

            new_cat_name = form.cleaned_data.get('new_category_name', '').strip()
            if new_cat_name:
                cat_obj, _ = Category.objects.get_or_create(
                    user=request.user,
                    name=new_cat_name,
                    defaults={'icon': 'bi-tag-fill', 'color': '#3b82f6'}
                )
                expense.category = cat_obj

            expense.save()
            messages.success(request, f"Expense '{expense.title}' of ${expense.amount} recorded successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to record expense. Please fix errors below.")
    else:
        form = ExpenseForm(user=request.user)

    return render(request, 'tracker/expense_form.html', {'form': form, 'title': 'Add New Expense'})


@login_required
def expense_update_view(request, pk):
    """
    View to update an existing expense entry (isolated to request.user). Supports typing a new category.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            updated_expense = form.save(commit=False)

            new_cat_name = form.cleaned_data.get('new_category_name', '').strip()
            if new_cat_name:
                cat_obj, _ = Category.objects.get_or_create(
                    user=request.user,
                    name=new_cat_name,
                    defaults={'icon': 'bi-tag-fill', 'color': '#3b82f6'}
                )
                updated_expense.category = cat_obj

            updated_expense.save()
            messages.success(request, f"Expense '{updated_expense.title}' updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update expense. Please check input.")
    else:
        form = ExpenseForm(instance=expense, user=request.user)

    return render(request, 'tracker/expense_form.html', {'form': form, 'title': f"Edit Expense: {expense.title}", 'expense': expense})



@login_required
def expense_delete_view(request, pk):
    """
    View to delete an existing expense (isolated to request.user).
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f"Expense '{title}' deleted successfully.")
        return redirect('dashboard')

    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})


@login_required
def category_list_create_view(request):
    """
    View to list categories (defaults + user custom) and create a custom user category.
    """
    user = request.user
    custom_categories = Category.objects.filter(user=user)
    default_categories = Category.objects.filter(user__isnull=True)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = user
            try:
                category.save()
                messages.success(request, f"Category '{category.name}' created successfully!")
                return redirect('category_list')
            except IntegrityError:
                messages.error(request, f"A category named '{category.name}' already exists.")
        else:
            messages.error(request, "Could not create category. Please check errors.")
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'custom_categories': custom_categories,
        'default_categories': default_categories,
    }
    return render(request, 'tracker/category_list.html', context)


@login_required
def category_delete_view(request, pk):
    """
    View to delete a custom user category. Default system categories cannot be deleted.
    """
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Custom category '{name}' deleted.")
        return redirect('category_list')

    return redirect('category_list')


@login_required
def budget_set_view(request):
    """
    View to set or update monthly budget for a selected month.
    """
    if request.method == 'POST':
        form = MonthlyBudgetForm(request.POST)
        if form.is_valid():
            month_year = form.instance.month_year
            monthly_limit = form.cleaned_data['monthly_limit']

            budget, created = MonthlyBudget.objects.update_or_create(
                user=request.user,
                month_year=month_year,
                defaults={'monthly_limit': monthly_limit}
            )

            action_text = "created" if created else "updated"
            messages.success(request, f"Monthly budget for {month_year.strftime('%B %Y')} {action_text} to ${monthly_limit:.2f}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to save monthly budget limit. Check form inputs.")

    return redirect('dashboard')
