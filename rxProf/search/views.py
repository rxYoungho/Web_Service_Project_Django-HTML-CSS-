
from .forms import SearchForm
from django.views import generic
# Create your views here.
from django.shortcuts import render_to_response, redirect, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from accounts.models import User
from django.db.models import Q
from django.contrib import messages
from . import models
from datetime import datetime as dt
import datetime
from django.core.exceptions import ValidationError
class SearchResultsView(generic.list.ListView):
    model = User
    template_name = 'search.html'
    def get_queryset(self): # new
        query = self.request.GET.get('q')
        if query is not None:
            object_list = User.objects.filter(
                (Q(email__icontains=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query) | Q(officeloc__icontains=query)) & Q(userstatus=1)
            )
        else:
            object_list = User.objects.none()
        object_list.order_by('-rating')
        return object_list

class ProfDataView(generic.list.ListView):
    model = User
    template_name = 'profinfo.html'
    def get_queryset(self): # new
        query = self.request.GET.get('email')
        if query is not None:
            object_list = User.objects.filter(
                Q(email__icontains=query)
            )
        return object_list
    def post(self, request):
        likequery = self.request.POST.get('likebtn')
        emailsave = self.request.GET.get('email')
        next = self.request.POST.get('next', '/')
        if likequery is not None:
            created = models.LikeList.objects.filter(
                Q(user=self.request.user.get_username()) & Q(prof=emailsave)
            )
            object_list = User.objects.filter(
                Q(email__icontains=emailsave)
            )
            for i in created:
                for curprof in object_list:
                    curprof.rating -= 1
                    curprof.save()
                i.delete()
                return redirect('/profinfo/?email='+emailsave)
            newlike = models.LikeList(user=self.request.user.get_username(), prof=emailsave)
            newlike.save()
            for curprof in object_list:
                curprof.rating += 1
                curprof.save()
            return redirect('/profinfo/?email='+emailsave)
                
class CalendarView(generic.list.ListView):
    model = User
    template_name = 'calendar.html'
    def get(self, request):
        query = self.request.GET.get('email')
        daylist = [datetime.date.today() + datetime.timedelta(s) for s in range(7)]
        #Get free time for prof 
        
        freetimes = models.Freetime.objects.filter(
            Q(prof=query)
        )
        #get meetings for prof
        meetings = models.Meeting.objects.filter(
            Q(prof=query)
        )
        
        freetimesperday = [freetimes.filter(Q(weekday=day.weekday())) for day in daylist]
        for i in range(len(freetimesperday)):
            if not freetimesperday[i].exists():
                freetimesperday[i] = None
        
        meetingsperday = [meetings.filter(Q(day=day_l)) for day_l in daylist]
        for i in range(len(meetingsperday)):
            if not meetingsperday[i].exists():
                meetingsperday[i] = None
        
        compilation = []
        for i in range(len(freetimesperday)):
            compilation.append([[], []])
            if freetimesperday[i] is not None:
                for freetime in freetimesperday[i]:
                    compilation[i][0] = [freetime.starttime, freetime.endtime]
            if meetingsperday[i] is not None:
                for meeting in meetingsperday[i]:
                    compilation[i][1].append([meeting.starttime, meeting.endtime, meeting.user, meeting.id, meeting.prof])
                compilation[i][1] = sorted(compilation[i][1], key=lambda x: x[0])
                    
        #return them in days dict in this format:
        #days = {day1 : [[FreetimeStart, FreetimeEnd], [[Meeting1Start, Meeting1End], ...]], ...}
        days = {}
        for i in range(len(compilation)):
            days[daylist[i]] = compilation[i]
        #print(days)
        #return render_to_response('calendar.html',{'days':days})
        return render(self.request, 'calendar.html', {"days":days})
    
    def post(self, request):
        if 'addmeeting' in self.request.POST:
            newdate = dt.strptime(self.request.POST.get('date'), "%b. %d, %Y")
            newstart = dt.strptime(self.request.POST.get('starttime'), "%H:%M").time()
            newend = dt.strptime(self.request.POST.get('endtime'), "%H:%M").time()
            newmeeting = models.Meeting(user = self.request.user.get_username(), prof = self.request.GET.get('email'), starttime = newstart, endtime = newend, day = newdate)
            try:
                newmeeting.clean()
            except ValidationError:
                messages.info(self.request, "This meeting overlaps with another!")
                return HttpResponseRedirect("?email="+self.request.GET.get('email'))
            freetime = models.Freetime.objects.filter(
                Q(weekday=newdate.weekday()) & Q(prof=self.request.GET.get('email'))
            )
            if freetime.exists():
                for slot in freetime:
                    if newmeeting.starttime < slot.starttime or newmeeting.endtime > slot.endtime:
                        messages.info(self.request, "This meeting takes up more time than is available!")
                        return HttpResponseRedirect("?email="+self.request.GET.get('email'))
                newmeeting.save()
                messages.info(self.request, "Successfully created meeting!")
                return HttpResponseRedirect("?email="+self.request.GET.get('email'))
            else:
                messages.info(self.request, "There are no free timeslots for the specified day!")
                return HttpResponseRedirect("?email="+self.request.GET.get('email'))
        if 'deletemeeting' in self.request.POST:
            if self.request.POST.get('meeting') is not None:
                meetingid = int(self.request.POST.get('meeting'))
                findmeeting = models.Meeting.objects.filter( Q(id=meetingid) )
                for meeting in findmeeting:
                    meeting.delete()
                    messages.info(self.request, "Successfully deleted meeting!")
                    return HttpResponseRedirect("?email="+self.request.GET.get('email'))
            messages.info(self.request, "Could not delete meeting!")
            return HttpResponseRedirect("?email="+self.request.GET.get('email'))
        