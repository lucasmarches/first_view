# Generated by Django 2.2.2 on 2019-07-04 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0022_auto_20190704_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadecases',
            name='date_end',
            field=models.DateField(default='2010-01-01'),
            preserve_default=False,
        ),
    ]