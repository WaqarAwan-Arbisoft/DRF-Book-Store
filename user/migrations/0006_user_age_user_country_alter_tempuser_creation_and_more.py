# Generated by Django 4.1.1 on 2022-09-06 11:01

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_tempuser_creation_alter_tempuser_user_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(default=18, validators=[django.core.validators.MinValueValidator(15)]),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(default='Pakistan', max_length=50),
        ),
        migrations.AlterField(
            model_name='tempuser',
            name='creation',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 11, 1, 11, 534247, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='tempuser',
            name='user_code',
            field=models.IntegerField(blank=True, default=785453, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='creation',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 11, 1, 11, 532038, tzinfo=datetime.timezone.utc)),
        ),
    ]