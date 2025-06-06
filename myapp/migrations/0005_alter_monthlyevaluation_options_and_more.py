# Generated by Django 5.1.3 on 2025-04-08 19:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_monthlyevaluation_month_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monthlyevaluation',
            options={'ordering': ['-month_number']},
        ),
        migrations.AlterUniqueTogether(
            name='monthlyevaluation',
            unique_together={('student', 'month_number')},
        ),
        migrations.AddField(
            model_name='monthlyevaluation',
            name='total_score',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monthlyevaluation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='monthlyevaluation',
            name='month_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='monthlyevaluation',
            name='punctuality',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='monthlyevaluation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='myapp.student'),
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='accuracy',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='additional_comments',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='communication',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='cooperation',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='engagement',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='independence',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='need_for_work',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='organizational_skills',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='professionalism',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='project_support',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='reliability',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='responsibility',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='speed_of_work',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='team_quality',
        ),
        migrations.RemoveField(
            model_name='monthlyevaluation',
            name='technical_skills',
        ),
    ]
