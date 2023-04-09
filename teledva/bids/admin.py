from django.contrib import admin

from bids.models import Attachment, Auction, AuctionOffer, Bid, Order


admin.site.register(Bid)
admin.site.register(Order)
admin.site.register(Attachment)
admin.site.register(AuctionOffer)
admin.site.register(Auction)