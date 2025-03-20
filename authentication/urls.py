from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    # Заменяем стандартный выход на наш кастомный logout_view
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]