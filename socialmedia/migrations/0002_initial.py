# Generated by Django 4.1.1 on 2022-10-05 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('socialmedia', '0001_initial'),
        ('books', '0001_initial'),
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='friendshipnotification',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='requestReceiver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendshipnotification',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='requestSender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendship',
            name='initiatedBy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='frSender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendship',
            name='initiatedTowards',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='frReceiver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='book',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='books.book'),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='creator',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='favorite',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.favorite'),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='like',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.like'),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='notify',
            field=models.ManyToManyField(
                related_name='notificationFor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookfeed',
            name='review',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.review'),
        ),
    ]
