# Generated by Django 3.0 on 2019-12-27 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('mainApp', '0014_auto_20191227_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='problem_statement_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments',
                                    to='mainApp.ProblemStatementTeam'),
        ),
    ]