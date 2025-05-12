from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Weather, PredictWeather, Subscriber
from .serializers import WeatherSerializer, PredictWeatherSerializer, SubscriberSerializer



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
            weather_data = Weather.objects.filter(province=province).order_by('time')
            # print(weather_data)
            serialize = WeatherSerializer(weather_data, many=True)
            # print(serialize)
            return Response(serialize.data[-8:], status=status.HTTP_200_OK)
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
            # if province=="TP Hồ Chí Minh":
            #     province = "TP. Hồ Chí Minh"
            if "Hồ Chí Minh" in province:
                province = "TP. Hồ Chí Minh"
            else:
                province = province.title()
            # print(province)
            predict_weather = PredictWeather.objects.filter(province=province).order_by('date')
            # print(predict_weather)
            serialize = PredictWeatherSerializer(predict_weather, many=True)
            # print(serialize)
            return Response(serialize.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# API lưu email và tỉnh của user
@api_view(['POST'])
def subscribe_weather(request):
    if request.method == 'POST':
        serializer = SubscriberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                subscriber = serializer.save()
                return Response({
                    'message': 'Đăng ký thành công! Bạn sẽ nhận được dự báo thời tiết hàng ngày vào lúc 7h sáng.',
                    'subscriber': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'message': 'Email này đã được đăng ký.',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API lưu email và tỉnh của user
@api_view(['POST'])
def SubscribeApiView(request):
    if request.method == 'POST':
        email = request.data.get('email')
        province = request.data.get('province')
        
        if not email or not province:
            return Response(
                {"error": "Email and province are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscriberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                subscriber = serializer.save()
                return Response({
                    'message': 'Đăng ký thành công! Bạn sẽ nhận được dự báo thời tiết hàng ngày vào lúc 7h sáng.',
                    'subscriber': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'message': 'Email này đã được đăng ký.',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)