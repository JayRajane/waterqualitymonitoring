# Generated by Django 5.1.7 on 2025-04-28 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring_app', '0004_rename_flow_waterqualitydata_flow1_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='show_daily_flow',
            new_name='show_daily_flow1',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='show_flow',
            new_name='show_daily_flow2',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='show_monthly_flow',
            new_name='show_daily_flow3',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='show_total_flow',
            new_name='show_flow1',
        ),
        migrations.RenameField(
            model_name='waterqualitydata',
            old_name='daily_flow',
            new_name='daily_flow1',
        ),
        migrations.RenameField(
            model_name='waterqualitydata',
            old_name='monthly_flow',
            new_name='daily_flow2',
        ),
        migrations.RenameField(
            model_name='waterqualitydata',
            old_name='total_flow',
            new_name='daily_flow3',
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_flow2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_flow3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_monthly_flow1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_monthly_flow2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_monthly_flow3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_total_flow1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_total_flow2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='show_total_flow3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='monthly_flow1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='monthly_flow2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='monthly_flow3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='total_flow1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='total_flow2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='waterqualitydata',
            name='total_flow3',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
