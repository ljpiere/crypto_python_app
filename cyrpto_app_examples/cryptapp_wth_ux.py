import rx
from rx import operators as ops
import requests
import time

# Función para obtener precios de criptomonedas
def get_crypto_prices():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple&vs_currencies=usd')
        data = response.json()
        print(f"Data Received: {data}")  # Log de datos recibidos de la API
        
        return {
            'BTC': data.get('bitcoin', {}).get('usd', 0),
            'ETH': data.get('ethereum', {}).get('usd', 0),
            'XRP': data.get('ripple', {}).get('usd', 0)
        }
    except Exception as e:
        print(f"Error al obtener precios: {e}")
        return {'BTC': 0, 'ETH': 0, 'XRP': 0}

# Fuente de datos reactiva (observable)
prices_stream = rx.interval(2.0).pipe(
    ops.map(lambda _: get_crypto_prices()),  # Obtención de datos de la API cada 2 segundos
    ops.distinct_until_changed(),            # Emitir solo si hay un cambio en los datos
)

# Procesamiento y salida
prices_stream.pipe(
    ops.flat_map(lambda prices: rx.from_([prices])), # Convertir dict a flujo
    ops.map(lambda prices: {k: v for k, v in prices.items() if v > 100}),  # Filtrar precios mayores a 100 USD
    ops.map(lambda prices: f"Filtered Prices: {prices}")
).subscribe(
    on_next=lambda x: print(x),
    on_error=lambda e: print(f"Error: {e}"),
    on_completed=lambda: print("Completed!")
)

# Mantener la aplicación en ejecución
while True:
    time.sleep(1)
