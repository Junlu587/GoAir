# Generated by Django 5.1.7 on 2025-03-19 17:25

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('airline', models.CharField(default='Unknown Airline', max_length=100)),
                ('flight_number', models.CharField(default='UNKNOWN', max_length=10, unique=True)),
                ('origin', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('departure_date', models.DateField(default=datetime.date.today)),
                ('departure_time', models.TimeField(blank=True, null=True)),
                ('arrival_date', models.DateField(blank=True, null=True)),
                ('arrival_time', models.TimeField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=10)),
                ('available_seats', models.PositiveIntegerField(default=100)),
                ('stops', models.IntegerField(default=0)),
                ('aircraft', models.CharField(blank=True, default='Unknown', max_length=100)),
                ('flight_token', models.CharField(blank=True, max_length=100, null=True)),
                ('flight_class', models.CharField(default='economy', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SavedTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_data', models.JSONField(help_text='Stores the flight trip data from search results')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_in', to='flights.flight')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_trips', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
