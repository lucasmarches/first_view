# Generated by Django 2.2.2 on 2019-07-04 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0011_auto_20190704_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadecases',
            name='date_end',
            field=models.DateField(blank=True, null=True),
        ),
    ]
