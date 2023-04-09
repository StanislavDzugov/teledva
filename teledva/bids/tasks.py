import logging
import datetime
from django.utils import timezone

from celery import shared_task
from bids.models import Auction, AuctionOffer

logger = logging.getLogger('__name__')


@shared_task()
def finish_auction():
    auctions = Auction.objects.filter(status=Auction.ACTIVE)
    now = timezone.now()
    logger.info(f"start check auctions: {auctions.values('id')}")
    for auction in auctions:
        if now >= auction.auction_finish_date:
            offer = AuctionOffer.objects.filter(auction=auction).order_by('-price').first()
            shipment_price = auction.order.bids.first().shipment_price
            auction.status = Auction.FINISHED
            if offer and shipment_price and offer.price < shipment_price:
                transportation_company = offer.transportation_company
                auction.order.bids.update(
                    shipment_price=offer.price,
                    transportation_company=transportation_company
                )
            elif shipment_price:
                auction.order.bids.update(
                    transportation_company=auction.auction_default_company
                )
            else:
                auction.status = Auction.CANCELED
            auction.save()
            logger.info(f"Order: {auction.order.id} updated, auction {auction.id} finished with status: {auction.status}")