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

@api_view(['GET'])
def GetUniqueProvinceApiView(request):
    if request.method == 'GET':
        try:
            unique_provinces = list(Weather.objects.values_list('province', flat=True).distinct("province"))
            return Response({"unique_provinces": list(unique_provinces)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def GetWeatherProvinceApiView(request):
    """
    API để lấy dữ liệu thời gần nhất tiết theo tỉnh 8 giờ gần nhât (mỗi giờ cách nhau 3 giờ)
    """
    if request.method == 'GET':
        province = request.GET.get('province', None)
        if not province:
            return Response({"error": "Missing 'province' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            weather_data = list(Weather.objects.filter(province=province).values(
                'id', 'province', 'time', 'temperature', 'temp_max', 'temp_min',
                'precipitation', 'windspeed_max', 'uv_index_max', 'sunshine_hours',
                'sundown_hours', 'weather_code'
            ))[-8:]
            return Response({"weather_data":weather_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
