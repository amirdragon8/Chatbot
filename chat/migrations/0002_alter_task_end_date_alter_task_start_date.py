# Generated by Django 4.2.17 on 2025-01-10 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='end_date',
            field=models.DateField(help_text='End date of the task(YYYY-MM-DD)'),
        ),
        migrations.AlterField(
            model_name='task',
            name='start_date',
            field=models.DateField(help_text='Start date of the task(YYYY-MM-DD)'),
        ),
    ]
