# Generated by Django 3.1.3 on 2020-11-12 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_update_agent_primary_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="dark_mode",
            field=models.BooleanField(default=True),
        ),
    ]
