from rest_framework import serializers, validators

from bids.models import Bid, Order
from users.serializers import CompanySerializer


class BidListSerializer(serializers.ModelSerializer):
    transportation_company = CompanySerializer()

    class Meta:
        model = Bid
        fields = [
            'bid_number', 'status', 'transportation_type', 'bid_date',
            'planned_departure_date', 'planned_arrival_date', 'transportation_company',
            'fact_departure_date', 'fact_arrival_date', 'order_id'
        ]


class BidUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = ['status', 'fact_departure_date', 'fact_arrival_date']

    def validate_status(self, status):
        if not (self.instance.status == Bid.CREATED and status == Bid.STARTED):
            raise validators.ValidationError('Incorrect status')
        return status

    def validate_fact_departure_date(self, date):
        if self.instance.fact_departure_date:
            raise validators.ValidationError('fact_departure_date already exists')
        if self.instance.status == Bid.STARTED:
            return date
        raise validators.ValidationError('Permission denied fact_departure_date')

    def validate_fact_arrival_date(self, date):
        if self.instance.fact_arrival_date:
            raise validators.ValidationError('fact_arrival_date already exists')
        if self.instance.fact_departure_date and \
            self.instance.fact_departure_date < date and \
            self.instance.status == Bid.IN_WAY:
            return date
        raise validators.ValidationError('Permission denied fact_arrival_date')


class BidRetreiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    bids = BidListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
