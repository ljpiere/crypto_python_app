import rx
from rx import operators as ops
import requests
import time
import tkinter as tk
from threading import Thread

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

# Configuración de la Interfaz Gráfica
class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Price Monitor")
        
        # Etiqueta para mostrar los precios filtrados
        self.label = tk.Label(root, text="Initializing...", font=("Helvetica", 16))
        self.label.pack(pady=20)
        
        # Botón para salir de la aplicación
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=20)
        
        # Iniciar el flujo de datos en un hilo separado
        self.start_data_stream()

    def start_data_stream(self):
        def run():
            # Fuente de datos reactiva (observable)
            prices_stream = rx.interval(7.0).pipe(
                ops.map(lambda _: get_crypto_prices()),  # Obtención de datos de la API cada 2 segundos
                ops.distinct_until_changed(),            # Emitir solo si hay un cambio en los datos
            )
            
            # Procesamiento y salida en la interfaz gráfica
            prices_stream.pipe(
                ops.flat_map(lambda prices: rx.from_([prices])), # Convertir dict a flujo
                ops.map(lambda prices: {k: v for k, v in prices.items() if v > 100}),  # Filtrar precios mayores a 100 USD
                ops.map(lambda prices: f"Filtered Prices: {prices}")
            ).subscribe(
                on_next=lambda x: self.update_label(x),
                on_error=lambda e: print(f"Error: {e}"),
                on_completed=lambda: print("Completed!")
            )
        
        # Iniciar el flujo de datos en un hilo separado para no bloquear la GUI
        Thread(target=run).start()

    def update_label(self, text):
        self.label.config(text=text)

# Ejecución de la Interfaz Gráfica
if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
