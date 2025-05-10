from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Weather, PredictWeather
from .serializers import WeatherSerializer, PredictWeatherSerializer



# API lấy dữ liệu thời tiết từ DB
@api_view(['GET'])
def GetWeatherApiView(request):
    if request.method == 'GET':
        weather = Weather.objects.all()
        serialize = WeatherSerializer(weather, many=True)
        # print('-'*100)
        # print(serialize.data)
        return Response(serialize.data, status=status.HTTP_200_OK)


# API lấy tên các tỉnh
@api_view(['GET'])
def GetUniqueProvinceApiView(request):
    if request.method == 'GET':
        try:
            unique_provinces = list(Weather.objects.values_list('province', flat=True).distinct("province"))
            return Response({"unique_provinces": list(unique_provinces)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API lấy tỉnh theo tên tỉnh/thành phố
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
        

# API lấy dữ liệu dự đoán từ DB
@api_view(['GET'])
def GetPredictWeatherApiView(request):
    if request.method == 'GET':
        province = request.GET.get('province', None)
        if not province:
            return Response({"error": "Missing 'province' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        try:
<<<<<<< HEAD
            # if province=="TP Hồ Chí Minh":
            #     province = "TP. Hồ Chí Minh"
            if "Hồ Chí Minh" in province:
                province = "TP. Hồ Chí Minh"
            else:
                province = province.title()
            # print(province)
            predict_weather = PredictWeather.objects.filter(province=province)
            # print(predict_weather)
=======
            predict_weather = PredictWeather.objects.filter(province=province)
            print(predict_weather)
>>>>>>> 2013ee418b6a7b3aa3c2cd4bddfd5409a5053ceb
            serialize = PredictWeatherSerializer(predict_weather, many=True)
            # print(serialize)
            return Response(serialize.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)