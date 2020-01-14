from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

# Create your models here.
class NewUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        if not password:
            raise ValueError('Users must have a password')

        
        
        
			
        user = self.model(
            email=self.normalize_email(email),
			userstatus = userstatus,
			firstname = firstname,
			lastname = lastname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    userstatus = models.IntegerField()
    #1 is prof, 0 is student
    objects=NewUserManager()
    #prof exclusive
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    email = models.CharField(max_length=60, unique=True)
    officeloc = models.CharField(max_length=30, blank=True, default='')
    rating = models.IntegerField(blank=True, default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.
    
    
class Course(models.Model):
    prof = models.ForeignKey(User, on_delete=models.CASCADE)
    courseid = models.CharField(max_length=30)

class FreeHour(models.Model):
    prof = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()

class TakenHour(models.Model):
    prof = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()