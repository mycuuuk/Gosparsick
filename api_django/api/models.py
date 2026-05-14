from django.contrib.auth.models import AbstractUser
from django.db import models
import os


class CustomUser(AbstractUser):
    def image_upload_to(self, instance=None):
        if instance:
            return os.path.join("Users", self.username, instance)
        return None

    STATUS = (
        ('regular', 'regular'),
        ('subscriber', 'subscriber'),
        ('moderator', 'moderator'),
    )

    email = models.EmailField(unique=True)
    status = models.CharField(max_length=100, choices=STATUS, default='regular')
    payed_orders = models.PositiveSmallIntegerField(default='1', verbose_name="Кол-во оплаченных заказов", blank=True)

    def __str__(self):
        return self.username


class Order(models.Model):
    request = models.CharField(max_length=255, verbose_name="Введите поисковый запрос")
    year_start = models.CharField(max_length=255, verbose_name="Введите год начала периода отчета")
    year_end = models.CharField(max_length=255, verbose_name="Введите год окончания периода отчета")
    ktru_plots = models.BooleanField(verbose_name="Хотите ли вы посмотреть данные по закупкам товаров содержащих в КТРУ данные кодовые слова? ")
    customers_plots = models.BooleanField(verbose_name="Хотите посмотреть данные по заказчикам, подчиненным Министерству Здравоохранения РФ")
    regions_plots = models.BooleanField(verbose_name="Хотите ли вы получить распределение по закупкам изделий произведенных в РФ и импортных в регионах")
    mnn_plots = models.BooleanField(verbose_name="Хотите ли вы получить данные по МНН закупаемых лекарственных средств, содержащих данные кодовые слова?")
    parse_data = models.BooleanField(verbose_name="Хотите ли вы выгружать данные с сайта?")
    is_ready = models.ForeignKey('Order_cat', on_delete=models.PROTECT, default=1)
    username = models.CharField(max_length=255, verbose_name="", blank=True)
    email = models.CharField(max_length=255, verbose_name="", blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    result_pdf = models.CharField(max_length=500, blank=True, default='')
    result_excel = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return self.request


class Order_cat(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

