---
description: Revisa el estado del flujo de n8n, verifica si corrió correctamente hoy, detecta errores y sugiere correcciones. Útil para diagnosticar problemas con el flujo de tendencias diarias.
---

1. Verifica que n8n esté corriendo en `http://localhost:5678`
2. Lee el archivo `modelo/flujo-tendencias-instagram.json` del repositorio
3. Revisa los logs de n8n buscando ejecuciones recientes del flujo "AI Instagram - Tendencias Diarias"
4. Reporta:
   - ¿Corrió hoy? ¿A qué hora?
   - ¿Hubo errores? ¿En qué nodo?
   - ¿El PDF fue generado y guardado?
   - ¿Se subió a Google Drive?
5. Si hay errores, explica la causa probable y los pasos para corregirlo
6. Si el flujo no corrió, ofrece ejecutarlo manualmente ahora
