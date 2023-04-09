from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserRetrieveUpdateView, LoginView, LogoutView, 
    RegisterUserApiView, UpdatePasswordView
)

router = DefaultRouter()
#router.register('entity-tasks', EntityTaskViewSet)

urlpatterns = [
    path('profile/', UserRetrieveUpdateView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegisterUserApiView.as_view()),
    path('password-change/', UpdatePasswordView.as_view()),

]