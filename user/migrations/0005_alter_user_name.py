# Generated by Django 4.1.1 on 2022-10-24 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_user_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default='Default username', max_length=255),
        ),
    ]
