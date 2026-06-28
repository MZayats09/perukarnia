from django.contrib import admin
from .models import Master, Service, Appointment


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user', 'specialization', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['first_name', 'last_name', 'email']
    list_editable = ['is_active']
    # Поле user прив'язує акаунт до майстра
    raw_id_fields = ['user']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['price', 'is_active']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_phone', 'master', 'service', 'date', 'time', 'status']
    list_filter = ['status', 'date', 'master']
    search_fields = ['client_name', 'client_phone', 'client_email']
    list_editable = ['status']
    date_hierarchy = 'date'
    ordering = ['-date', 'time']
    readonly_fields = ['created_at']
