# AlcolEnri Web v5 — plataforma central

La web y los clientes `.exe` utilizan el mismo PostgreSQL mediante Django y `/api/sync/`.

## URL objetivo

`https://alcolenri.onrender.com`

La URL será válida cuando el servicio sea creado en Render con el nombre `alcolenri`. Si Render asigna otro nombre por disponibilidad, usa la URL asignada por Render y ponla también en `Desktop/configuracion_web.json`.

## Superadmin

- Usuario: `maligui`
- Contraseña: `contrasena7649`

## Acceso de profesores y estudiantes

Los profesores y estudiantes acceden con el mismo código único que utilizan en el `.exe`. El servidor central crea/vincula automáticamente su usuario web al sincronizar la persona.

## Notas del profesor

Siete evaluaciones:

- 1ª Evaluación
- 2ª Evaluación
- 3ª Evaluación
- 4ª Evaluación
- 5ª Evaluación
- Evaluación Final
- Recuperación

El profesor puede crear, actualizar, publicar y eliminar notas, incluso después de publicarlas.

## Asistencia

El profesor puede crear, actualizar, publicar y eliminar registros de asistencia y corregirlos después de su publicación.

## Alojamiento gratuito recomendado

Para mantener los datos fuera de un disco efímero de Render, el paquete está preparado para usar Render Free como servidor web y un PostgreSQL gratuito externo, por ejemplo Supabase Free, mediante `DATABASE_URL`.

No existe una garantía de alojamiento gratuito ilimitado/permanente. Los proveedores gratuitos actuales imponen límites de uso, suspensión por inactividad o caducidad de bases de datos. Consulta `DEPLOY_RENDER.md`.
