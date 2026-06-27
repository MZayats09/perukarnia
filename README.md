# ✂ BarberShop — Система запису

Django-проект для онлайн-запису в перукарню (барбершоп).

## Структура проекту

```
barbershop/
├── barbershop/          # Налаштування Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── booking/             # Основний застосунок
│   ├── models.py        # Master, Service, Appointment
│   ├── views.py         # Всі представлення
│   ├── forms.py         # Форма запису
│   ├── urls.py          # URL-маршрути
│   ├── admin.py         # Django Admin
│   └── templates/booking/
│       ├── home.html
│       ├── appointment_form.html
│       ├── appointment_success.html
│       ├── master_list.html
│       ├── service_list.html
│       ├── schedule.html
│       └── admin_dashboard.html
├── templates/
│   └── base.html        # Базовий шаблон
├── manage.py
└── requirements.txt
```

## Моделі

- **Master** — майстер (ім'я, фото, спеціалізація, контакти)
- **Service** — послуга (назва, опис, ціна, тривалість)
- **Appointment** — запис клієнта (клієнт + майстер + послуга + дата/час + статус)

## Швидкий старт

### 1. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 2. Міграції бази даних
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Створення суперкористувача (адміністратора)
```bash
python manage.py createsuperuser
```

### 4. Заповнення тестовими даними (опційно)
```bash
python manage.py shell
```
```python
from booking.models import Master, Service

Master.objects.create(first_name='Олексій', last_name='Коваль', specialization='Чоловічі стрижки, борода', phone='+38 099 111-11-11')
Master.objects.create(first_name='Дмитро', last_name='Шевченко', specialization='Класичні стрижки, укладка', phone='+38 099 222-22-22')

Service.objects.create(name='Чоловіча стрижка', price=250, duration=45, description='Класична або сучасна стрижка')
Service.objects.create(name='Стрижка бороди', price=150, duration=30, description='Моделювання та догляд за бородою')
Service.objects.create(name='Комплекс (стрижка + борода)', price=350, duration=70, description='Стрижка та борода разом')
```

### 5. Запуск сервера
```bash
python manage.py runserver
```

## Сторінки

| URL | Опис |
|-----|------|
| `/` | Головна сторінка |
| `/book/` | Форма запису |
| `/masters/` | Список майстрів |
| `/services/` | Список послуг |
| `/schedule/` | Розклад доступності |
| `/dashboard/` | Панель адміністратора (потрібен staff) |
| `/admin/` | Django Admin |

## Статуси записів

- **Очікує підтвердження** — новий запис від клієнта
- **Підтверджено** — адміністратор підтвердив
- **Скасовано** — запис скасовано
- **Виконано** — візит відбувся
