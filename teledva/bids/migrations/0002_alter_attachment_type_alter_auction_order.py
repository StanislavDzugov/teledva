# Generated by Django 4.1.1 on 2023-04-08 19:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bids', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='type',
            field=models.IntegerField(choices=[(1, 'Ежедневный'), (2, 'Итоговый')], verbose_name='Тип файла'),
        ),
        migrations.AlterField(
            model_name='auction',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auction', to='bids.order', verbose_name='Разыгрываемый ордер'),
        ),
    ]