# Generated by Django 5.1.6 on 2025-02-24 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_delete_serviceprovider'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.FileField(upload_to='')),
                ('name', models.TextField()),
                ('phone', models.IntegerField(unique=True)),
                ('experience', models.IntegerField()),
                ('availability', models.BooleanField(default=True)),
                ('rating', models.FloatField(default=0.0)),
                ('location', models.TextField()),
                ('des', models.TextField()),
                ('charge', models.FloatField()),
                ('working_hours', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.category')),
            ],
        ),
    ]
