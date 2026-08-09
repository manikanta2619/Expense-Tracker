from decimal import Decimal
# pyrefly: ignore [missing-import]
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):
    """
    Model representing expense categories.
    `user=None` represents global system default categories available to all users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=50,
        default='bi-tag-fill',
        help_text='Bootstrap icon class name, e.g. bi-house-door-fill'
    )
    color = models.CharField(
        max_length=20,
        default='#4e73df',
        help_text='Hex color code for UI badges and charts'
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_user_category_name'
            )
        ]

    def clean(self):
        super().clean()
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Category name cannot be empty.'})

    def __str__(self):
        if self.user is None:
            return f"{self.name} (Default)"
        return self.name


class Expense(models.Model):
    """
    Model representing individual financial expense transactions logged by a user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def clean(self):
        super().clean()
        if self.amount is not None and self.amount <= Decimal('0.00'):
            raise ValidationError({'amount': 'Expense amount must be greater than zero.'})

    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.date})"


class MonthlyBudget(models.Model):
    """
    Model storing monthly budget limits configured per user per month.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='monthly_budgets'
    )
    monthly_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month_year = models.DateField(
        help_text='First day of the budget month (e.g. 2026-08-01)'
    )

    class Meta:
        ordering = ['-month_year']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'month_year'],
                name='unique_user_monthly_budget'
            )
        ]

    def clean(self):
        super().clean()
        if self.monthly_limit is not None and self.monthly_limit <= Decimal('0.00'):
            raise ValidationError({'monthly_limit': 'Monthly budget limit must be positive.'})

    def __str__(self):
        return f"{self.user.username} - {self.month_year.strftime('%B %Y')}: ${self.monthly_limit}"
