# Generated by Django 3.0 on 2019-12-21 17:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('mainApp', '0009_auto_20191221_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemstatement',
            name='category',
            field=models.CharField(choices=[('S', 'Software'), ('H', 'Hardware')], max_length=70),
        ),
    ]