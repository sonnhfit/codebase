# Generated by Django 2.2.2 on 2019-08-07 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_remove_file_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='File',
        ),
    ]
