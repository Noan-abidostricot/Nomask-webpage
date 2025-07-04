from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Candidate, Condition, Experience, Attribute, Company, JobOffer

admin.site.register(User)
admin.site.register(Candidate)
admin.site.register(Experience)
admin.site.register(Attribute)
admin.site.register(Condition)
admin.site.register(Company)
admin.site.register(JobOffer)