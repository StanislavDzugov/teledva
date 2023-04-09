from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    name = models.CharField(_('company name'), max_length=255, unique=True)
    address = models.TextField(_('address'), blank=True, null=True)
    email = models.EmailField(_('email'))
    phone = models.IntegerField(_('phone'), blank=True, null=True, help_text='format: 79995555656')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'


class CustomUserManager(UserManager):
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        tele2 = Company.objects.filter(inn=9909005588).first()
        if not tele2:
            tele2 = Company(
                name='tele2', inn=9909005588,
                address='121099, Москва, Новинский бульвар, д.8'
            )
            tele2.save()
        extra_fields['company'] = tele2
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ADMIN = 1
    COMPANY_USER = 2
    LOGIST_USER = 3

    ROLE_ENUM = [
        (ADMIN, 'Админ'),
        (COMPANY_USER, 'Пользователь'),
        (LOGIST_USER, 'Логист')
    ]
    company = models.ForeignKey(
        Company, verbose_name=_('company'), related_name='users', 
        on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.IntegerField(_('role'), choices=ROLE_ENUM, default=COMPANY_USER)
    email = models.EmailField(_("email address"), unique=True)
    phone = models.IntegerField(_('phone'), blank=True, null=True, help_text='format: 79995555656')

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
