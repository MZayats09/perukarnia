from django.db import models
from django.contrib.auth.models import User


class Master(models.Model):
    """Модель майстра (барбера)"""
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Акаунт користувача',
        help_text='Прив\'яжіть акаунт, щоб майстер міг входити в систему'
    )
    first_name = models.CharField(max_length=100, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=100, verbose_name='Прізвище')
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    bio = models.TextField(verbose_name='Про майстра', blank=True)
    photo = models.ImageField(
        upload_to='masters/', verbose_name='Фото', blank=True, null=True
    )
    specialization = models.CharField(
        max_length=200, verbose_name='Спеціалізація', blank=True,
        help_text='Наприклад: чоловічі стрижки, борода, укладка'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активний')

    class Meta:
        verbose_name = 'Майстер'
        verbose_name_plural = 'Майстри'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class Service(models.Model):
    """Модель послуги"""
    name = models.CharField(max_length=200, verbose_name='Назва послуги')
    description = models.TextField(verbose_name='Опис', blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name='Ціна (грн)'
    )
    duration = models.PositiveIntegerField(
        verbose_name='Тривалість (хв)',
        help_text='Тривалість послуги у хвилинах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Послуга'
        verbose_name_plural = 'Послуги'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — {self.price} грн ({self.duration} хв)'


class Appointment(models.Model):
    """Модель запису клієнта"""

    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
        ('completed', 'Виконано'),
    ]

    client_name = models.CharField(max_length=200, verbose_name='Ім\'я клієнта')
    client_phone = models.CharField(max_length=20, verbose_name='Телефон')
    client_email = models.EmailField(verbose_name='Email', blank=True)

    master = models.ForeignKey(
        Master, on_delete=models.CASCADE,
        verbose_name='Майстер', related_name='appointments'
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE,
        verbose_name='Послуга', related_name='appointments'
    )

    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Час')

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Статус'
    )
    comment = models.TextField(verbose_name='Коментар', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        verbose_name = 'Запис'
        verbose_name_plural = 'Записи'
        ordering = ['-date', '-time']
        unique_together = ['master', 'date', 'time']

    def __str__(self):
        return (
            f'{self.client_name} → {self.master} | '
            f'{self.date} {self.time} | {self.get_status_display()}'
        )
