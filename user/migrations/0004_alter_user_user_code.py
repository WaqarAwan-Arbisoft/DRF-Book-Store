# Generated by Django 4.1.1 on 2022-10-24 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_user_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
