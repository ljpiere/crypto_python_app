import time
import requests
import rx
from rx import operators as ops
import os
from dotenv import load_dotenv
load_dotenv()

# Función para obtener la temperatura actual de una ciudad desde la API de OpenWeatherMap
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta una excepción para códigos de estado HTTP no exitosos
        data = response.json()
        if "main" in data and "temp" in data["main"]:
            return data["main"]["temp"]
        else:
            raise ValueError(f"Invalid response structure: {data}")
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching weather data: {e}")
        return None  # Retorna None si hay un error

# Observable que emite la temperatura en intervalos regulares
def temperature_stream(city, api_key, interval=5):
    return rx.interval(interval).pipe(
        ops.map(lambda _: get_weather_data(city, api_key)),
        ops.filter(lambda temp: temp is not None),  # Filtra valores None
        ops.distinct_until_changed()  # Emite solo si la temperatura cambia
    )

# Función principal que ejecuta el sistema de alertas
def run_weather_alert_system(city, api_key, interval=10):
    stream = temperature_stream(city, api_key, interval)

    # Suscripción al observable para recibir alertas al mínimo cambio
    stream.subscribe(
        on_next=lambda temp: print(f"Alert! Temperature changed to {temp:.2f}°C"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Monitoring completed")
    )

    # Mantener el programa en ejecución indefinidamente
    while True:
        time.sleep(1)

# Ejecución del sistema de monitoreo
if __name__ == "__main__":
    city = "London,uk"  # Puedes cambiar esta ciudad a la que desees monitorear
    api_key = os.getenv('API_TOKEN')  # Reemplaza con tu API Key de OpenWeatherMap
    run_weather_alert_system(city, api_key, interval=10)
