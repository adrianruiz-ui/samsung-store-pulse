# Actualización semanal de Samsung Store Pulse

Corre cada domingo a las 9:00 pm (hora de Ciudad de México) en el Mac de Adrian, con Chrome abierto y la extensión Claude in Chrome activa. No cuesta nada: lee las fichas públicas de Google Maps desde el navegador de Adrian.

## Pasos

1. **Abrir Chrome.** Cargar las herramientas de Claude in Chrome en una sola búsqueda (tabs_context_mcp, tabs_create_mcp, navigate, computer, javascript_tool, browser_batch). Crear una pestaña nueva. No usar pestañas que Adrian tenga abiertas.
2. **Preparar.** Ir a `https://www.google.com/maps?hl=es` y ejecutar el contenido de `pipeline/clear.js` con javascript_tool.
3. **Recorrer las tiendas.** Para cada tienda de `pipeline/stores.json` que tenga `fid`, en el orden del archivo:
   - navegar a `https://www.google.com/maps/place/Samsung/data=!4m2!3m1!1s{fid}?hl=es`
   - esperar 4 segundos
   - ejecutar con javascript_tool: `await (CONTENIDO_DE_scraper.js)('{id}')`

   Agrupar 2 tiendas por llamada de browser_batch para no exceder el tiempo de espera. Si una tienda devuelve error o menos de 50 reseñas, reintentarla una vez al final.
4. **Exportar.** Ejecutar `pipeline/export.js`. Descarga `samsung_resenas_AAAA-MM-DD.json` en la carpeta Descargas del Mac. Si Chrome pide permiso de descarga, detenerse y avisar a Adrian; no aceptar permisos por él.
5. **Traer el archivo.** Pasarlo al entorno de trabajo con device_stage_files: `~/Downloads/samsung_resenas_AAAA-MM-DD.json`.
6. **Reconstruir.**
   - Agregar el repo `adrianruiz-ui/samsung-store-pulse` con acceso de escritura y clonarlo.
   - Ejecutar `python pipeline/build.py <archivo> --out data.json`. Necesita pandas y numpy.
   - Revisión mínima antes de publicar: al menos 60 tiendas y 15,000 reseñas. Si no se cumple, no publicar y avisar a Adrian qué tiendas fallaron.
7. **Publicar.**
   - Hacer commit de `data.json` y `pipeline/history/` con el autor `Adrian Ruiz <adrian.ruiz@ganem.mx>` y el mensaje `Actualización semanal AAAA-MM-DD`.
   - Hacer push a `main`. GitHub Pages se actualiza solo.
8. **Avisar.** Mandar a Adrian un resumen corto:
   - reseñas leídas y tiendas;
   - críticas de 6 meses, contra la semana anterior;
   - tiendas que entraron o salieron de "fuera de rango";
   - menciones nuevas de competencia sin clasificar;
   - tiendas que fallaron, si hubo.

## Notas

- `stores.json` tiene la ficha de Maps (`fid`) de las 64 tiendas activas. Si Samsung abre o cierra tiendas, se actualiza ahí.
- `curated.json` guarda las citas textuales de los territorios, la validación del clasificador y las reseñas de competencia clasificadas a mano. No cambia en la corrida semanal.
- `history/` guarda una copia comprimida de cada corrida para comparar semana contra semana.
