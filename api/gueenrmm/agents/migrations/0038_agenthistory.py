# Generated by Django 3.2.1 on 2021-07-06 02:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0037_auto_20210627_0014'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('task_run', 'Task Run'), ('script_run', 'Script Run'), ('cmd_run', 'CMD Run')], default='cmd_run', max_length=50)),
                ('command', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('success', 'Success'), ('failure', 'Failure')], default='success', max_length=50)),
                ('username', models.CharField(default='system', max_length=50)),
                ('results', models.TextField(blank=True, null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='agents.agent')),
            ],
        ),
    ]
