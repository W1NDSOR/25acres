# Generated by Django 4.2.5 on 2023-10-01 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twentyfiveacres', '0009_property_transaction_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='currentBid',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
