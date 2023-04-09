from rest_framework import viewsets
from django.db.models import Q

from .serializers import (
    BidListSerializer, BidRetreiveSerializer,
    BidUpdateSerializer, OrderSerializer
)
from .models import Auction, Bid, Order
from .filters import BidsFilter
from users.models import CustomUser


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        user= self.request.user
        base_queryset = queryset.filter(
            Q(auction=None) | Q(auction__status=Auction.FINISHED),
            )
        if user.role == CustomUser.ADMIN:
            return base_queryset
        elif user.role == CustomUser.LOGIST_USER:
            return base_queryset.exclude(bids__status=Bid.CREATED)
        return base_queryset.filter(transportation_company=user.company).exclude(bids__status=Bid.CREATED)


class BidsViewSet(viewsets.ModelViewSet):
    serializer_class = BidListSerializer
    queryset = Bid.objects.all()
    filter_backends = [BidsFilter]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return BidUpdateSerializer
        elif self.action == 'retrieve':
            return BidRetreiveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        user= self.request.user
        base_queryset = queryset.filter(
            Q(order__auction=None) | Q(order__auction__status=Auction.FINISHED),
            )
        if user.role == CustomUser.ADMIN:
            return base_queryset
        elif user.role == CustomUser.LOGIST_USER:
            return base_queryset.exclude(status=Bid.CREATED)
        return base_queryset.filter(order__transportation_company=user.company).exclude(status=Bid.CREATED)

