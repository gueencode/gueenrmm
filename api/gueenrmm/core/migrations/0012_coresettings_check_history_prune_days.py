# Generated by Django 3.1.4 on 2021-01-10 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_auto_20201026_0719"),
    ]

    operations = [
        migrations.AddField(
            model_name="coresettings",
            name="check_history_prune_days",
            field=models.PositiveIntegerField(default=30),
        ),
    ]
