---
description: Gestiona el bot de Telegram que controla la PC. Sirve para iniciarlo, detenerlo, ver su estado, actualizar la configuración o diagnosticar problemas de conexión.
---

1. Detecta el estado actual del bot:
   - ¿Está corriendo? (busca proceso python con telegram-bot.py)
   - ¿Cuándo fue la última actividad?

2. Según lo que el usuario necesite:
   - **Iniciar**: `cd entorno-local && python telegram-bot.py`
   - **Detener**: mata el proceso del bot
   - **Reiniciar**: detiene y vuelve a iniciar
   - **Ver logs**: muestra las últimas líneas de actividad

3. Si hay problemas de conexión:
   - Verifica que el `.env` tenga las 3 variables correctas
   - Testea la conexión con la API de Telegram
   - Verifica la API key de Gemini

4. Si el usuario quiere actualizar la configuración:
   - Abre el `.env` para editar
   - Después de guardar, reinicia el bot automáticamente

5. Para dejar el bot corriendo siempre en segundo plano, ofrece configurarlo con PM2 o como servicio del sistema
