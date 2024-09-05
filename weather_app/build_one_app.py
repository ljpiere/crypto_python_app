import time
import requests
import rx
from rx import operators as ops

# Función para obtener el precio de una criptomoneda desde la API de CoinGecko
def get_crypto_price(crypto_id="bitcoin", currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta una excepción para códigos de estado HTTP no exitosos
        data = response.json()
        # Verifica que la respuesta contiene los datos esperados
        if crypto_id in data and currency in data[crypto_id]:
            return data[crypto_id][currency]
        else:
            raise ValueError(f"Invalid response structure: {data}")
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching price: {e}")
        return None  # Retorna None si hay un error

# Observable que emite el precio de la criptomoneda en intervalos regulares
def price_stream(crypto_id="bitcoin", currency="usd", interval=5):
    return rx.interval(interval).pipe(
        ops.map(lambda _: get_crypto_price(crypto_id, currency)),
        ops.filter(lambda price: price is not None),  # Filtra valores None
        ops.distinct_until_changed()  # Emite solo si el precio cambia
    )

# Función que crea un observable para generar alertas basadas en cambios de precio
def price_alerts(crypto_id="bitcoin", currency="usd", interval=5, threshold=5):
    stream = price_stream(crypto_id, currency, interval)

    return stream.pipe(
        ops.buffer_with_count(2, 1),  # Agrupa los valores de 2 en 2
        ops.map(lambda prices: ((prices[1] - prices[0]) / prices[0]) * 100),  # Calcula el cambio porcentual
        ops.filter(lambda change: abs(change) >= threshold)  # Filtra si el cambio excede el umbral
    )

# Función principal que ejecuta el sistema de alertas
def run_alert_system(crypto_id="bitcoin", currency="usd", interval=10, threshold=1):
    alerts = price_alerts(crypto_id, currency, interval, threshold)

    # Suscripción al observable para recibir alertas
    alerts.subscribe(
        on_next=lambda change: print(f"Alert! Price changed by {change:.2f}%"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Monitoring completed")
    )

    # Mantener el programa en ejecución indefinidamente
    while True:
        time.sleep(1)

# Ejecución del sistema de monitoreo
if __name__ == "__main__":
    run_alert_system(crypto_id="bitcoin", currency="usd", interval=10, threshold=1)
