# Generated by Django 4.2.5 on 2023-10-22 13:59

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('rollNumber', models.IntegerField(unique=True)),
                ('verificationCode', models.CharField(blank=True, max_length=6, null=True)),
                ('documentHash', models.CharField(blank=True, max_length=128, null=True)),
                ('userHash', models.CharField(max_length=128)),
                ('wallet', models.IntegerField(default=1000000000)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BuyerContract',
            fields=[
                ('contractHashIdentifier', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('contractAddress', models.CharField(blank=True, max_length=255, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_contract', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('locationId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10, null=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('propertyId', models.AutoField(primary_key=True, serialize=False)),
                ('listed', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('bedrooms', models.PositiveIntegerField()),
                ('bathrooms', models.PositiveIntegerField()),
                ('area', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('for_sale', 'For Sale'), ('for_rent', 'For Rent'), ('sold', 'Sold'), ('rented', 'Rented')], max_length=20)),
                ('availabilityDate', models.DateField()),
                ('propertyHashIdentifier', models.CharField(max_length=128)),
                ('currentBid', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('ownershipDocumentHash', models.CharField(max_length=128)),
                ('reported', models.BooleanField(default=False)),
                ('bidder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_bidder', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twentyfiveacres.location')),
                ('originalOwner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='property_original_owner', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transactionId', models.AutoField(primary_key=True, serialize=False)),
                ('withPortal', models.BooleanField(default=False)),
                ('amount', models.IntegerField(default=0)),
                ('credit', models.BooleanField(default=True)),
                ('debit', models.BooleanField(default=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('other', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_other_user_relation', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_user_relation', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SellerContract',
            fields=[
                ('contractHashIdentifier', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('contractAddress', models.CharField(blank=True, max_length=255, null=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twentyfiveacres.property')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_contract', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('imageId', models.AutoField(primary_key=True, serialize=False)),
                ('imageUrl', models.URLField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twentyfiveacres.property')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyerContract', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_buyer_contract', to='twentyfiveacres.buyercontract')),
                ('property', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='twentyfiveacres.property', verbose_name='related_proprety')),
                ('sellerContract', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='related_seller_contract', to='twentyfiveacres.sellercontract')),
            ],
        ),
        migrations.AddField(
            model_name='buyercontract',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twentyfiveacres.property'),
        ),
    ]
