from rest_framework import serializers
from .models import Weather, PredictWeather, Subscriber



class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = "__all__"


class PredictWeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictWeather
        fields = "__all__"

# ... existing serializers ...

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email', 'province']