# Generated by Django 3.1.4 on 2021-01-10 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checks", "0012_auto_20210110_0503"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkhistory",
            name="y",
            field=models.PositiveIntegerField(null=True),
        ),
    ]
