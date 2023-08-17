from django.urls import path
from . import views

urlpatterns = [
    path('upload_many/', views.FileFieldFormView.as_view(), name='upload_many'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('upload/', views.upload_file, name='upload'),
    path('download/',views.download_page, name='download_page'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('', views.fileapp_home, name='fileapp_home'),
]