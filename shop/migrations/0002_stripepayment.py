# Generated by Django 4.1.1 on 2022-10-07 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('payment_method_id', models.CharField(max_length=150)),
            ],
        ),
    ]