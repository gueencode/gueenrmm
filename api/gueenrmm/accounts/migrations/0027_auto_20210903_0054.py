# Generated by Django 3.2.6 on 2021-09-03 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_auto_20210901_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='api_key', to='accounts.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='block_dashboard_login',
            field=models.BooleanField(default=False),
        ),
    ]
