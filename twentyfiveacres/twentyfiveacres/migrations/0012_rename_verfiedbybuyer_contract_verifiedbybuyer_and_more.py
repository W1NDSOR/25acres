# Generated by Django 4.2.5 on 2023-10-01 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twentyfiveacres', '0011_remove_contract_contracttext_contract_verfiedbybuyer_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='verfiedByBuyer',
            new_name='verifiedByBuyer',
        ),
        migrations.RenameField(
            model_name='contract',
            old_name='verfiedByPortal',
            new_name='verifiedByPortal',
        ),
        migrations.RenameField(
            model_name='contract',
            old_name='verfiedBySeller',
            new_name='verifiedBySeller',
        ),
    ]