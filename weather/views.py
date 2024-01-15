from django.shortcuts import render
from requests import request
import json

key = "b5ad8f226b5d8e97c5522e5b3fb1da72"
weather_url = "http://api.openweathermap.org/data/2.5/weather"
forecast_url = "http://api.openweathermap.org/data/2.5/forecast"

weather_conditions = {
    'Clear': {'icon': 'wi-day-sunny', 'description': 'Clear sky'},
    'Clouds': {'icon': 'wi-cloudy', 'description': 'Cloudy'},
    'Rain': {'icon': 'wi-rain', 'description': 'Rain'},
    'Snow': {'icon': 'wi-snow', 'description': 'Snow'},
}

def get_weather_report(city):
    params = {
        "q": city,
        "appid": key
    }
    response = request(method="GET", url=weather_url, params=params)
    if response.status_code != 200:
        return None
    return response.json()

def get_page_context(weather_data, city):
    weather_code = weather_data['weather'][0]['main']
    weather_info = weather_conditions.get(weather_code, {'icon': 'wi-na', 'description': 'Not available'})

    return {
        'city_name': city,
        'temp': (weather_data['main']['temp'] - 273.15).__round__(2),
        'weather_icon': weather_info['icon'],
        'weather_description': weather_info['description'],
        'weather_code': weather_code,
        'wind_speed': weather_data['wind']['speed'],
        'humidity': weather_data['main']['humidity'],
        'pressure': weather_data['main']['pressure'],
        'visibility': weather_data['visibility'],
        'latitude': weather_data['coord']['lat'],
        'longitude': weather_data['coord']['lon'],
    }

def get_weather_forecast(city):
    params = {
        "q": city,
        "appid": key,
        "units": "metric"
    }
    response = request("GET", forecast_url, params=params)
    forecast_data = response.json()

    # Adăugăm icoanele și descrierea stării meteo pentru fiecare element din prognoză
    for item in forecast_data['list']:
        weather_code = item['weather'][0]['main']
        weather_info = weather_conditions.get(weather_code, {'icon': 'wi-na', 'description': 'Not available'})
        item['weather'][0]['icon'] = weather_info['icon']
        item['weather'][0]['description'] = weather_info['description']

    return forecast_data

def index(request):
    context = {'error_message': None}
    if 'city' in request.GET:
        city = request.GET['city']
        weather_data = get_weather_report(city)

        if weather_data:
            # Verificăm dacă datele meteo sunt complete
            if weather_data.get('main') and weather_data.get('weather'):
                forecast_data = get_weather_forecast(city)
                context.update(get_page_context(weather_data, city))
                context['forecast'] = forecast_data
            else:
                context['error_message'] = "City not found or there's a problem with the API."
        else:
            context['error_message'] = "City not found or there's a problem with the API."

    return render(request, 'index.html', context)