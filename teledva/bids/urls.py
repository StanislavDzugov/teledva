from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, BidsViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='Order')
router.register('', BidsViewSet, basename='Bid')

urlpatterns = [
    path('', include(router.urls)),
]