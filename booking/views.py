from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time

from .models import Master, Service, Appointment
from .forms import AppointmentForm


# ── Публічні сторінки ─────────────────────────────────────────────────────────

def home(request):
    masters = Master.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    return render(request, 'booking/home.html', {
        'masters': masters,
        'services': services,
    })


def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
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
                            f'Час: {appointment.time}\n\nЧекаємо на вас!'
                        ),
                        from_email='noreply@barbershop.ua',
                        recipient_list=[appointment.client_email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            messages.success(
                request,
                f'✅ Запис успішно створено! Чекаємо вас {appointment.date} о {appointment.time}.'
            )
            return redirect('appointment_success', pk=appointment.pk)
    else:
        form = AppointmentForm()
    return render(request, 'booking/appointment_form.html', {'form': form})


def appointment_success(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'booking/appointment_success.html', {'appointment': appointment})


def master_list(request):
    masters = Master.objects.filter(is_active=True)
    return render(request, 'booking/master_list.html', {'masters': masters})


def service_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'booking/service_list.html', {'services': services})


def schedule(request):
    masters = Master.objects.filter(is_active=True)
    selected_master_id = request.GET.get('master')
    selected_date = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))

    appointments = Appointment.objects.filter(status__in=['pending', 'confirmed'])
    if selected_master_id:
        appointments = appointments.filter(master_id=selected_master_id)
    if selected_date:
        appointments = appointments.filter(date=selected_date)

    work_hours = [time(h, 0) for h in range(9, 19)]
    booked_times = set(a.time.strftime('%H:%M') for a in appointments)

    return render(request, 'booking/schedule.html', {
        'masters': masters,
        'selected_master_id': int(selected_master_id) if selected_master_id else None,
        'selected_date': selected_date,
        'work_hours': work_hours,
        'booked_times': booked_times,
    })


def get_available_times(request):
    master_id = request.GET.get('master_id')
    date = request.GET.get('date')
    if not master_id or not date:
        return JsonResponse({'times': []})

    booked = Appointment.objects.filter(
        master_id=master_id, date=date,
        status__in=['pending', 'confirmed']
    ).values_list('time', flat=True)

    booked_str = set(t.strftime('%H:%M') for t in booked)
    work_hours = [f'{h:02d}:00' for h in range(9, 19)]
    available = [t for t in work_hours if t not in booked_str]
    return JsonResponse({'times': available})


# ── Аутентифікація ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return _redirect_after_login(user)
        else:
            # Повертаємо форму з помилкою
            from django.contrib.auth.forms import AuthenticationForm
            form = AuthenticationForm(data=request.POST)
            form.is_valid()  # щоб заповнити errors
            return render(request, 'booking/login.html', {'form': form})

    return render(request, 'booking/login.html', {'form': None})


def _redirect_after_login(user):
    """Перенаправлення після входу залежно від ролі"""
    if user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('master_dashboard')


def logout_view(request):
    logout(request)
    messages.success(request, 'Ви успішно вийшли з системи.')
    return redirect('home')


# ── Панель майстра ────────────────────────────────────────────────────────────

@login_required(login_url='login')
def master_dashboard(request):
    # Перевірка чи є прив'язаний профіль майстра
    try:
        master = Master.objects.get(user=request.user)
    except Master.DoesNotExist:
        return render(request, 'booking/no_master_profile.html')

    appointments = Appointment.objects.filter(master=master).select_related('service')

    # Фільтри
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(date=date_filter)

    today = timezone.now().date()
    all_appointments = Appointment.objects.filter(master=master)

    stats = {
        'pending': all_appointments.filter(status='pending').count(),
        'confirmed': all_appointments.filter(status='confirmed').count(),
        'today': all_appointments.filter(date=today, status__in=['pending', 'confirmed']).count(),
        'total': all_appointments.count(),
    }

    return render(request, 'booking/master_dashboard.html', {
        'master': master,
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES,
        'stats': stats,
    })


# ── Адмін-панель ──────────────────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    appointments = Appointment.objects.select_related('master', 'service').all()

    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'booking/admin_dashboard.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
        'total': appointments.count(),
        'masters': Master.objects.filter(is_active=True),
    })


@staff_member_required
def appointment_update_status(request, pk):
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
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Запис видалено.')
    return redirect('admin_dashboard')
