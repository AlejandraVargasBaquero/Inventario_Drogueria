# Bitácora de uso de IA

Proyecto: Sistema de inventario para una droguería de barrio, con control de lotes y fechas de vencimiento
Estudiante: Alejandra Vargas Baquero
Funcionalidad: HU-05 Productos bajo el mínimo (`productos_por_pedir`). Semana 6: revisión de código y seguridad.
Asistente usado: GitHub Copilot (chat en VS Code, modo agente) en el taller de clase; Gemini (chat) para explicar y revisar el código de clase; Claude (chat) para la implementación y el refactor del proyecto. En la semana 6, Claude como revisor (chat) y como agente en la rama `agente/revision-semana6`.

> Parto del taller de clase, como lo permite la tarea: allí Copilot escribió las pruebas y la
> implementación de `productos_por_pedir` para la tienda del OVA 1. Las capturas están en el
> documento de actividades de clase de la semana 5.

## Entradas

### Entrada 1

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Reutilizar tal cual la implementación de clase que hizo Copilot (`r = [p for p in productos if p.existencias <= p.minimo]` con la validación de negativos), adaptada solo para sumar las cajas de los lotes de cada medicamento.
- **Decisión:** Rechazada
- **Por qué:** En la tienda cada producto tenía un solo número de existencias; en la droguería las existencias salen de los lotes y los vencidos no cuentan (HU-02, RNF-04). La versión de clase sumaba también las 12 cajas vencidas del L-0925, así que el acetaminofén salía con 15 cajas y no aparecía por pedir.
- **Verificación:** Corrí `python -m pytest` con esa versión: 8 fallaron y 6 pasaron. Fallaron, entre otras, `test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir` (`assert 0 == 1`) y `test_medicamento_con_todos_los_lotes_vencidos_aparece_con_cero` (`IndexError`).
- **Commit relacionado:** No se guardó; la versión que quedó es la de `Implementación de HU-05 productos por pedir (pruebas en verde)`.

### Entrada 2

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El contrato de clase (OVA 1) decía «existencias menores **o iguales** a su mínimo» y la implementación de Copilot usaba `<=`.
- **Decisión:** Rechazada
- **Por qué:** HU-05 dice «por debajo del mínimo». Con `<=`, la loratadina con 10 de 10 cajas aparecía por pedir. Lo dejé como menor estricto en el contrato (supuesto 3) y lo agregué como pregunta P-12 para el cliente.
- **Verificación:** `test_vigentes_iguales_al_minimo_no_aparece` y `test_lote_que_vence_hoy_todavia_cuenta_como_vigente` fallaban con `<=` y pasan con `<`.
- **Commit relacionado:** `Pruebas de HU-05 productos por pedir (en rojo)` y `Implementación de HU-05 productos por pedir (pruebas en verde)`.

### Entrada 3

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** En clase, Copilot definió `Producto` como un `Protocol` (tipado estructural) porque no encontró una clase `Producto` en el proyecto.
- **Decisión:** Aceptada con cambios
- **Por qué:** La idea de declarar los tipos sí sirve, pero en mi proyecto ya existen las entidades del modelo de datos de la semana 4. Usé `@dataclass(frozen=True)` para `Medicamento` y `Lote` con los mismos campos del modelo, y agregué `ProductoPorPedir` con la propiedad `texto` («3 de 10 cajas») que pide el criterio de HU-05. `frozen=True` impide cambiar los objetos recibidos.
- **Verificación:** Las pruebas importan los modelos desde `app/reglas/modelos.py`; `test_no_modifica_las_listas_recibidas` pasa.
- **Commit relacionado:** `Contrato de HU-05 en el README y estructura de la capa de reglas`.

### Entrada 4

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Actúa como desarrollador Python que trabaja con pruebas primero. Contexto: capa de reglas del sistema de inventario de una droguería (Python 3.13, pytest; Flask y SQLite según el ADR-001). Contrato: [pegué la sección Funcionalidad de la semana 5 del README]. Pruebas: [pegué tests/test_pedidos.py]. Tarea: escribe la implementación más simple que haga pasar las 14 pruebas. Formato: un bloque de código y una línea por cada supuesto que tomes. Restricciones: solo librería estándar; no cambies la firma ni las pruebas; no modifiques las listas recibidas.»
- **Decisión:** Aceptada
- **Por qué:** Cumple el contrato: valida el mínimo con el mensaje exacto del escenario 2, suma solo los lotes con `fecha_vencimiento >= hoy`, compara con `<` y devuelve una lista nueva ordenada. Leí cada línea antes de aceptarla y no agrega dependencias.
- **Verificación:** `python -m pytest -v`: 14 passed. Revisé que no tocara la carpeta `tests/`.
- **Commit relacionado:** `Implementación de HU-05 productos por pedir (pruebas en verde)`.

### Entrada 5

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Supuesto que Copilot dejó escrito en clase: «si varios productos tienen las mismas existencias, se conserva su orden de entrada».
- **Decisión:** Aceptada
- **Por qué:** Es el comportamiento de `sorted` en Python (es estable) y le sirve al dueño, que ve los medicamentos en el orden en que los registró. Lo pasé al contrato para que no quede como supuesto escondido.
- **Verificación:** Agregué `test_con_empate_conserva_el_orden_de_llegada` y pasa.
- **Commit relacionado:** `Pruebas de HU-05 productos por pedir (en rojo)`.

### Entrada 6

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Al revisar el código de clase, Gemini dijo que recorrer la lista dos veces (una para validar y otra para filtrar) era una «ineficiencia notable» y propuso hacer todo en una sola pasada.
- **Decisión:** Aceptada con cambios
- **Por qué:** La razón está exagerada: dos recorridos siguen siendo O(n) y el `sorted` del final pesa más. Pero en la droguería hay hasta 5.000 lotes (RNF-01), así que en `_cajas_vigentes_por_medicamento` sí valido y sumo cada lote en una sola pasada. Los medicamentos los valido aparte, en `_validar_minimos`, porque así se lee mejor y son pocos.
- **Verificación:** Las 14 pruebas pasan, incluidas las 3 de error, que comprueban que la validación sigue ocurriendo antes de devolver resultados.
- **Commit relacionado:** `Refactor de productos_por_pedir sin cambiar comportamiento`.

### Entrada 7

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Refactoriza esta función sin cambiar su comportamiento: nombres claros en lugar de v, r, l y m, el mensaje del mínimo en una constante, dividir la función larga y quitar la duplicación de v.get(m.id, 0). No toques las pruebas.»
- **Decisión:** Aceptada
- **Por qué:** Mejora la lectura sin cambiar lo que hace. Revisé que el refactor no agregara validaciones nuevas, porque eso sería un cambio de comportamiento mezclado con el refactor (lo que pasó en clase con `registrar_abono`, cuando se agregaron las validaciones de NaN e infinito en el mismo cambio).
- **Verificación:** `python -m pytest`: 14 passed. `git diff -- tests` vacío: las pruebas no se modificaron.
- **Commit relacionado:** `Refactor de productos_por_pedir sin cambiar comportamiento`.

## Entradas de la semana 6

### Entrada 8

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Segunda revisión con IA (Claude) con el prompt de la semana: «Actúa como revisor de código Python con experiencia en seguridad. Módulo: capa de reglas del inventario de una droguería [...]. Criterios: corrección y casos límite, diseño, legibilidad, pruebas y seguridad. Formato: tabla con archivo, línea, problema, severidad y confianza. No reescribas todo el código: separa los problemas seguros de las sospechas que habría que verificar.» Le pasé `pedidos.py`, `modelos.py` y `test_pedidos.py`.
- **Decisión:** Aceptada con cambios
- **Por qué:** De 6 hallazgos, 2 eran reales (tipos sin validar e ids repetidos), 1 es real pero queda pendiente (fechas `datetime`) y 3 eran falsos positivos (`sorted` inestable, XSS en una capa que no genera HTML y S101 en las pruebas). La IA no vio que `.gitignore` ignoraba `.env.example` ni que `pytest` no tenía versión fijada, porque esos archivos no estaban en el prompt; los encontré con la lista de la semana.
- **Verificación:** Comprobé cada hallazgo llamando a la función con los datos del caso (`"10"` lanzó `TypeError`; `True` devolvió «0 de True cajas»), con la documentación de `sorted` y con la prueba de empate. La tabla está en la sección 3 de `revision_seguridad.md`.
- **Commit relacionado:** `ead80c7` y `2cf950c`.

### Entrada 9

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Agente (Claude) con una instrucción delimitada. **Rol:** agente que trabaja en la rama `agente/revision-semana6`. **Contexto:** capa de reglas del inventario, ADR-001, contrato de HU-05 en el README. **Tarea:** corregir los hallazgos reales de la revisión, un commit por corrección, configurar ruff, completar los docstrings y el README con las 8 secciones. **Formato:** al terminar, lista de commits, pruebas agregadas y resultado de pytest y ruff. **Restricciones:** no modificar las pruebas existentes (solo agregar), solo librería estándar en `app/`, no instalar paquetes, no tocar `main`.
- **Decisión:** Aceptada después de revisar el diff
- **Por qué:** Hizo 8 commits pequeños, cada uno con un mensaje que dice qué corrige. Revisé que las validaciones nuevas tuvieran sus pruebas y que el refactor (`f27c7d8`) no cambiara el comportamiento.
- **Verificación:** `git diff main...agente/revision-semana6` revisado archivo por archivo; `git diff d1110d4 -- tests` solo tiene líneas agregadas; `python -m pytest`: 23 passed; `ruff check --select E,F,B,S .`: All checks passed! Integré la rama a `main` solo con las pruebas en verde.
- **Commit relacionado:** del `56374bc` al `973133c`.

### Entrada 10

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Corrección de H-03: validar con `isinstance(valor, int)` que el mínimo y la cantidad sean enteros.
- **Decisión:** Aceptada con cambios
- **Por qué:** `isinstance(True, int)` es `True` en Python porque `bool` es subclase de `int`, así que con eso solo un mínimo `True` seguía pasando. Se agregó `_es_entero`, que excluye los booleanos. Como la corrección cambia el comportamiento (antes `"10"` daba `TypeError` y ahora `ValueError` con mensaje), agregué pruebas nuevas en vez de cambiar las que existían.
- **Verificación:** Escribí primero las pruebas parametrizadas con `"10"`, `2.5`, `True` y `None`: fallaron (en rojo). Después de la corrección pasaron todas.
- **Commit relacionado:** `ead80c7`.

### Entrada 11

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** La IA sugirió validar también que `fecha_vencimiento` sea `date` y no `datetime`, en la misma rama.
- **Decisión:** Rechazada por ahora
- **Por qué:** Es real (comparar un `datetime` con un `date` lanza `TypeError`), pero hoy las fechas solo las crea el código. Cuando llegue la capa de datos, las fechas vendrán de SQLite como texto y la conversión se hará allí. Hacerlo ahora sería decidir sin saber cómo se guardarán. Queda en Pendientes del informe.
- **Verificación:** Reproduje el error con `Lote(1, "L", datetime(2027, 1, 1), 3)`.
- **Commit relacionado:** Ninguno (pendiente).

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 4 (entradas 4, 5, 7 y 9) |
| Aceptadas con cambios | 4 (entradas 3, 6, 8 y 10) |
| Rechazadas | 3 (entradas 1, 2 y 11) |

## Errores que atraparon las pruebas

Cuando probé la implementación de clase en el proyecto (entrada 1), 8 de las 14 pruebas
fallaron. El error principal: sumaba todas las cajas del medicamento, también las vencidas.
`test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir` esperaba el acetaminofén con
«3 de 10 cajas», pero la función contaba 12 vencidas + 3 vigentes = 15 y lo dejaba fuera de
la lista (`assert 0 == 1`). Es justo el problema del cliente: «En el Excel me salen 30 cajas
de acetaminofén, pero no sé cuántas de esas ya están vencidas». Lo corregí sumando solo los
lotes con `fecha_vencimiento >= hoy`. Las pruebas también atraparon el `<=` (entrada 2), el
mensaje de error distinto al del escenario 2 y que no se validaban los lotes con cantidad
negativa ni los lotes de un medicamento no registrado.

## Reflexión final

El asistente me ayudó más a escribir rápido el código repetitivo y a proponer el refactor;
lo más útil fue que dejara escritos sus supuestos, porque así pude convertir uno en prueba.
Las pruebas atraparon el error más grave: el código de clase contaba las cajas vencidas como
vigentes, y a simple vista parecía correcto porque en la tienda funcionaba. Aprendí que un
código que pasa en un contexto no pasa en otro si el contrato cambia, y que el contrato y las
pruebas de límite son los que lo dejan ver. En la próxima funcionalidad escribiré primero los
casos límite que salen de la historia (como «vence hoy» o «igual al mínimo») y le preguntaré
al cliente las dudas antes de decidirlas yo, como la P-12.
