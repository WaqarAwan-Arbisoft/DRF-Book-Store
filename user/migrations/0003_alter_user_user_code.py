# Generated by Django 4.1.1 on 2022-10-12 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_code',
            field=models.IntegerField(blank=True),
        ),
    ]