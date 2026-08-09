import os
# pyrefly: ignore [missing-import]
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from tracker.models import Category, Expense, MonthlyBudget

# 1. Create or get demo user
demo_user, created = User.objects.get_or_create(
    username='demo',
    defaults={
        'email': 'demo@example.com',
        'first_name': 'Alex',
        'last_name': 'Morgan'
    }
)
if created:
    demo_user.set_password('demopassword123')
    demo_user.save()
    print("Created demo user: demo / demopassword123")

# 2. Get default categories
housing = Category.objects.filter(user=None, name='Housing').first()
food = Category.objects.filter(user=None, name='Food').first()
utilities = Category.objects.filter(user=None, name='Utilities').first()
entertainment = Category.objects.filter(user=None, name='Entertainment').first()
transportation = Category.objects.filter(user=None, name='Transportation').first()
healthcare = Category.objects.filter(user=None, name='Healthcare').first()
misc = Category.objects.filter(user=None, name='Misc').first()

# 3. Create Custom Category for demo user
fitness, _ = Category.objects.get_or_create(
    user=demo_user,
    name='Fitness & Gym',
    defaults={'icon': 'bi-heart-pulse-fill', 'color': '#ec4899'}
)

today = date.today()
first_of_month = today.replace(day=1)

# 4. Set monthly budget for demo user
MonthlyBudget.objects.update_or_create(
    user=demo_user,
    month_year=first_of_month,
    defaults={'monthly_limit': Decimal('2500.00')}
)
print("Configured monthly budget of $2,500.00 for demo user.")

# 5. Seed sample expenses for demo user
sample_expenses = [
    {'title': 'Apartment Rent', 'amount': Decimal('1100.00'), 'category': housing, 'days_ago': 2, 'desc': 'Monthly lease payment'},
    {'title': 'Whole Foods Market', 'amount': Decimal('145.50'), 'category': food, 'days_ago': 1, 'desc': 'Groceries & fresh produce'},
    {'title': 'Electricity & Power Bill', 'amount': Decimal('85.20'), 'category': utilities, 'days_ago': 4, 'desc': 'Utility bill for current cycle'},
    {'title': 'Gasoline Refill', 'amount': Decimal('48.00'), 'category': transportation, 'days_ago': 3, 'desc': 'Fuel for car'},
    {'title': 'Cinema & Popcorn', 'amount': Decimal('32.50'), 'category': entertainment, 'days_ago': 5, 'desc': 'Weekend movie night with friends'},
    {'title': 'Pharmacy Prescription', 'amount': Decimal('24.90'), 'category': healthcare, 'days_ago': 6, 'desc': 'Vitamins & prescription refill'},
    {'title': 'Coffee & Bakery', 'amount': Decimal('14.25'), 'category': food, 'days_ago': 0, 'desc': 'Morning espresso and croissant'},
    {'title': 'Gym Membership Renewal', 'amount': Decimal('60.00'), 'category': fitness, 'days_ago': 7, 'desc': 'Monthly fitness club dues'},
    {'title': 'Online Shopping (Amazon)', 'amount': Decimal('89.99'), 'category': misc, 'days_ago': 8, 'desc': 'Home office accessories'},
]

for item in sample_expenses:
    val = item['days_ago']
    days_ago = int(str(val))
    exp_date = today - timedelta(days=days_ago)


    Expense.objects.get_or_create(
        user=demo_user,
        title=item['title'],
        date=exp_date,
        defaults={
            'amount': item['amount'],
            'category': item['category'],
            'description': item['desc']
        }
    )

print("Seeded sample expenses successfully.")
