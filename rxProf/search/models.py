from django.db import models
from accounts.models import User
from django.core.exceptions import ValidationError
# Create your models here.


    
class LikeList(models.Model):
    user = models.CharField(max_length=60)
    prof = models.CharField(max_length=60)
    
class Meeting(models.Model):
    user = models.CharField(max_length=60)
    prof = models.CharField(max_length=60)
    starttime = models.TimeField()
    endtime = models.TimeField()
    day = models.DateField()
    
    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:    #edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): #innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end: #outer limits
            overlap = True
 
        return overlap
    
    def clean(self):
        if self.endtime <= self.starttime:
            raise ValidationError('Meeting end time must be after start time')
 
        events = Meeting.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if self.check_overlap(event.starttime, event.endtime, self.starttime, self.endtime):
                    raise ValidationError(
                        'There is an overlap with another meeting: ' + str(event.day) + ', ' + str(
                            event.starttime) + '-' + str(event.endtime))

class Freetime(models.Model):
    prof = models.CharField(max_length=60)
    starttime = models.TimeField()
    endtime = models.TimeField()
    weekday = models.IntegerField()