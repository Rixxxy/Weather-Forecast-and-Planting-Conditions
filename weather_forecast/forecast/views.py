from django.shortcuts import render
import requests
from datetime import datetime

API_KEY = 'Your_API_Key'
BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast'

plants = [
    {'name': 'Coconut', 'temp_range': (24, 30), 'humidity_min': 60, 'rain_max': 5, 'wind_max': 15},
    {'name': 'Banana', 'temp_range': (20, 28), 'humidity_min': 70, 'rain_max': 10, 'wind_max': 15},
    {'name': 'Pepper', 'temp_range': (18, 26), 'humidity_min': 60, 'rain_max': 5, 'wind_max': 10},
    {'name': 'Tomato', 'temp_range': (18, 30), 'humidity_min': 60, 'rain_max': 6, 'wind_max': 12},
    {'name': 'Potato', 'temp_range': (10, 25), 'humidity_min': 70, 'rain_max': 7, 'wind_max': 10},
    {'name': 'Carrot', 'temp_range': (10, 24), 'humidity_min': 60, 'rain_max': 5, 'wind_max': 10},
    {'name': 'Mango', 'temp_range': (24, 32), 'humidity_min': 50, 'rain_max': 8, 'wind_max': 10},
    {'name': 'Wheat', 'temp_range': (12, 25), 'humidity_min': 55, 'rain_max': 5, 'wind_max': 15},
    {'name': 'Rice', 'temp_range': (20, 35), 'humidity_min': 70, 'rain_max': 10, 'wind_max': 10},
    {'name': 'Corn', 'temp_range': (18, 27), 'humidity_min': 65, 'rain_max': 6, 'wind_max': 12},
    {'name': 'Soybean', 'temp_range': (15, 30), 'humidity_min': 60, 'rain_max': 7, 'wind_max': 10},
    {'name': 'Onion', 'temp_range': (13, 24), 'humidity_min': 60, 'rain_max': 6, 'wind_max': 12},
    {'name': 'Spinach', 'temp_range': (5, 24), 'humidity_min': 70, 'rain_max': 5, 'wind_max': 10},
    {'name': 'Pumpkin', 'temp_range': (18, 30), 'humidity_min': 60, 'rain_max': 7, 'wind_max': 15},
    {'name': 'Chili', 'temp_range': (20, 30), 'humidity_min': 60, 'rain_max': 8, 'wind_max': 15},
    {'name': 'Garlic', 'temp_range': (12, 24), 'humidity_min': 50, 'rain_max': 4, 'wind_max': 12},
    {'name': 'Lettuce', 'temp_range': (15, 25), 'humidity_min': 60, 'rain_max': 6, 'wind_max': 8},
    {'name': 'Cauliflower', 'temp_range': (15, 22), 'humidity_min': 65, 'rain_max': 5, 'wind_max': 10},
    {'name': 'Cabbage', 'temp_range': (10, 20), 'humidity_min': 70, 'rain_max': 7, 'wind_max': 12},
    {'name': 'Strawberry', 'temp_range': (13, 24), 'humidity_min': 60, 'rain_max': 6, 'wind_max': 8},
]
def get_weather_data(city):
    url = f"{BASE_URL}?q={city}&cnt=40&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def check_planting_conditions(forecast_item, plant):
    temp = forecast_item['temp']
    rain = forecast_item.get('rain', 0)
    wind_speed = forecast_item['wind_speed']
    humidity = forecast_item['humidity']

    temp_ok = plant['temp_range'][0] <= temp <= plant['temp_range'][1]
    humidity_ok = humidity >= plant['humidity_min']
    rain_ok = rain <= plant['rain_max']
    wind_ok = wind_speed <= plant['wind_max']

    if not temp_ok:
        return False, f"Temperature is not ideal ({temp}°C)."
    if not humidity_ok:
        return False, f"Humidity is too low ({humidity}%)."
    if not rain_ok:
        return False, f"Too much rain ({rain} mm)."
    if not wind_ok:
        return False, f"Wind speed is too high ({wind_speed} km/h)."

    return True, "All conditions are good."

def home(request):
    city = request.GET.get('city', 'Mangaluru')  # Default to 'Mangaluru' if no city is provided
    weather_data = get_weather_data(city)

    if weather_data is None or 'list' not in weather_data:
        context = {'error': 'Could not retrieve weather data. Please try again later.'}
        return render(request, 'home.html', context)

    forecast = []
    best_planting_days = {}
    dates = set()

    for item in weather_data['list']:
        date = datetime.utcfromtimestamp(item['dt']).strftime('%Y-%m-%d')
        time = datetime.utcfromtimestamp(item['dt']).strftime('%H:%M:%S')

        if date not in dates and "12:00:00" in time:
            temp = item['main']['temp']
            weather_description = item['weather'][0]['description']
            wind_speed = item['wind']['speed']
            wind_deg = item['wind']['deg']
            rain = item.get('rain', {}).get('3h', 0)
            humidity = item['main'].get('humidity', 0)
            cloud_cover = item['clouds'].get('all', 0)
            visibility = item.get('visibility', 10000)

            soil_moisture = item.get('soil_moisture', 30)  # Mock value
            sunlight_hours = item.get('sunlight_hours', 8)  # Mock value
            soil_ph = item.get('soil_ph', 6.5)  # Mock value
            uv_index = item.get('uv_index', 6)  # Mock value
            aqi = item.get('aqi', 50)  # Mock value

            forecast_item = {
                'date': date,
                'temp': temp,
                'weather': weather_description,
                'wind_speed': wind_speed,
                'wind_deg': wind_deg,
                'rain': rain,
                'humidity': humidity,
                'cloud_cover': cloud_cover,
                'soil_moisture': soil_moisture,
                'sunlight_hours': sunlight_hours,
                'soil_ph': soil_ph,
                'uv_index': uv_index,
                'aqi': aqi,
                'visibility': visibility,
            }
            forecast.append(forecast_item)

            for plant in plants:
                can_plant, reason = check_planting_conditions(forecast_item, plant)
                if can_plant and plant['name'] not in best_planting_days:
                    best_planting_days[plant['name']] = {
                        'date': date,
                        'conditions': forecast_item
                    }
                elif not can_plant and plant['name'] not in best_planting_days:
                    best_planting_days[plant['name']] = {
                        'date': None,
                        'reason': reason
                    }

            dates.add(date)

        if len(forecast) >= 7:
            break

    context = {
        'city': city,
        'forecast': forecast,
        'best_planting_days': best_planting_days
    }

    return render(request, 'home.html', context)
