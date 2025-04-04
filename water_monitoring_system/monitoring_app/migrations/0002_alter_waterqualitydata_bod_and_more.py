# Generated by Django 5.1.7 on 2025-03-24 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waterqualitydata',
            name='bod',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='cod',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='daily_flow',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='flow',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='ph',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='total_flow',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='waterqualitydata',
            name='tss',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
