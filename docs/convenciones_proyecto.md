# Convenciones del proyecto

## Gestión de rutas
Todas las rutas deben obtenerse desde `config.yaml` mediante la función 
`get_config()` ubicada en `src/config/config_loader.py`.

No se permite hardcodear rutas dentro de los scripts.
Si una ruta no existe en el config, debe añadirse allí antes de usarla.


