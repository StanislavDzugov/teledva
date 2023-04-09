import os
import logging

from django.db import transaction
from openpyxl import load_workbook

from users.models import Company
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from bids.models import Attachment, Order, Auction,  Bid
from bids.utils import convert_date, digit_or_none


logger = logging.getLogger(__name__)


@transaction.atomic
def parse_file(instance):
    path = os.path.join(os.getcwd(), instance.file.path)
    worksheet = load_workbook(filename=path, data_only=True)
    sheet = worksheet.active
    row_index = 1
    while row_index >= 1 and sheet['B{}'.format(row_index)].value:
        company = Company.objects.filter(
            name__iexact=sheet['I{}'.format(row_index)].value
        ).first()
        bid = Bid.objects.filter(
            bid_number=sheet['B{}'.format(row_index)].value
        )
        auction = Auction.objects.filter(
            order__bids__bid_number=sheet['B{}'.format(row_index)].value
        )
        if company:
            if not bid.exists() and not auction.exists() and instance.type == Attachment.DAILY:
                bid_data = {
                    "requirement_number": sheet['A{}'.format(row_index)].value,
                    "bid_number": sheet['B{}'.format(row_index)].value,
                    "bid_date": convert_date(sheet['C{}'.format(row_index)].value),
                    "transportation_type": sheet['D{}'.format(row_index)].value,
                    "vehicle_payload": digit_or_none(sheet['E{}'.format(row_index)].value),
                    "vehicles_number": digit_or_none(sheet['F{}'.format(row_index)].value),
                    "planned_departure_date": convert_date(sheet['G{}'.format(row_index)].value),
                    "planned_arrival_date": convert_date(sheet['H{}'.format(row_index)].value),
                    "transportation_company": company,
                    "annotation": sheet['K{}'.format(row_index)].value,
                    "sender_company": sheet['L{}'.format(row_index)].value,
                    "loading_full_address": sheet['M{}'.format(row_index)].value,
                    "loading_city": sheet['N{}'.format(row_index)].value,
                    "sender_name": sheet['O{}'.format(row_index)].value,
                    "sender_phone": sheet['P{}'.format(row_index)].value,
                    "sender_email": sheet['Q{}'.format(row_index)].value,
                    "recipient_company": sheet['R{}'.format(row_index)].value,
                    "dispatch_full_address": sheet['S{}'.format(row_index)].value,
                    "dispatch_city": sheet['T{}'.format(row_index)].value,
                    "recipient_name": sheet['U{}'.format(row_index)].value,
                    "recipient_phone": sheet['V{}'.format(row_index)].value,
                    "recipient_email": sheet['W{}'.format(row_index)].value,
                    "slots_number": digit_or_none(sheet['X{}'.format(row_index)].value),
                    "total_weight": digit_or_none(sheet['Y{}'.format(row_index)].value),
                    "total_volume": digit_or_none(sheet['Z{}'.format(row_index)].value),
                    "load_dimensions": sheet['AA{}'.format(row_index)].value,
                    "load_weight": sheet['AB{}'.format(row_index)].value,
                    "load_value": digit_or_none(sheet['AC{}'.format(row_index)].value),
                    "shipment_price": digit_or_none(sheet['AD{}'.format(row_index)].value)
                }
                if bid_data["transportation_type"]:
                    order = Order.objects.create(
                        transportation_company=company,
                        transportation_type=bid_data["transportation_type"]
                    )
                    transportation_type = bid_data["transportation_type"]
                    if company.name == 'редукцион':
                        def_company = Company.objects.filter(name__iexact=sheet['J{}'.format(row_index)].value).first()
                        Auction.create_auction(
                            company=def_company, order=order
                        )
                try:
                    bid_data.pop("transportation_type")
                    bid = Bid.objects.create(
                        **bid_data,
                        transportation_type=transportation_type,
                        order=order
                    )
                    bid.attachments.add(instance)
                except Exception as e:
                    logger.error("Error %s, while creating bid %s", e, bid_data)
                    raise
            elif bid.exists() and instance.type == Attachment.FINAL:
                bid = bid.first()
                bid.fact_departure_date = convert_date(sheet['AD{}'.format(row_index)].value)
                bid.fact_arrival_date = convert_date(sheet['AE{}'.format(row_index)].value)
                bid.attachments.add(instance)
                if bid.fact_departure_date:
                    bid.status = Bid.IN_WAY
                if bid.fact_arrival_date:
                    bid.status = Bid.DELIVERED
                bid.save()

        else:
            logger.error("Unknown company: %s", sheet['I{}'.format(row_index)].value)
        row_index += 1
    return True


@receiver(post_save, sender=Attachment)
def hanle_xlsx_file(sender, instance, created, **kwargs):
    """Handle xlsx data to models"""
    if created:
        result = parse_file(instance)
        if result is not True:
            raise ValueError("incorrect file data")


@receiver(pre_save, sender=Bid)
def update_bid_status(sender, instance, **kwargs):
    db_instance = Bid.objects.filter(bid_number=instance.bid_number).first()
    if db_instance and not db_instance.fact_departure_date and instance.fact_departure_date:
        instance.status = Bid.IN_WAY
    if db_instance and not db_instance.fact_arrival_date and instance.fact_arrival_date:
        instance.status = Bid.DELIVERED