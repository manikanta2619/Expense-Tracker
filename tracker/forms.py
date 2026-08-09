from datetime import datetime, date
# pyrefly: ignore [missing-import]
from django import forms
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Category, Expense, MonthlyBudget


ICON_CHOICES = [
    ('bi-house-door-fill', '🏠 Housing / Home'),
    ('bi-cup-hot-fill', '☕ Food & Dining'),
    ('bi-lightning-charge-fill', '⚡ Utilities / Bills'),
    ('bi-controller', '🎮 Entertainment'),
    ('bi-car-front-fill', '🚗 Transportation'),
    ('bi-heart-pulse-fill', '🩺 Healthcare / Medical'),
    ('bi-bag-fill', '🛍️ Shopping / Misc'),
    ('bi-briefcase-fill', '💼 Business / Work'),
    ('bi-book-fill', '📚 Education'),
    ('bi-plane-fill', '✈️ Travel / Vacation'),
    ('bi-gift-fill', '🎁 Gifts / Donations'),
    ('bi-piggy-bank-fill', '🐖 Savings / Investment'),
    ('bi-phone-fill', '📱 Phone & Internet'),
    ('bi-wrench-fill', '🔧 Maintenance / Repairs'),
]


class RegisterForm(UserCreationForm):
    """
    Form for user signup with standard user metadata and Bootstrap styling.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


class ExpenseForm(forms.ModelForm):
    """
    Form for creating and editing expenses. Filters available categories to system defaults + user customs,
    and supports typing a new custom category name directly on the fly.
    """
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=date.today
    )
    new_category_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type a new category name (optional)...',
            'list': 'categoryDatalist'
        })
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grocery Shopping'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add notes or receipt details...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).order_by('name')
        else:
            self.fields['category'].queryset = Category.objects.filter(user__isnull=True)



class CategoryForm(forms.ModelForm):
    """
    Form for creating user-customized expense categories with icon & color pickers.
    """
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fitness & Gym'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color', 'value': '#3b82f6'}),
        }


class MonthlyBudgetForm(forms.ModelForm):
    """
    Form for setting or modifying monthly budget limit.
    """
    month_year_input = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'month'}),
        label='Budget Month'
    )

    class Meta:
        model = MonthlyBudget
        fields = ['monthly_limit']
        widgets = {
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1500.00', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.month_year:
            self.fields['month_year_input'].initial = self.instance.month_year.strftime('%Y-%m')
        else:
            self.fields['month_year_input'].initial = datetime.now().strftime('%Y-%m')

    def clean(self):
        cleaned_data = super().clean()
        month_year_str = cleaned_data.get('month_year_input')
        if month_year_str:
            try:
                parsed_date = datetime.strptime(month_year_str, '%Y-%m').date().replace(day=1)
                self.instance.month_year = parsed_date
            except ValueError:
                self.add_error('month_year_input', 'Invalid month format selected.')
        return cleaned_data


class ExpenseFilterForm(forms.Form):
    """
    Filter form for searching transactions on the dashboard by search query, category, and date range.
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search title or notes...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).order_by('name')
