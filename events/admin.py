from django.contrib import admin

# Register your models here.
from .models import Venue,MyClubUser,Event

# admin.site.register(Event)
admin.site.register(MyClubUser)
# admin.site.register(Venue)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display=('name','address','phone')
    ordering=('name',)
    search_fields=('name','address')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields=(('name','venue'),'event_date','manager','attendees')
    list_display=('name','venue','event_date')

    ordering=('event_date',)
    list_filter=('event_date',)

    