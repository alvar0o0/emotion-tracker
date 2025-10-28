"Jules, quiero construir un 'tracker de emociones'.

Necesito 3 componentes, en python:

1. Una API de backend (usa FastAPI en Python):
   - Debe tener un solo endpoint /log.
   - Este endpoint debe aceptar un POST con un JSON, algo como {"emotion": "alegria", "level": 5}.
   - Debe guardar esta información y un timestamp en una base de datos simple (usa SQLite).

3. Un bot de Telegram (usa python-telegram-bot):
   - Cuando le envíe un emoji (ej. 😊), el bot debe "traducir" ese emoji a una emoción (ej. "alegria").
   - Luego, debe llamar al endpoint /log de mi API para registrarlo.

5. Un dashboard web simple (usa Streamlit):
   - Debe leer la base de datos SQLite.
   - Debe mostrar un gráfico de barras con el conteo de cada emoción.
   - Debe mostrar una línea de tiempo de las emociones registradas hoy.

Por favor, genera la estructura de archivos y el código base para estos tres servicios."
