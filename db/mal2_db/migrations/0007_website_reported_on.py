# Generated by Django 2.2.4 on 2020-03-18 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mal2_db', '0006_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='reported_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Reported on'),
            preserve_default=False,
        ),
    ]