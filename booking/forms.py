from django import forms
from django.utils import timezone
from .models import Appointment, Master, Service


class AppointmentForm(forms.ModelForm):
    """Форма для запису клієнта"""

    class Meta:
        model = Appointment
        fields = [
            'client_name', 'client_phone', 'client_email',
            'master', 'service', 'date', 'time', 'comment'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше ім\'я'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+38 (0XX) XXX-XX-XX'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'master': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Додатковий коментар (необов\'язково)'
            }),
        }
        labels = {
            'client_name': 'Ваше ім\'я',
            'client_phone': 'Телефон',
            'client_email': 'Email',
            'master': 'Майстер',
            'service': 'Послуга',
            'date': 'Дата',
            'time': 'Час',
            'comment': 'Коментар',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показуємо лише активних майстрів та послуги
        self.fields['master'].queryset = Master.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('Не можна записатися на минулу дату.')
        return date

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if master and date and time:
            # Перевірка чи вільний час у майстра
            existing = Appointment.objects.filter(
                master=master,
                date=date,
                time=time,
                status__in=['pending', 'confirmed']
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    f'Майстер {master} вже зайнятий о {time} {date}. '
                    f'Оберіть інший час або майстра.'
                )
        return cleaned_data
