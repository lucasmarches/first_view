# Generated by Django 2.2.2 on 2019-07-04 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0016_auto_20190704_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadecases',
            name='date_end',
            field=models.DateField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='cadecases',
            name='decision',
            field=models.TextField(blank=True),
        ),
    ]
