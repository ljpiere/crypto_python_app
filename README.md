# crypto_python_app

1. Descripción del Proyecto:
Objetivo: Monitorear los precios de criptomonedas en tiempo real y generar alertas si el precio cumple con ciertas condiciones (por ejemplo, si sube o baja más de un cierto porcentaje).
Tecnologías: Python, RxPY, una API de criptomonedas (como CoinGecko o Binance).

2. Arquitectura General:
API de Criptomonedas: Obtener los precios en tiempo real.
Observables y Operadores: Utilizar RxPY para crear flujos de datos que representen los precios.
Alertas: Configurar condiciones para emitir alertas (por ejemplo, variaciones de precio).
Interfaz de Usuario: (Opcional) Una interfaz simple en la terminal o usando una biblioteca como Tkinter para mostrar la información en tiempo real.
