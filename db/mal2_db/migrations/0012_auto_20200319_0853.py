# Generated by Django 2.2.4 on 2020-03-19 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mal2_db', '0011_website_website_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitetype',
            name='type_de',
            field=models.CharField(max_length=255, null=True, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='websitetype',
            name='type_en_GB',
            field=models.CharField(max_length=255, null=True, verbose_name='Type'),
        ),
    ]