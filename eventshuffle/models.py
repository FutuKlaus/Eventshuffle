from django.db import models
from django.contrib.postgres.fields import ArrayField


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class EventDate(models.Model):
    event = models.ForeignKey(Event, related_name='dates', on_delete=models.CASCADE)
    date = models.DateField()

    people = ArrayField(models.CharField(max_length=255), blank=True, default=list)

    def __str__(self):
        return f"{self.event.name} - {self.date}"