from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from datetime import datetime



class Venue(models.Model):
    name=models.CharField('Venue Name',max_length=120)
    address=models.CharField(max_length=120)
    zip_code=models.CharField('Zip Code',max_length=120)
    phone=models.CharField('Contact Phone',max_length=120)
    web=models.URLField('Website Address')
    email_address=models.EmailField('Email Address')
    owner=models.IntegerField('Venue Owner',blank=False,default=1)
    venue_image=models.ImageField(null=True,blank=True,upload_to='images/')
    def __str__(self) -> str:
        return self.name
    
class MyClubUser(models.Model):
    first_name=models.CharField(max_length=120)
    last_name=models.CharField(max_length=120)
    email=models.EmailField('User Email Address')

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Event(models.Model):
    name=models.CharField('Event Name' ,max_length=120)
    event_date=models.DateTimeField('Event Date')
    venue=models.ForeignKey(Venue,blank=True,null=True,on_delete=models.CASCADE)
    manager=models.ForeignKey(User,blank=True,null=True,on_delete=models.SET_NULL)
    description=models.TextField(blank=True)
    attendees=models.ManyToManyField(MyClubUser,blank=True)

    def __str__(self) -> str:
        return self.name
    
    @property
    def Days_till(self):
        today=datetime.today()
        days_till=self.event_date.date()-today.date()
        
        return str(days_till).split(',',1)[0]