# Generated by Django 4.2.5 on 2023-10-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twentyfiveacres', '0003_alter_contract_buyercontract'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SHA',
        ),
        migrations.AlterField(
            model_name='buyercontract',
            name='contractHashIdentifier',
            field=models.CharField(max_length=128, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='property',
            name='ownershipDocumentHash',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='property',
            name='propertyHashIdentifier',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='sellercontract',
            name='contractHashIdentifier',
            field=models.CharField(max_length=128, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='documentHash',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='userHash',
            field=models.CharField(max_length=128),
        ),
    ]
