from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

handler404 = views.custom_handler404


urlpatterns = [
    path('', views.MainView.as_view(), name='index'),
    path('vacancies/', views.VacanciesView.as_view(), name='vacancies'),
    path('vacancies/search/', views.SearchVacanciesView.as_view(), name='vacancies_search'),
    path('vacancies/cat/<str:speciality>', views.VacanciesCategoryView.as_view(), name='specialization'),
    path('vacancies/<int:vacancy_id>/', views.VacancyDetailView.as_view(), name='vacancy'),
    path('vacancies/<int:vacancy_id>/send', views.SendedResumeView.as_view(), name='send_resume'),
    path('companies/<int:company_id>/', views.CompanyDetailView.as_view(), name='company'),
    path('myresume/', views.MyResumeView.as_view(), name='my_resume'),
    path('myresume/edit/', views.MyResumeEditView.as_view(), name='resume_edit'),
    path('mycompany/', views.MyCompanyView.as_view(), name='my_company'),
    path('mycompany/edit/', views.MyCompanyEditView.as_view(), name='company_edit'),
    path('mycompany/vacancies/', views.MyCompanyVacaniesView.as_view(), name='mycompany_vacancies'),
    path('mycompany/vacancies/<int:vacancy_id>', views.MyVacancyEditView.as_view(), name='my_vacancy_edit'),
    path('mycompany/vacancies/create/', views.MyCompanyCreateVacancy.as_view(), name='my_vacancy_create'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registration/', views.RegistrationView.as_view(), name='register'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
