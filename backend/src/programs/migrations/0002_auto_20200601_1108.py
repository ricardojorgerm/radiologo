# Generated by Django 3.0.6 on 2020-06-01 11:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('programs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='authors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Autores'),
        ),
        migrations.AddField(
            model_name='day',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programs.Program'),
        ),
    ]
