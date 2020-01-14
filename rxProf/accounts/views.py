from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.urls import reverse_lazy
from django.views import generic
from .models import User
from search.models import LikeList, Meeting, Freetime
from django.contrib.auth import login, logout
#from search.views import searchView
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.views import LoginView
from datetime import datetime as dt
# Create your views here.
def redirectLogin(request):
    if request.user.is_authenticated:
        return redirect("search:search")
    else:
        return redirect("accounts:login")
        
def redirectRegister(request):
    if request.user.is_authenticated:
        return redirect("search:search")
    else:
        return redirect("accounts:register")

class Register(generic.CreateView):
    
    form_class = RegisterForm
    template_name = 'register.html'
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            return redirect("search:search")
        user = form.save()
        login(self.request, user)
        #if user.userstatus = 0:
        return redirect("search:search") #redirect to index for now, but later redirect to settings if user is prof
        
def customLogout(request):
    logout(request)
    return redirect("search:search")
    
class Settings(generic.list.ListView):
    template_name = 'settings.html'
    model=User
    def get(self, request):
        conv = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        freetimes = [Freetime.objects.filter( Q(prof = self.request.user.get_username()) & Q(weekday = daynum) ) for daynum in conv.values()]
        for i in range(len(freetimes)):
            if not freetimes[i].exists():
                freetimes[i] = None
        compilation = []
        for i in range(len(weekdays)):
            compilation.append([])
            if freetimes[i] is not None:
                for freetime in freetimes[i]:
                    compilation[i] = [freetime.starttime, freetime.endtime, self.request.user.get_username(), freetime.id]
        days = {}
        for i in range(len(weekdays)):
            days[weekdays[i]] = compilation[i]
        return render(self.request, 'settings.html', {"days":days})
        
    def post(self, request):
        if self.request.user.is_authenticated and self.request.user.userstatus == 1:
            if 'personalinfo' in self.request.POST:
                newfirst = self.request.POST.get('firstname')
                newlast = self.request.POST.get('lastname')
                newemail = self.request.POST.get('email')
                newpass = self.request.POST.get('newpass')
                if self.request.user.check_password(self.request.POST.get('curpass')):
                    self.request.user.firstname = newfirst
                    self.request.user.lastname = newlast
                    if self.request.user.email != newemail:
                        object_list = LikeList.objects.filter(
                            Q(prof=self.request.user.email)
                        )
                        for like in object_list:
                            like.prof=newemail
                            like.save()
                    self.request.user.email = newemail
                    
                    if newpass is not None and len(newpass) > 0:
                        self.request.user.set_password(newpass)
                    self.request.user.save()
                    login(request, self.request.user)
                    messages.info(self.request, "Password changed!")
                else:
                    messages.info(self.request, "Incorrect password!")
                return redirect("accounts:settings")
            if 'addtime' in self.request.POST:
                conv = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
                newweekday = conv[self.request.POST.get('weekday')]
                newstart = dt.strptime(self.request.POST.get('starttime'), "%H:%M").time()
                newend = dt.strptime(self.request.POST.get('endtime'), "%H:%M").time()
                newtimeslot = Freetime(prof = self.request.user.get_username(), starttime = newstart, endtime = newend, weekday = newweekday)
                freetime = Freetime.objects.filter(
                    Q(weekday=newweekday) & Q(prof=self.request.user.get_username())
                )
                if freetime.exists():
                    messages.info(self.request, "There is already a timeslot for the specified weekday!")
                    return redirect("accounts:settings")
                elif newtimeslot.starttime > newtimeslot.endtime:
                    messages.info(self.request, "The start time is after the end time!")
                    return redirect("accounts:settings")
                else:
                    newtimeslot.save()
                    messages.info(self.request, "Successfully created timeslot!")
                    return redirect("accounts:settings")
            if 'deletetime' in self.request.POST:
                if self.request.POST.get('meeting') is not None:
                    meetingid = int(self.request.POST.get('meeting'))
                    findmeeting = Freetime.objects.filter( Q(id=meetingid) )
                    for meeting in findmeeting:
                        meeting.delete()
                        messages.info(self.request, "Successfully deleted timeslot!")
                        return redirect("accounts:settings")
                messages.info(self.request, "Could not delete timeslot!")
                return redirect("accounts:settings")
        else:
            return redirect("search:search")