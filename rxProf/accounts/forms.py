from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from urllib.request import urlopen
from urllib.error import HTTPError
from lxml import etree, html
from lxml.builder import E
from .models import User
from django.db import transaction

class RegisterForm(UserCreationForm):
    """password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)"""

    class Meta:
        model = User
        fields = ('email', )

    """def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2"""
	
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        query = user.email
        revisedquery = query.split('.')
        revisedquery = revisedquery[:-1]
        revisedquery[-1] = revisedquery[-1].split('@')[0]
        newquery = '%20'.join(revisedquery)
        search = urlopen('https://adam.cc.sunysb.edu:8443/acc/new-dirsearch.cgi?name_string='+newquery+'&status=Any')
        tree = etree.parse(search, etree.HTMLParser())
        root = tree.find('//body')
        person = root.find('div[@class="record"]')
        #print("person:", person)
        #user.userstatus = 0
        if person is not None:
            #teacher
            fullname = person.find('div[@class="name"]').find('h2[@class="title"]').text.split('  ')
            user.firstname = fullname[0]
            user.lastname = fullname[1]
            user.userstatus = 1

        else:
            #student
            user.userstatus = 0
            user.firstname = "None"
            user.lastname = "None"
        user.save()
        return user