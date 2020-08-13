# Generated by Django 2.2.2 on 2020-08-11 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_key', models.CharField(blank=True, max_length=100, null=True)),
                ('file_up', models.FileField(upload_to='documents/%Y/%m/%d')),
            ],
        ),
    ]
