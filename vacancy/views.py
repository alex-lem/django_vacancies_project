from django.shortcuts import render
from django.http import Http404, HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.models import User
from django.contrib import messages

from vacancy.models import (
    Company,
    Speciality,
    Vacancy,
    Resume,
    Application,
    ApplicationForm,
    CompanyForm,
    RegisterForm,
    ResumeForm,
    VacancyForm,
    SearchVacanciesForm)


class MainView(TemplateView):
    form_class = SearchVacanciesForm
    initial = {'key': 'value'}

    def get(self, request):
        context = {}
        context['specialities'] = Speciality.objects.annotate(
            vacancies_count=Count('vacancies')
        ).all()
        context['compaines'] = Company.objects.annotate(
            vacancies_count=Count('vacancies')
        ).all()
        form = self.form_class(initial=self.initial)
        return render(request, 'vacancy/index.html', context={'compaines': context['compaines'],
                                                              'specialities': context['specialities'],
                                                              'form': form})


class VacanciesView(View):

    def get(self, request):
        context = {}
        context['vacancies'] = Vacancy.objects.select_related('company').all()

        return render(request, 'vacancy/vacancies.html', context={'vacancies': context['vacancies']})


class VacanciesCategoryView(View):

    def get(self, request, speciality):
        if not Vacancy.objects.filter(speciality__code=speciality).exists():
            raise Http404
        context = {}
        context['vacancies'] = Vacancy.objects.filter(speciality__code=speciality)

        return render(request, 'vacancy/vacancies.html', context={'vacancies': context['vacancies']})


class VacancyDetailView(View):
    form_class = ApplicationForm
    template_name = 'vacancy/vacancy.html'
    initial = {'key': 'value'}

    # Handle GET HTTP requests
    def get(self, request, vacancy_id, *args, **kwargs):
        if not Vacancy.objects.filter(id=vacancy_id).exists():
            raise Http404
        context = {}
        context['vacancy'] = Vacancy.objects.get(id=vacancy_id)
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form, 'vacancy': context['vacancy']})

    # Handle POST GTTP requests
    def post(self, request, vacancy_id, *args, **kwargs):
        context = {}
        context['vacancy'] = Vacancy.objects.get(id=vacancy_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            user = request.user if request.user.is_authenticated else None
            data.user = user
            data.vacancy = context['vacancy']
            data.username = form.cleaned_data['written_username']
            data.phone = form.cleaned_data['written_phone']
            data.cover = form.cleaned_data['written_cover_letter']
            data.save()
            return HttpResponseRedirect('send')

        return render(request, self.template_name, {'form': form, 'vacancy': context['vacancy']})


class SendedResumeView(TemplateView):
    template_name = 'vacancy/sent.html'


class CompanyDetailView(View):

    def get(self, request, company_id):
        if not Company.objects.filter(id=company_id).exists():
            raise Http404
        context = {}
        context['company'] = Company.objects.get(id=company_id)
        return render(request, 'vacancy/company.html', context={'company': context['company']})


class MyCompanyView(View):

    def get(self, request):
        user = request.user if request.user.is_authenticated else redirect('login')
        if not hasattr(user, 'company'):
            return render(request, 'vacancy/company-create.html')
        return redirect('company_edit')


class MyCompanyEditView(View):
    form_class = CompanyForm
    template_name = 'vacancy/company-edit.html'
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):

        user = request.user if request.user.is_authenticated else redirect('login')
        if hasattr(user, 'company'):
            company_init = {'name': self.request.user.company.name,
                            'employee_count': self.request.user.company.employee_count,
                            'location': self.request.user.company.location,
                            'description': self.request.user.company.description}
            form = self.form_class(initial=company_init)
            return render(request, self.template_name, context={'logo': self.request.user.company.logo, 'form': form})
        else:
            form = self.form_class(initial=self.initial)
            return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):

        user = request.user if request.user.is_authenticated else None
        if hasattr(user, 'company'):
            form = self.form_class(request.POST,
                                   request.FILES,
                                   instance=Company.objects.get(id=self.request.user.company.id))
            logo = self.request.user.company.logo
        else:
            form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.owner_id = user.id
            data.name = form.cleaned_data['name']
            if request.FILES:
                Company(logo=request.FILES['logo'])
            data.employee_count = form.cleaned_data['employee_count']
            data.location = form.cleaned_data['location']
            data.description = form.cleaned_data['description']
            data.save()
            messages.success(
                request, 'Информация о компании обновлена', extra_tags='info'
            )
            logo = Company.objects.get(owner=self.request.user.id).logo

        return render(request, self.template_name, {'form': form, 'logo': logo})


class MyCompanyVacaniesView(View):
    template_name = "vacancy/vacancy-list.html"

    def get(self, request, *args, **kwargs):

        if request.user.company.vacancies.exists():
            return render(request,
                          self.template_name,
                          context={'vacancies': Vacancy.objects.filter(company=request.user.company)})
        else:
            messages.success(
                request, 'У вас пока нет вакансий, но вы можете создать первую', extra_tags='info'
            )
            return render(request, self.template_name)


class MyVacancyEditView(View):
    template_name = "vacancy/vacancy-edit.html"
    form_class = VacancyForm
    initial = {'key': 'value'}

    def get(self, request, vacancy_id, *args, **kwargs):

        context = {}
        context['applications'] = (
            Application.objects.filter(vacancy__id=vacancy_id)
            .select_related('vacancy')
            .all()
        )
        if Vacancy.objects.filter(id=vacancy_id).exists():
            vacancy_get_data = Vacancy.objects.get(id=vacancy_id)
            vacancy_init = {'title': vacancy_get_data.title,
                            'speciality': vacancy_get_data.speciality,
                            'salary_min': vacancy_get_data.salary_min,
                            'salary_max': vacancy_get_data.salary_max,
                            'skills': vacancy_get_data.skills,
                            'text': vacancy_get_data.text}
            form = self.form_class(initial=vacancy_init)
            return render(request,
                          self.template_name,
                          context={'form': form, 'applications': context['applications']})
        else:
            form = self.form_class(initial=self.initial)
            return render(request,
                          self.template_name,
                          context={'form': form})

    def post(self, request, vacancy_id):

        if Vacancy.objects.filter(id=vacancy_id).exists():
            form = self.form_class(request.POST, instance=Vacancy.objects.get(id=vacancy_id))
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            data = form.save(commit=False)
            data.company = request.user.company
            speciality = form.cleaned_data['speciality']
            data.speciality = Speciality.objects.filter(code=speciality).first()
            data.title = form.cleaned_data['title']
            data.salary_min = form.cleaned_data['salary_min']
            data.salary_max = form.cleaned_data['salary_max']
            data.skills = form.cleaned_data['skills']
            data.text = form.cleaned_data['text']
            data.save()
            messages.success(
                request, 'Вакансия обновлена', extra_tags='info'
            )

        return render(request, self.template_name, {'form': form})


class MyCompanyCreateVacancy(View):
    template_name = "vacancy/vacancy-create.html"
    form_class = VacancyForm
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):

        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.company = request.user.company
            speciality = form.cleaned_data['speciality']
            data.speciality = Speciality.objects.filter(code=speciality).first()
            data.title = form.cleaned_data['title']
            data.salary_min = form.cleaned_data['salary_min']
            data.salary_max = form.cleaned_data['salary_max']
            data.skills = form.cleaned_data['skills']
            data.text = form.cleaned_data['text']
            data.save()

            messages.success(
                request, 'Вакансия добавлена', extra_tags='info'
            )

        return render(request, self.template_name, {'form': form})


class LoginView(LoginView):
    template_name = 'vacancy/login.html'
    redirect_authenticated_user = True


class LogoutView(LogoutView):
    pass


class RegistrationView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'vacancy/register.html'

    def get_success_url(self):
        return reverse('login')

    def get(self, request, *args, **kwargs):
        self.object = None
        if request.user.is_authenticated:
            return redirect('/')
        return super().get(request, *args, **kwargs)


class MyResumeView(View):

    def get(self, request, *args, **kwargs):

        user = request.user if request.user.is_authenticated else None
        if not hasattr(user, 'resume'):
            return render(request, 'vacancy/resume-create.html')
        return redirect('resume_edit')


class MyResumeEditView(View):
    template_name = 'vacancy/resume-edit.html'
    form_class = ResumeForm
    initial = {'key': 'value'}

    def get(self, request, *args, **kwargs):

        user = request.user if request.user.is_authenticated else redirect('login')
        if hasattr(user, 'resume'):
            company_init = {'name': self.request.user.resume.name,
                            'surname': self.request.user.resume.surname,
                            'status': self.request.user.resume.status,
                            'salary': self.request.user.resume.salary,
                            'speciality': self.request.user.resume.speciality,
                            'grade': self.request.user.resume.grade,
                            'education': self.request.user.resume.education,
                            'experience': self.request.user.resume.experience,
                            'portfolio': self.request.user.resume.portfolio}
            form = self.form_class(initial=company_init)
            return render(request, self.template_name, context={'form': form})
        else:
            form = self.form_class(initial=self.initial)
            return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):

        user = request.user if request.user.is_authenticated else None
        if hasattr(user, 'resume'):
            form = self.form_class(request.POST, instance=Resume.objects.get(id=self.request.user.id))
        else:
            form = self.form_class(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = user
            data.name = form.cleaned_data['name']
            data.surname = form.cleaned_data['surname']
            data.status = form.cleaned_data['status']
            data.salary = form.cleaned_data['salary']
            speciality = form.cleaned_data['speciality']
            data.speciality = Speciality.objects.filter(code=speciality).first()
            data.grade = form.cleaned_data['grade']
            data.education = form.cleaned_data['education']
            data.experience = form.cleaned_data['experience']
            data.portfolio = form.cleaned_data['portfolio']
            data.save()
            messages.success(
                request, 'Ваше резюме обновлено!', extra_tags='info'
            )
        return render(request, self.template_name, {'form': form})


class SearchVacanciesView(ListView):
    template_name = "vacancy/vacancies.html"
    context_object_name = 'vacancies'

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(**kwargs)
        context['title'] = 'Найдено вакансий'
        return context

    def get_queryset(self):

        querystring = self.request.GET.get('search')
        return (
            Vacancy.objects.filter(
                Q(title__icontains=querystring)
                | Q(skills__icontains=querystring)
                | Q(text__icontains=querystring),
            )
            .select_related('company')
            .all()
        )


def custom_handler404(request, exception):
    return HttpResponseNotFound('Ой, страница не найдена!')


def custom_handler505(request, exception):
    return HttpResponseServerError('Ой, сервер поломался!')
