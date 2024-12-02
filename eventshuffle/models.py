from django.db import models



class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class EventDate(models.Model):
    event = models.ForeignKey(Event, related_name='dates', on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.event.name} - {self.date}"
    
class Vote(models.Model):
    date = models.ForeignKey(EventDate, related_name='votes', on_delete=models.CASCADE)
    person = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.person} - {self.date.date}"