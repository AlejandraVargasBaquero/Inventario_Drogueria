# Plan de operación y mantenimiento

Sistema de inventario de la Droguería San Rafael. Es una aplicación local de un solo usuario (ADR-001) y no usa modelos de IA en producción, así que no hay MLOps. Lo que se opera es la aplicación y su base SQLite.

## Qué se vigila

| Qué | Cómo se ve | Qué hacer |
|---|---|---|
| La aplicación responde | La pantalla «Por pedir» abre. El job `imagen` del pipeline hace la misma comprobación con `curl` | Revisar la consola o `docker logs inventario` |
| Errores 500 | Flask los escribe en la consola con su traza (así se encontró el D-01) | Reproducir con el caso mínimo, abrir un reporte en `docs/defectos/` y escribir la prueba en rojo antes de corregir |
| Datos que no cuadran | El conteo físico de cajas no coincide con «Inventario» | Revisar los lotes de ese medicamento y su fecha de vencimiento |
| Vulnerabilidades | `pip-audit -r requirements.txt` | Una vez al mes y antes de cada versión; actualizar la versión fijada y correr el pipeline |

## Copias de seguridad

- La base es un solo archivo. Copia diaria al cierre a una memoria USB, con la fecha en el nombre (`inventario_2026-11-27.sqlite3`). Se guardan las últimas 30.
- En Docker: `docker cp inventario:/datos/inventario.sqlite3 respaldo/inventario_AAAA-MM-DD.sqlite3`.
- Una vez al mes se prueba restaurar una copia en otra carpeta y abrir la aplicación con ella. Una copia que nunca se restauró no está probada.

## Mantenimiento

- Cada cambio entra por una rama y un pull request. Solo se integra con el pipeline en verde.
- Las dependencias tienen versión fijada. Se actualizan una por una, con el pipeline como red de seguridad.
- Pendientes conocidos: usuarios y roles (por ahora la aplicación es local), dar de baja lotes vencidos (HU-06), servidor de producción si algún día se publica y la pregunta P-12 para el cliente.

## Si la IA dejara de estar disponible

El código usa solo Flask y la librería estándar, tiene 122 pruebas y cada regla está escrita en el contrato de HU-05 del README. Cualquier cambio se puede hacer a mano y las pruebas dicen si algo se rompió.
