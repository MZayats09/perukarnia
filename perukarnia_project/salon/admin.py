from django.contrib import admin
from .models import Master, Client, Order

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone') # Що ми бачимо у списку
    search_fields = ('full_name',)        # Пошук за ім'ям

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone')
    search_fields = ('full_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('service', 'visit_date', 'master', 'client', 'price')
    list_filter = ('visit_date', 'master') # Фільтри збоку