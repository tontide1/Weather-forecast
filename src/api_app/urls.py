from django.urls import path

from . import views, views


app_name = 'api_app'
urlpatterns = [
    # API ENDPOINT
    path('getdata/', views.GetWeatherApiView, name='get-data'),
    
]