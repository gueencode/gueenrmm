# Generated by Django 3.2.6 on 2021-09-17 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("automation", "0008_auto_20210302_0415"),
    ]

    operations = [
        migrations.AlterField(
            model_name="policy",
            name="created_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="policy",
            name="modified_by",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
