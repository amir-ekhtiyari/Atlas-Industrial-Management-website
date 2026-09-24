from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('company/', views.about, name='about'),
    path('technologies/', views.technology_list, name='technology_list'),
    path('technologies/<str:slug>/', views.technology_detail, name='technology_detail'),
    path('industries/', views.industry_list, name='industry_list'),
    path('industries/<str:slug>/', views.industry_detail, name='industry_detail'),
    path('quality/', views.quality, name='quality'),
]
