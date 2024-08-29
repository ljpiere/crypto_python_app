# Programación Reactiva: Monitor de Precios de Criptomonedas en Tiempo Real

## Descripción de la prueba

Esta prueba implementa una aplicación sencilla para monitorear precios de criptomonedas en tiempo real utilizando un enfoque de programación reactiva. La prueba incluye la obtención de datos de una API de criptomonedas y la visualización de esos datos en una interfaz gráfica construida con Tkinter.

## Objetivo(s) de la prueba

1. **Demostrar el uso de la programación reactiva** en la actualización continua de datos en tiempo real.
2. **Implementar una interfaz gráfica** simple para la visualización de los precios de criptomonedas.
3. **Probar la capacidad de respuesta y robustez** del sistema frente a fallas de conexión o datos incorrectos.

## Pasos implementados para llevar a cabo la prueba

1. **Obtención de datos de la API**:
   - Se realiza una solicitud GET a la API de CoinGecko para obtener los precios actuales de Bitcoin (BTC), Ethereum (ETH) y Ripple (XRP) en USD.
   - Los datos obtenidos se procesan y se transforman en un diccionario con los precios específicos de cada criptomoneda.
   - En caso de error durante la solicitud, se maneja la excepción y se devuelven valores predeterminados.

2. **Configuración de la interfaz gráfica**:
   - Se crea una ventana utilizando Tkinter con un título y una etiqueta inicial.
   - Se añade un botón para cerrar la aplicación.

3. **Flujo de datos reactivo**:
   - Se inicia un flujo de datos utilizando `rx.interval` que emite eventos a intervalos regulares (7 segundos).
   - Cada evento desencadena una solicitud a la API para obtener los precios de las criptomonedas.
   - Los precios obtenidos se comparan con los datos previos y, si han cambiado, se actualizan en la interfaz gráfica.
   - Todo este proceso se realiza en un hilo separado para evitar bloquear la interfaz gráfica.

## Tecnologías usadas en la prueba

- **Lenguaje de programación**: Python
- **Librerías**:
  - **`rxpy`**: Para implementar programación reactiva.
  - **`requests`**: Para realizar solicitudes HTTP a la API de CoinGecko.
  - **`tkinter`**: Para construir la interfaz gráfica de usuario.
  - **`threading`**: Para manejar la ejecución en segundo plano de tareas largas sin bloquear la interfaz gráfica.

## Explicación del código

## Importaciones

```python
import rx
from rx import operators as ops
import requests
import time
import tkinter as tk
from threading import Thread
```

- `rx`: Biblioteca para programación reactiva
- `operators as ops`: Operadores de RxPY para manipular flujos de datos
- `requests`: Para realizar solicitudes HTTP
- `time`: Para funciones relacionadas con el tiempo (no se usa en este código)
- `tkinter as tk`: Para crear la interfaz gráfica
- `Thread`: Para ejecutar tareas en hilos separados

## Función para obtener precios de criptomonedas

```python
def get_crypto_prices():
    """Función para obtener precios de criptomonedas

    Returns:
        dictionary: Data de consulta de la API.
    """
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
```

- Realiza una solicitud GET a la API de CoinGecko
- Convierte la respuesta a JSON
- Imprime los datos recibidos para depuración
- Devuelve un diccionario con los precios de BTC, ETH y XRP
- En caso de error, imprime el error y devuelve precios en cero

## Clase CryptoApp

```python
class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Price Monitor")
        
        # Creamos una etiqeuta
        self.label = tk.Label(root, text="Initializing...", font=("Helvetica", 16))
        self.label.pack(pady=20)
        
        # Un botón para terminar ejecución de la APP
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=20)
        
        # Iniciar el flujo de datos en un hilo separado
        self.start_data_stream()
```

- Inicializa la ventana principal de la aplicación
- Crea una etiqueta para mostrar los precios
- Crea un botón para salir de la aplicación
- Inicia el flujo de datos en un hilo separado

## Método start_data_stream

```python
def start_data_stream(self):
    def run():
        # Fuente de datos reactiva (observable)
        prices_stream = rx.interval(7.0).pipe(
            ops.map(lambda _: get_crypto_prices()),  # Podemos cambiar tiempo entre solicites
            ops.distinct_until_changed(),            # Lanzar alerta si encuentra cambios
        )
            
        # Procesamiento y salida en la interfaz gráfica
        prices_stream.pipe(
            ops.flat_map(lambda prices: rx.from_([prices])), # Convertir dict a flujo
            ops.map(lambda prices: {k: v for k, v in prices.items() if v > 100}),  #Filtramos precios a mayor 100 USD
            ops.map(lambda prices: f"Filtered Prices: {prices}")
        ).subscribe(
            on_next=lambda x: self.update_label(x),
            on_error=lambda e: print(f"Error: {e}"),
            on_completed=lambda: print("Completed!")
        )
        
    # Iniciamos el hilo de ejecuciond e la API separado de la interfaz
    # para evitar problemas de rendimiento
    Thread(target=run).start()
```

- Crea un flujo de datos que obtiene precios cada 7 segundos
- Filtra los precios mayores a 100 USD
- Actualiza la etiqueta con los precios filtrados
- Ejecuta todo esto en un hilo separado para no bloquear la GUI

## Método update_label

```python
def update_label(self, text):
    self.label.config(text=text)
```

- Actualiza el texto de la etiqueta con los nuevos precios

## Ejecución principal

```python
if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
```

- Crea la ventana principal de Tkinter
- Inicializa la aplicación CryptoApp
- Inicia el bucle principal de la interfaz gráfica

## Resultados

- La aplicación logra actualizar los precios de las criptomonedas en la interfaz gráfica en intervalos de 7 segundos.
- Los cambios en los precios se reflejan correctamente cuando estos difieren de los valores anteriores.
- La interfaz gráfica sigue siendo responsiva durante la ejecución, permitiendo cerrar la aplicación sin problemas.

## Conclusiones

- **Eficacia de la programación reactiva**: El uso de programación reactiva simplificó la actualización continua de los precios de criptomonedas y mejoró la eficiencia de la aplicación.
- **Robustez frente a errores**: La aplicación maneja adecuadamente los errores de red y las respuestas inesperadas de la API, mostrando valores predeterminados en caso de fallos.
- **Interfaz gráfica simple pero efectiva**: Aunque sencilla, la interfaz gráfica proporciona una visualización clara y oportuna de los datos.



