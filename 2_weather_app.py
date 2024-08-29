import time
import requests
import rx
from rx import operators as ops
import os
from dotenv import load_dotenv
load_dotenv()

def get_weather_data(city, api_key):
    """Función para obtener la temperatura actual de una ciudad desde la API de OpenWeatherMap

    Args:
        city (string): Nombre de la ciudad
        api_key (string): Token de conexión a la API

    Raises:
        ValueError: Se crea una excepcion en caso de problemas de conexión a la API

    Returns:
        string: Temperatura al momento de realizar la peticion POST
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  #Levantamos una excepcion
        data = response.json()
        if "main" in data and "temp" in data["main"]:
            return data["main"]["temp"]
        else:
            raise ValueError(f"Invalid response structure: {data}")
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching weather data: {e}")
        return None  #Devolvemos NONE en caso de no recibir informacion

def temperature_stream(city, api_key, interval=5):
    """Observable que emite la temperatura en intervalos regulares

    Args:
        city (string): Nombre de la ciudad
        api_key (string): Token de conexión a la API
        interval (int, optional): Intervalos regulares de consulta a la API. Defaults to 5.

    Returns:
        string : Temp promedio de la ciudad a consultar
    """
    return rx.interval(interval).pipe(
        ops.map(lambda _: get_weather_data(city, api_key)),
        ops.filter(lambda temp: temp is not None),  # Filtra valores None
        ops.distinct_until_changed()  # El observable emite señal solo si hay cambio de temperatura
    )

def run_weather_alert_system(city, api_key, interval=10):
    """Función principal que ejecuta el sistema de alertas

    Args:
        city (string): Nombre de la ciudad
        api_key (string): Token de conexión a la API
        interval (int, optional): Intervalos regulares de ejecución. Defaults to 10.
    """
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
    city = "London,uk"  # Editar ciudad
    api_key = os.getenv('API_TOKEN')  # El token se carga como variable del sistema
    run_weather_alert_system(city, api_key, interval=10)
