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

# Función para actualizar la interfaz con los datos filtrados
def update_ui(filtered_prices):
    text_box.delete(1.0, tk.END)  # Limpiar el contenido anterior
    text_box.insert(tk.END, f"Filtered Prices: {filtered_prices}\n")

# Configuración de Tkinter (interfaz gráfica)
root = tk.Tk()
root.title("Criptomonedas Reactivas")

# Crear un cuadro de texto para mostrar los precios
text_box = tk.Text(root, height=10, width=50)
text_box.pack()

# Hilo para ejecutar el flujo reactivo sin bloquear la interfaz
def reactive_prices():
    prices_stream = rx.interval(2.0).pipe(
        ops.map(lambda _: get_crypto_prices()),  # Obtención de datos de la API cada 2 segundos
        ops.distinct_until_changed(),            # Emitir solo si hay un cambio en los datos
    )
    
    prices_stream.pipe(
        ops.flat_map(lambda prices: rx.from_([prices])),  # Convertir dict a flujo
        ops.map(lambda prices: {k: v for k, v in prices.items() if v > 100}),  # Filtrar precios mayores a 100 USD
    ).subscribe(
        on_next=lambda filtered_prices: update_ui(filtered_prices),  # Actualizar la interfaz con los precios filtrados
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Completed!")
    )

# Ejecutar el flujo reactivo en un hilo aparte para no bloquear la interfaz
thread = Thread(target=reactive_prices)
thread.daemon = True
thread.start()

# Ejecutar la aplicación Tkinter
root.mainloop()
