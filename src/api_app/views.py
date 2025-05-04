# from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Weather
from .serializers import WeatherSerializer




@api_view(['GET'])
def GetWeatherApiView(request):
    if request.method == 'GET':
        weather = Weather.objects.all()
        serialize = WeatherSerializer(weather, many=True)
        # print('-'*100)
        # print(serialize.data)
        return Response(serialize.data, status=status.HTTP_200_OK)