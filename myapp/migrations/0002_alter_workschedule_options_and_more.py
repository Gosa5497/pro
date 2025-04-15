# Generated by Django 5.1.3 on 2025-04-06 18:39

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workschedule',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterUniqueTogether(
            name='workschedule',
            unique_together={('student', 'is_active')},
        ),
        migrations.AddField(
            model_name='workschedule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='workschedule',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_schedules', to='myapp.student'),
        ),
        migrations.AlterField(
            model_name='workschedule',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_schedules', to='myapp.supervisor'),
        ),
        migrations.AlterField(
            model_name='workschedule',
            name='workdays_per_week',
            field=models.PositiveIntegerField(default=4, help_text='Number of required task submissions per week', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.RemoveField(
            model_name='workschedule',
            name='assigned_days',
        ),
        migrations.RemoveField(
            model_name='workschedule',
            name='start_date',
        ),
    ]
