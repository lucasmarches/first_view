# Generated by Django 2.2.2 on 2019-07-04 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0015_auto_20190704_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadecases',
            name='date_end',
            field=models.DateField(default='0000-00-00'),
        ),
    ]
