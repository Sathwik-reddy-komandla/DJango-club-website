from django.shortcuts import render,redirect

import calendar
from calendar import HTMLCalendar
from datetime import datetime

# Create your views here.
from .models import *
from .forms import VenueForm,EventForm,AdminEventForm
from django.http import HttpResponseRedirect

from django.http import HttpResponse,FileResponse
import csv

from reportlab.pdfgen import canvas
import io
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


# Pagination
from django.core.paginator import Paginator
from django.contrib import messages

def venue_pdf(request):
    #  CReate ByteStream buffer
    buf=io.BytesIO()
    c=canvas.Canvas(buf,pagesize=letter,bottomup=0)
    # create a Text Object
    textob=c.beginText()
    textob.setTextOrigin(inch,inch)
    textob.setFont('Helvetica',14)
    # Add TExt
    venues=Venue.objects.all()
    for venue in venues:
        textob.textLine(venue.name)
        textob.textLine(venue.address)
        textob.textLine(venue.zip_code)
        textob.textLine(venue.phone)
        textob.textLine(venue.web)
        textob.textLine(venue.email_address)    
        textob.textLine(' ')
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)    
    return FileResponse(buf,as_attachment=True,filename='venue.pdf')   


def venue_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=venues.csv'
    # Create CSV Writer
    writer=csv.writer(response)
    venues=Venue.objects.all()
    # Add column labels
    writer.writerow(['Venue Name','Address','ZipCode','Phone','Web Address','Email'])
    for venue in venues:
        writer.writerow([venue.name,venue.address,venue.zip_code,venue.phone,venue.web,venue.email_address])        
    return response   


def venue_text(request):
    response=HttpResponse(content_type='text/plain')
    response['Content-Disposition']='attachment; filename=venues.txt'
    venues=Venue.objects.all()
    lines=[]
    for venue in venues:
        lines.append(f'{venue.name}\n')
        lines.append(f'{venue.address}\n')
        lines.append(f'{venue.zip_code}\n')
        lines.append(f'{venue.phone}\n')
        lines.append(f'{venue.web}\n')
        lines.append(f'{venue.email_address}\n\n')
    response.writelines(lines)
    return response


def delete_event(request,event_id):
    event=Event.objects.get(id=event_id)
    if request.user==event.manager:
        event.delete()
        messages.success(request,"Event Deleted")
    else:
        messages.success(request,"You aren't authorized to delete this Event")
    return redirect('list_events')


def delete_venue(request,venue_id):
    venue=Venue.objects.get(id=venue_id)
    venue.delete()
    return redirect('list_venues')

def my_events(request):
    if request.user.is_authenticated:
        me=request.user.id
        events=Event.objects.filter(attendees=me)
        return render(request,'events/myevents.html',{'me':me,'events':events})

    else:
        messages.success(request,"You aren't Authorized To View")
    return redirect('home')


def update_event(request,event_id):
    event=Event.objects.get(id=event_id)
    if request.user.is_superuser:
        form=AdminEventForm(request.POST or None,instance=event)
    else:
        form=EventForm(request.POST or None,instance=event)

    if form.is_valid():
        form.save()
        return redirect('list_events')
    return render(request,'events/update_event.html',{'event':event,'form':form})


def search_events(request):
    if request.method=='POST':
        searched=request.POST['searched']
        events=Event.objects.filter(name__contains=searched)
        return render(request,'events/search_events.html',{'searched':searched,'events':events})
    else:
        return render(request,'events/search_events.html',{})


def add_event(request):
    submitted=False
    if request.method=='POST':
        if request.user.is_superuser:
            form=AdminEventForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted')
        else:
            form=EventForm(request.POST)
            if form.is_valid():
                event=form.save(commit=False)
                event.manager=request.user.id
                event.save()
                return HttpResponseRedirect('/add_event?submitted')
    else:
        if request.user.is_superuser:
            form=AdminEventForm
        else:
            form=EventForm
        if 'submitted' in request.GET:
            submitted=True
    return render(request,'events/add_event.html',{'form':form,'submitted':submitted})





def update_venue(request,venue_id):
    venue=Venue.objects.get(id=venue_id)
    form=VenueForm(request.POST or None,request.FILES or None,instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list_venues')
    return render(request,'events/update_venue.html',{'venue':venue,'form':form})





def search_venues(request):
    if request.method=='POST':
        searched=request.POST['searched']
        venues=Venue.objects.filter(name__contains=searched)
        return render(request,'events/search_venues.html',{'searched':searched,'venues':venues})


def show_venue(request,venue_id):
    venue=Venue.objects.get(id=venue_id)
    user_id=venue.owner
    venue_owner=User.objects.get(id=user_id)
    return render(request,'events/show_venue.html',{'venue':venue,'venue_owner':venue_owner})



def list_venues(request):
    # venues_list=Venue.objects.all().order_by('name')
    # Set Up Pagination
    p=Paginator(Venue.objects.all(),5)
    page=request.GET.get('page')
    venues=p.get_page(page)
    nums='a'*p.num_pages

    return render(request,'events/venues.html',{'venues':venues,'nums':nums})


def add_venue(request):
    submitted=False
    if request.method=='POST':
        form=VenueForm(request.POST,request.FILES)
        if form.is_valid():
            venue=form.save(commit=False)
            venue.owner=request.user.id
            venue.save()
            return HttpResponseRedirect('/add_venue?submitted')
    else:
        form=VenueForm
        if 'submitted' in request.GET:
            submitted=True
    return render(request,'events/add_venue.html',{'form':form,'submitted':submitted})



def all_events(request):
    event_list=Event.objects.all().order_by('event_date')
    return render(request,'events/event_list.html',{'event_list':event_list})



def home(request,year=datetime.now().year,month=datetime.now().strftime('%B')):

    month=month.capitalize()
    month_number=list(calendar.month_name).index(month)

    cal=HTMLCalendar().formatmonth(year,int(month_number))

    now=datetime.now()
    current_year=now.year

    event_list=Event.objects.filter(
        event_date__year=year,
        event_date__month=month_number
    )

    time=now.strftime('%I:%M %p')
    return render(request,'events/home.html',{
        'year':year,
        'month':month,
        'month_number':month_number,
        'cal':cal,
        'current_year':current_year,
        'time':time,
        'event_list':event_list
    })


    