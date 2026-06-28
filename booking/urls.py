from django.urls import path
from . import views

urlpatterns = [
    # Публічні
    path('', views.home, name='home'),
    path('book/', views.appointment_create, name='appointment_create'),
    path('book/success/<int:pk>/', views.appointment_success, name='appointment_success'),
    path('masters/', views.master_list, name='master_list'),
    path('services/', views.service_list, name='service_list'),
    path('schedule/', views.schedule, name='schedule'),
    path('api/available-times/', views.get_available_times, name='available_times'),

    # Аутентифікація
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Панель майстра
    path('my-appointments/', views.master_dashboard, name='master_dashboard'),

    # Адмін-панель
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/appointment/<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
    path('dashboard/appointment/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
]
