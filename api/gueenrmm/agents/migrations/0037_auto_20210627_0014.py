# Generated by Django 3.2.4 on 2021-06-27 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0036_agent_block_policy_inheritance'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='has_patches_pending',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='agent',
            name='pending_actions_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
