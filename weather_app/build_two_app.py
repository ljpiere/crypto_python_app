import time
import requests
import rx
from rx import operators as ops

# Función para obtener la temperatura actual de una ciudad desde la API de OpenWeatherMap
def get_weather_data(city, api_key):
    #url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},uk&APPID={api_key}"
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

# Función que crea un observable para generar alertas basadas en cambios de temperatura
def temperature_alerts(city, api_key, interval=5, threshold=2):
    stream = temperature_stream(city, api_key, interval)

    return stream.pipe(
        ops.buffer_with_count(2, 1),  # Agrupa los valores de 2 en 2
        ops.map(lambda temps: temps[1] - temps[0]),  # Calcula el cambio de temperatura
        ops.filter(lambda change: abs(change) >= threshold)  # Filtra si el cambio excede el umbral
    )

# Función principal que ejecuta el sistema de alertas
def run_weather_alert_system(city, api_key, interval=10, threshold=2):
    alerts = temperature_alerts(city, api_key, interval, threshold)

    # Suscripción al observable para recibir alertas
    alerts.subscribe(
        on_next=lambda change: print(f"Alert! Temperature changed by {change:.2f}°C"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Monitoring completed")
    )

    # Mantener el programa en ejecución indefinidamente
    while True:
        time.sleep(1)

# Ejecución del sistema de monitoreo
if __name__ == "__main__":
    city = "London"  # Puedes cambiar esta ciudad a la que desees monitorear
    api_key = "27f5bcecbd3e9de978893a962b3ef0d2"  # Reemplaza con tu API Key de OpenWeatherMap
    run_weather_alert_system(city, api_key, interval=2, threshold=0.1)
