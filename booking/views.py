from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, time
import json

from .models import Master, Service, Appointment
from .forms import AppointmentForm


def home(request):
    """Головна сторінка"""
    masters = Master.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    context = {
        'masters': masters,
        'services': services,
    }
    return render(request, 'booking/home.html', context)


def appointment_create(request):
    """Створення нового запису"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()

            # Надсилання підтвердження на email
            if appointment.client_email:
                try:
                    send_mail(
                        subject='Підтвердження запису — Barbershop',
                        message=(
                            f'Привіт, {appointment.client_name}!\n\n'
                            f'Ваш запис підтверджено:\n'
                            f'Майстер: {appointment.master}\n'
                            f'Послуга: {appointment.service.name}\n'
                            f'Дата: {appointment.date}\n'
                            f'Час: {appointment.time}\n\n'
                            f'Чекаємо на вас!'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL
                        if hasattr(settings, 'DEFAULT_FROM_EMAIL')
                        else 'noreply@barbershop.ua',
                        recipient_list=[appointment.client_email],
                        fail_silently=True,
                    )
                except Exception:
                    pass  # Email не критичний

            messages.success(
                request,
                f'✅ Запис успішно створено! Чекаємо вас '
                f'{appointment.date} о {appointment.time}.'
            )
            return redirect('appointment_success', pk=appointment.pk)
    else:
        form = AppointmentForm()

    return render(request, 'booking/appointment_form.html', {'form': form})


def appointment_success(request, pk):
    """Сторінка успішного запису"""
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'booking/appointment_success.html', {
        'appointment': appointment
    })


def master_list(request):
    """Список майстрів"""
    masters = Master.objects.filter(is_active=True)
    return render(request, 'booking/master_list.html', {'masters': masters})


def service_list(request):
    """Список послуг"""
    services = Service.objects.filter(is_active=True)
    return render(request, 'booking/service_list.html', {'services': services})


def schedule(request):
    """Розклад / доступність майстрів"""
    masters = Master.objects.filter(is_active=True)
    selected_master_id = request.GET.get('master')
    selected_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

    appointments = Appointment.objects.filter(
        status__in=['pending', 'confirmed']
    )

    if selected_master_id:
        appointments = appointments.filter(master_id=selected_master_id)
    if selected_date:
        appointments = appointments.filter(date=selected_date)

    # Робочі години: 9:00 — 19:00 з кроком 1 год
    work_hours = [time(h, 0) for h in range(9, 19)]
    booked_times = set(a.time.strftime('%H:%M') for a in appointments)

    context = {
        'masters': masters,
        'selected_master_id': int(selected_master_id) if selected_master_id else None,
        'selected_date': selected_date,
        'work_hours': work_hours,
        'booked_times': booked_times,
    }
    return render(request, 'booking/schedule.html', context)


def get_available_times(request):
    """AJAX: повертає вільні години для майстра на дату"""
    master_id = request.GET.get('master_id')
    date = request.GET.get('date')

    if not master_id or not date:
        return JsonResponse({'times': []})

    booked = Appointment.objects.filter(
        master_id=master_id,
        date=date,
        status__in=['pending', 'confirmed']
    ).values_list('time', flat=True)

    booked_str = set(t.strftime('%H:%M') for t in booked)
    work_hours = [f'{h:02d}:00' for h in range(9, 19)]
    available = [t for t in work_hours if t not in booked_str]

    return JsonResponse({'times': available})


# ---------- Адмін-панель ----------

@staff_member_required
def admin_dashboard(request):
    """Панель адміністратора"""
    appointments = Appointment.objects.select_related('master', 'service').all()

    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
        'total': appointments.count(),
    }
    return render(request, 'booking/admin_dashboard.html', context)


@staff_member_required
def appointment_update_status(request, pk):
    """Зміна статусу запису"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Статус змінено на «{appointment.get_status_display()}»')
    return redirect('admin_dashboard')


@staff_member_required
def appointment_delete(request, pk):
    """Видалення запису"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Запис видалено.')
    return redirect('admin_dashboard')
