# Generated by Django 2.2.2 on 2019-07-04 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0006_auto_20190704_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadecases',
            name='date_end',
            field=models.DateField(blank=True, default='', null=True),
        ),
    ]