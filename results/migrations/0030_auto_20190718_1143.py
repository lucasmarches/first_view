# Generated by Django 2.2.2 on 2019-07-18 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0029_auto_20190704_1418'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cadecases',
            options={'ordering': ['-date']},
        ),
    ]
