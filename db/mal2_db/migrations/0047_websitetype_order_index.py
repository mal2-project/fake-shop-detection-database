# Generated by Django 2.2.4 on 2020-12-02 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mal2_db', '0046_auto_20201111_0703'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitetype',
            name='order_index',
            field=models.PositiveIntegerField(default=0, verbose_name='Order index'),
        ),
    ]