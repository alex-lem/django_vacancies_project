from django import forms
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class Speciality(models.Model):

    title = models.CharField('Название', max_length=50, unique=True)
    code = models.CharField('Код', max_length=15, blank=True)
    picture = models.ImageField('Лого', upload_to=settings.MEDIA_SPECIALITY_IMAGE_DIR, blank=True)


class Company(models.Model):

    name = models.CharField('Название', max_length=50, unique=True)
    location = models.CharField('Город', max_length=15, blank=True)
    description = models.TextField('Информация о компании', blank=True)
    logo = models.ImageField('Логотип', upload_to=settings.MEDIA_COMPANY_IMAGE_DIR, blank=True)
    employee_count = models.PositiveIntegerField('Количество сотрудников', default=1)

    owner = models.OneToOneField(
        User,
        verbose_name='Владелец',
        on_delete=models.CASCADE,
        related_name='company',
        null=True,
        blank=True,
    )


class Vacancy(models.Model):

    title = models.CharField('Название вакансии', max_length=50)
    skills = models.CharField('Навыки', max_length=500, blank=True)
    published_at = models.DateField('Дата размещения', auto_now_add=True)
    text = models.TextField('Описание', blank=True)
    salary_min = models.IntegerField('Зарплата от', null=True, blank=True)
    salary_max = models.IntegerField('Зарплата до', null=True, blank=True)

    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        related_name='vacancies'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='vacancies'
    )


class Application(models.Model):

    written_username = models.CharField('Имя', max_length=30)
    written_phone = models.CharField('Телефон', max_length=15)
    written_cover_letter = models.TextField('Сопроводительное письмо')

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,

    )


class Resume(models.Model):

    STATUS = [
        ('NOT LOOKING FOR', 'Не ищу работу'),
        ('CONSIDERING OFFER', 'Рассматриваю предложения'),
        ('LOOKING FOR', 'Ищу работу'),
    ]
    GRADES = [
        ('TRAINEE', 'Стажер'),
        ('JUNIOR', 'Джуниор'),
        ('MIDDLE', 'Миддл'),
        ('SENIOR', 'Синьор'),
        ('TEAMLED', 'Лид'),
    ]

    name = models.CharField('Имя', max_length=50)
    surname = models.CharField('Фамилия', max_length=50)
    status = models.CharField(
        'Готовность к работе',
        max_length=100,
        choices=STATUS,
        default='LOOKING FOR')
    salary = models.PositiveIntegerField(
        'Вознаграждение', null=True, blank=True)
    grade = models.CharField(
        'Квалификация',
        max_length=50,
        choices=GRADES,
        default='JUNIOR')
    education = models.TextField('Образование', blank=True)
    experience = models.TextField('Опыт работы', blank=True)
    portfolio = models.URLField('Портфолио', max_length=250, blank=True)

    speciality = models.ForeignKey(
        Speciality,
        verbose_name='Специализация',
        on_delete=models.CASCADE,
        related_name='resume',
    )
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        null=True,
    )

# Модели для форм


SPECIALITIES = [
    ('frontend', 'Фронтенд разработка'),
    ('backend', 'Бэкенд разработка'),
    ('gamedev', 'Геймдев разработка'),
    ('devops', 'Девопс'),
    ('design', 'Дизайн'),
    ('products', 'Продукты'),
    ('management', 'Менеджмент'),
    ('testing', 'Тестирование'),
    ('ios', 'Разработка под iOS'),
    ('android', 'Разработка под Android'),
]
STATUS = [
    ('NOT LOOKING FOR', 'Не ищу работу'),
    ('CONSIDERING OFFER', 'Рассматриваю предложения'),
    ('LOOKING FOR', 'Ищу работу'),
]
GRADES = [
    ('TRAINEE', 'Стажер (trainee)'),
    ('JUNIOR', 'Младший (junior)'),
    ('MIDDLE', 'Средний (middle)'),
    ('SENIOR', 'Старший (senior)'),
    ('TEAMLEAD', 'Рукодитель (teamlead)'),
]


class ApplicationForm(forms.ModelForm):

    written_phone = forms.CharField(
        label='Ваш телефон',
        min_length=10,
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Application
        fields = ('written_username', 'written_phone', 'written_cover_letter')
        labels = {
            'written_username': 'Вас зовут',
            'written_cover_letter': 'Сопроводительное письмо',
        }
        widgets = {
            'written_username': forms.TextInput(attrs={'class': 'form-control'}),
            'written_cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': '8'}),
        }


class RegisterForm(UserCreationForm):

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class CompanyForm(forms.ModelForm):
    name = forms.CharField(
        label='Название компании',
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs=({'class': 'form-control'}))
    )
    logo = forms.FileField(
        label='Загрузить',
        required=False,
        widget=forms.FileInput(attrs={'class': 'custom-file-input'}),
    )
    employee_count = forms.IntegerField(
        label='Количество человек в компании',
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs=({'class': 'form-control'}))
    )
    location = forms.CharField(
        label='География',
        max_length=25,
        required=False,
        widget=forms.TextInput(attrs=({'class': 'form-control'}))
    )
    description = forms.CharField(
        label='Информация о компании',
        required=False,
        widget=forms.Textarea(attrs=({'class': 'form-control', 'style': 'color:#000;', 'row': '5'}))
    )

    class Meta:
        model = Company
        fields = ['name', 'logo', 'employee_count', 'location', 'description']


class VacancyForm(forms.ModelForm):
    title = forms.CharField(
        label='Название вакансии',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    speciality = forms.ChoiceField(
        label='Специализация',
        choices=SPECIALITIES,
        required=False,
        initial='backend',
        widget=forms.Select(attrs={'class': 'custom-select mr-sm-2'}),
    )
    salary_min = forms.IntegerField(
        label='Зарплата от',
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    salary_max = forms.IntegerField(
        label='Зарплата до',
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    skills = forms.CharField(
        label='Требуемые навыки',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'style': 'color:#000'}),
    )
    text = forms.CharField(
        label='Описание вакансии',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '13', 'style': 'color:#000'}),
    )

    class Meta:
        model = Vacancy
        fields = ['title', 'salary_min', 'salary_max', 'skills', 'text']


class ResumeForm(forms.ModelForm):

    name = forms.CharField(
        label='Имя',
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    surname = forms.CharField(
        label='Фамилия',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    status = forms.ChoiceField(
        label='Готовность к работе',
        choices=STATUS,
        required=False,
        initial='LOOKING FOR',
        widget=forms.Select(attrs={'class': 'custom-select mr-sm-2'}),
    )
    salary = forms.IntegerField(
        label='Вознаграждение',
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    speciality = forms.ChoiceField(
        label='Специализация',
        choices=SPECIALITIES,
        required=False,
        initial='backend',
        widget=forms.Select(attrs={'class': 'custom-select mr-sm-2'}),
    )
    grade = forms.ChoiceField(
        label='Квалификация',
        choices=GRADES,
        required=False,
        initial='MIDDLE',
        widget=forms.Select(attrs={'class': 'custom-select mr-sm-2'}),
    )
    education = forms.CharField(
        label='Образование',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control text-uppercase', 'rows': '5'}),
    )
    experience = forms.CharField(
        label='Опыт работы',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'style': 'color:#000;'}),
    )
    portfolio = forms.URLField(
        label='Ссылка на портфолио',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'http://anylink.github.io'}),
    )

    class Meta:
        model = Resume
        fields = ['name', 'surname', 'status', 'salary', 'grade', 'education', 'experience', 'portfolio']


class SearchVacanciesForm(forms.Form):

    search = forms.CharField(
        label='Найти работу',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control w-100',
                'placeholder': 'Найти работу или стажировку',
                'aria-label': 'Найти работу или стажировку',
                },
            )
    )
