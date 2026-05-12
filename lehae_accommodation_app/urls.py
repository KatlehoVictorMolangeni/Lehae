from django.urls import path
from . import views

urlpatterns = [
    path('', views.Intro_loading, name='IntroLoading'),
    path('lehae/home/', views.Home, name='Home'),
    path('lehae/register/', views.Register, name='Register'),
    path('lehae/login/', views.Login, name='Login'),
    path('lehae/two-factor-auth/', views.TwoFactorAuth, name='TwoFactorAuth'),
    path('lehae/main/accommodation/', views.LehaeMainPage, name='LehaeMainPage'),
    path('lehae/myaccommodation/', views.ManageAccommodation, name='ManageAccommodation'),
    path('lehae/find-accommodations/', views.FindAccommodation, name='FindAccommodation'),
    path ('lehae/student/profile/', views.StudentProfile, name='StudentProfilePage'),
    
]