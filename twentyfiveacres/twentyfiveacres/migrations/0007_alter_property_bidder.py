# Generated by Django 4.2.5 on 2023-09-27 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twentyfiveacres', '0006_merge_20230927_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='bidder',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
