from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('expenses/add/', views.expense_create_view, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_update_view, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete_view, name='expense_delete'),
    path('categories/', views.category_list_create_view, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    path('budget/set/', views.budget_set_view, name='budget_set'),
]
