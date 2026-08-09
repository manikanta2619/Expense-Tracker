from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Housing', 'icon': 'bi-house-door-fill', 'color': '#4e73df'},
    {'name': 'Food', 'icon': 'bi-cup-hot-fill', 'color': '#f6c23e'},
    {'name': 'Utilities', 'icon': 'bi-lightning-charge-fill', 'color': '#36b9cc'},
    {'name': 'Entertainment', 'icon': 'bi-controller', 'color': '#e74a0b'},
    {'name': 'Transportation', 'icon': 'bi-car-front-fill', 'color': '#1cc88a'},
    {'name': 'Healthcare', 'icon': 'bi-heart-pulse-fill', 'color': '#e74a3b'},
    {'name': 'Misc', 'icon': 'bi-bag-fill', 'color': '#858796'},
]

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """
    Automatically create global default categories after database migration.
    """
    if sender.name == 'tracker':
        for cat in DEFAULT_CATEGORIES:
            Category.objects.get_or_create(
                user=None,
                name=cat['name'],
                defaults={
                    'icon': cat['icon'],
                    'color': cat['color']
                }
            )
