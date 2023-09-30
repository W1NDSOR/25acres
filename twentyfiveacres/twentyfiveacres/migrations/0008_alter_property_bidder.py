# Generated by Django 4.2.5 on 2023-09-27 03:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twentyfiveacres', '0007_alter_property_bidder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='bidder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_bidder', to=settings.AUTH_USER_MODEL),
        ),
    ]