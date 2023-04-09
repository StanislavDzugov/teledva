import datetime
import logging

from django.db import models
from teledva.settings import DEFAULT_AUCTION_TIME

from users.models import Company, CustomUser

logger = logging.getLogger('__name__')


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)

    class Meta:
        abstract = True


class Attachment(TimeStampedMixin):
    
    DAILY = 1
    FINAL = 2

    TYPE_ENUM = [
        (DAILY, 'Ежедневный'),
        (FINAL, 'Итоговый')
    ]

    file = models.FileField('Выгрузка', upload_to='attachments/')
    type = models.IntegerField('Тип файла', choices=TYPE_ENUM)

    def __str__(self):
        return self.file.name
    
    class Meta:
        verbose_name = 'Приложение'
        verbose_name_plural = 'Приложения'


class Order(TimeStampedMixin):
    """Заказ, состоит из одной или нескольких заявок"""
    transportation_company = models.ForeignKey(
        Company, verbose_name='Компания перевозчик',
        related_name='orders',
        on_delete=models.CASCADE, db_index=True
    )
    transportation_type = models.CharField(
        'Вид транспортной услуги', max_length=255
        )

    def __str__(self):
        return f'Звявки № {[bid.bid_number for bid in self.bids.all()]}'


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        unique_together = ('id', 'transportation_company')


class Bid(TimeStampedMixin):
    """Заявка"""

    CREATED = 0
    STARTED = 1
    IN_WAY = 2
    DELIVERED= 3
    CANCELED = 4

    STATUS_ENUM = [
        (CREATED, 'Создана'),
        (STARTED, 'Принята'),
        (IN_WAY, 'В пути'),
        (DELIVERED, 'Доставлена'),
        (CANCELED, 'Отменена')
    ]

    order = models.ForeignKey(
        Order, verbose_name='Заказ', 
        related_name='bids', on_delete=models.CASCADE
    )
    status = models.IntegerField('Статус', choices=STATUS_ENUM, default=CREATED)

    requirement_number = models.CharField(
        'Номер требования', max_length=255, blank=True, null=True
    )
    bid_number = models.CharField(
        'Номер поручения', max_length=255, unique=True
    )
    bid_date = models.DateField('Дата поручения')
    transportation_type = models.CharField(
        'Вид транспортной услуги', max_length=255
        )
    vehicle_payload = models.FloatField('Тоннаж ТС', null=True, blank=True)
    vehicles_number = models.IntegerField(
        'Количество транспортных средств', null=True, blank=True
    )
    planned_departure_date = models.DateField(
        'Запланированная дата отправления'
    )
    planned_arrival_date = models.DateField(
        'Запланированная дата получения'
    )
    transportation_company = models.ForeignKey(
        Company, verbose_name='Компания перевозчик',
        related_name='bids',
        on_delete=models.CASCADE, db_index=True
    )
    annotation = models.TextField('Примечание', blank=True, null=True)

    sender_company = models.CharField(
        'Компания отправитель',
        blank=True,
        max_length=1000,
        null=True
    )
    loading_full_address = models.TextField('Адрес погрузки', blank=True, null=True)
    loading_city = models.CharField('Город погрузки', max_length=255, blank=True, null=True)
    sender_name = models.CharField(
        'ФИО отправителя', max_length=255, blank=True, null=True
    )
    sender_phone = models.CharField(
        'Телефон отправителя', null=True, blank=True, max_length=1000
    )
    sender_email = models.CharField(
        'Email отправителя', blank=True, max_length=255, null=True
    )

    recipient_company = models.CharField(
        'Компания получатель',
        blank=True,
        max_length=1000,
        null=True
    )
    dispatch_full_address = models.TextField('Адрес выгрузки', blank=True, null=True)
    dispatch_city = models.CharField('Город выгрузки', max_length=255)
    recipient_name = models.CharField(
        'ФИО получателя', max_length=255, blank=True, null=True
    )
    recipient_phone = models.CharField(
        'Телефон получателя', null=True, blank=True, max_length=1000
    )
    recipient_email = models.CharField(
        'Email получателя', blank=True, max_length=255, null=True
    )

    slots_number = models.IntegerField('Количество мест', blank=True, null=True)
    total_weight = models.FloatField('Общий вес груза', null=True, blank=True)
    total_volume = models.FloatField('Общий объем груза', null=True, blank=True)
    load_dimensions = models.CharField(
        'Габариты груза', max_length=1000, blank=True, null=True
    )
    load_weight = models.CharField('Вес', max_length=1000, blank=True, null=True
    )
    load_value = models.DecimalField(
        'Стоимость груза', null=True, blank=True,
        max_digits=12, decimal_places=2
    )
    shipment_price = models.DecimalField(
        'Стоимость перевозки с НДС',
        max_digits=12, decimal_places=2,
        blank=True, null=True
    )

    fact_departure_date = models.DateField(
        'Фактическа дата отправления', null=True, blank=True
    )
    fact_arrival_date = models.DateField(
        'Фактическая дата получения', null=True, blank=True
    )
    attachments = models.ManyToManyField(Attachment, blank=True, related_name='bids')

    def __str__(self):
        return f'{self.bid_number}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ('-order__id',)


class Auction(TimeStampedMixin):
    ACTIVE = 1
    FINISHED = 2
    CANCELED = 3

    STATUS_ENUM = [
        (ACTIVE, 'Активный'),
        (FINISHED, 'Завершен'),
        (CANCELED, 'Отменен')
    ]
    auction_default_company = models.ForeignKey(
        Company, verbose_name='Компания для аукциона',
        related_name='orders_default', null=True, blank=True,
        on_delete=models.CASCADE, db_index=True,
        help_text='Если никто не участвует,\
            автоматически ставим данную компанию победителем'
    )
    auction_finish_date = models.DateTimeField(
        'Дата завершения аукциона', null=True, blank=True
    )
    status = models.IntegerField('Статус', choices=STATUS_ENUM, default=ACTIVE)
    order = models.OneToOneField(
        Order, verbose_name='Разыгрываемый ордер',
        on_delete=models.CASCADE, related_name='auction'
    )

    def __str__(self):
        return f'Аукцион на звяку. \
            Автоматический выбор комании: {self.auction_default_company} \
            дата окончания: {self.auction_finish_date}'

    class Meta:
        verbose_name = 'Аукцион'
        verbose_name_plural = 'Аукционы'

    @staticmethod
    def create_auction(company, order):
        auction_hours = datetime.timedelta(minutes=DEFAULT_AUCTION_TIME)
        auction = Auction.objects.create(
            auction_default_company=company,
            auction_finish_date=datetime.datetime.now() + auction_hours,
            order=order
        )
        return auction

    
class AuctionOffer(TimeStampedMixin):
    auction = models.ForeignKey(
        Auction, verbose_name='Заказ-аукцион', related_name='auction_offers',
        on_delete=models.CASCADE
    )
    transportation_company = models.ForeignKey(
        Company, verbose_name='Компания перевозчик',
        related_name='auction_offers',
        on_delete=models.CASCADE, db_index=True
    )
    price = models.DecimalField(
        'Предложенная стоимость', max_digits=12, decimal_places=2
    )
    user = models.ForeignKey(CustomUser,
        verbose_name='Предложивший пользователь',
        on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f'{self.auction.id}:{self.transportation_company}:{self.price}'

    class Meta:
        verbose_name = 'Предложение по аукциону'
        verbose_name_plural = 'Предложения по аукционам'
        unique_together = ('id', 'auction', 'transportation_company')