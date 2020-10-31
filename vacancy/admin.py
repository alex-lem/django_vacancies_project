from django.contrib import admin
from .models import Company, Speciality, Vacancy, Application, Resume

# Register your models here.
admin.site.register(Company)
admin.site.register(Speciality)
admin.site.register(Vacancy)
admin.site.register(Application)
admin.site.register(Resume)
