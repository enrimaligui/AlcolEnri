# Despliegue de AlcolEnri

## Arquitectura

`Navegador + .exe -> Django central -> PostgreSQL`

La opción gratuita práctica para probar y mantener el proyecto con coste cero es:

- Web Django: Render Free.
- PostgreSQL: Supabase Free.

Render Free permite desplegar Django, pero el servicio web se duerme después de 15 minutos sin tráfico. El PostgreSQL gratuito de Render caduca a los 30 días, por lo que **no** se usa como base principal en este paquete. Supabase Free proporciona PostgreSQL gratuito, aunque puede pausar un proyecto tras un periodo de baja actividad.

## Pasos

1. Crea un proyecto gratuito de PostgreSQL en Supabase.
2. Copia la cadena de conexión PostgreSQL.
3. Sube `Web/` a GitHub.
4. En Render crea un Web Service y conecta el repositorio.
5. Usa `build.sh` como Build Command y el `startCommand` de `render.yaml`.
6. Configura `DATABASE_URL` con la cadena de Supabase.
7. Configura `ALCOLENRI_SYNC_KEY` con la misma clave que usa `Desktop/configuracion_web.json`.
8. Despliega.
9. Comprueba `/api/health/`.
10. Abre la URL pública de Render.

## Cuenta inicial

`maligui` / `contrasena7649`

## URL que se pretende usar

`https://alcolenri.onrender.com`

El nombre debe estar disponible en Render. Si no lo está, Render asignará otro subdominio; esa URL debe copiarse a `Desktop/configuracion_web.json`.
