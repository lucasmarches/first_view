# Generated by Django 2.2.2 on 2019-06-27 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20190626_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicJobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('legal_intrument', models.TextField()),
                ('job_giver', models.TextField()),
                ('appointed', models.TextField()),
                ('job', models.TextField()),
                ('where', models.TextField()),
                ('das_code', models.TextField()),
                ('link', models.TextField()),
                ('date', models.DateField()),
            ],
        ),
    ]
