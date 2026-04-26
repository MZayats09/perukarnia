from django.db import models


class Master(models.Model):
    """Таблиця: Майстри"""
    full_name = models.CharField(max_length=100, verbose_name="Майстер")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    # Поле для фото (дозволяємо бути порожнім, як у зразку)
    photo = models.ImageField(upload_to='masters_photos/', blank=True, null=True, verbose_name="Фото")

    class Meta:
        verbose_name = "Майстер"
        verbose_name_plural = "Майстри"

    def __str__(self):
        return self.full_name


class Client(models.Model):
    """Таблиця: Інформація про клієнта"""
    full_name = models.CharField(max_length=100, verbose_name="Клієнт")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    photo = models.ImageField(upload_to='clients_photos/', blank=True, null=True, verbose_name="Фото")

    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"

    def __str__(self):
        return self.full_name


class Order(models.Model):
    """Таблиця: Інформація про замовлення"""
    visit_date = models.DateField(null=True, blank=True, verbose_name="Дата візиту")
    service = models.CharField(max_length=255, verbose_name="Послуга")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    duration = models.PositiveIntegerField(verbose_name="Тривалість (хв)")

    # Зв'язки з іншими таблицями (ForeignKey)
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Хто робив (майстер)"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Кому робили (клієнт)"
    )

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f"{self.service} ({self.visit_date})"