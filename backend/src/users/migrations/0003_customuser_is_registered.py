# Generated by Django 3.0.7 on 2020-06-22 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_invite'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_registered',
            field=models.BooleanField(default=False),
        ),
    ]
