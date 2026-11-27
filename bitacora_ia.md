# Bitácora de uso de IA

Proyecto: Sistema de inventario para una droguería de barrio, con control de lotes y fechas de vencimiento
Estudiante: Alejandra Vargas Baquero
Funcionalidad: HU-05 Productos bajo el mínimo (`productos_por_pedir`). Semana 6: revisión de código y seguridad. Semana 7: suite de pruebas con técnicas formales (`validar_minimo`, `cajas_vigentes` y `productos_por_pedir`). Semanas 8 y 9: aceptación, defecto D-01, pipeline y contenedor.
Asistente usado: GitHub Copilot (chat en VS Code, modo agente) en el taller de clase; Gemini (chat) para explicar y revisar el código de clase; Claude (chat) para la implementación y el refactor del proyecto. En la semana 6, Claude como revisor (chat) y como agente en la rama `agente/revision-semana6`. En la semana 7, Claude para proponer casos, escribir el borrador de las pruebas y generar los datos sintéticos, en la rama `semana7/suite-pruebas`.

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

## Entradas de la semana 7

### Entrada 12

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Diseño de casos con IA (Claude) con el prompt de la semana: «Actúa como analista de pruebas. Te paso la regla completa de tres funciones de la capa de reglas: `validar_minimo` (HU-05, escenario 2 y semana 6), `cajas_vigentes` (supuestos 1, 2 y 4 del contrato) y `productos_por_pedir` (contrato completo de HU-05). Tarea: propón los casos con particiones de equivalencia (incluidas las inválidas), valores límite (último valor de una partición y primero de la siguiente) y una tabla de decisión para `productos_por_pedir`. Formato: una tabla por función con técnica, partición o límite, entrada y esperado. Restricciones: el esperado sale de la regla, no del código; si la regla no dice algo, márcalo como ambigüedad en lugar de decidirlo.»
- **Decisión:** Aceptada con cambios
- **Por qué:** Revisé la propuesta con las cinco preguntas. *Particiones:* faltaban `True`, `False` y `10.0` para el mínimo, y el lote con 0 cajas. *Límites:* para la fecha propuso ayer, hoy y mañana; dejé solo ayer y hoy, que son el último vencido y el primer vigente. *Origen del esperado:* los esperados de 18 y 3 cajas los comprobé con los ejemplos 1 y 2 del README. *Ambigüedades:* quedaron seis (A-1 a A-6 y P-12, sección 1 del registro). *Reglas inventadas:* no agregué una validación de nombre vacío porque HU-05 no la pide; quedó como ambigüedad A-6 para la capa de datos. En la tabla de decisión simplifiqué R2 y R3, porque con mínimo 0 la condición «vigentes < mínimo» nunca se cumple.
- **Verificación:** Cada fila de la tabla tiene una regla escrita como oráculo y una prueba que la cubre (registro, sección 1).
- **Commit relacionado:** `ae0402e` (las tablas quedaron en `registro_pruebas.md`).

### Entrada 13

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Generación de pruebas (Claude): «Actúa como desarrollador Python que escribe pruebas con pytest. Contexto: capa de reglas del inventario de una droguería (Python 3.13, pytest 9.1.1). Te paso la regla de cada función y mi tabla de casos revisada. Tarea: escribe las pruebas de cada fila. Formato: un archivo por función, `@pytest.mark.parametrize` con un comentario por fila, `pytest.raises` con el tipo de error exacto y esperados fijos escritos a mano. Restricciones: no modifiques el código de `app/`; el esperado sale de la regla, no de ejecutar el código.»
- **Decisión:** Aceptada con cambios
- **Por qué:** El borrador traía 32 casos y todos pasaban, pero eso no dice nada. Al revisar cada prueba con las tres preguntas corregí 6, descarté 7 y agregué las particiones y límites que faltaban (15 filas en la sección 2 del registro). Lo más importante: los `pytest.raises(ValueError)` sin mensaje pasaban aunque saliera el error equivocado, y la tabla de decisión solo miraba si el medicamento aparecía, no con cuántas cajas. Además, los mensajes esperados los escribí a mano en cada prueba en lugar de importar las constantes del código, para que el oráculo no salga del código.
- **Verificación:** `python -m pytest -v`: 70 passed. Rompí el código 8 veces (sección 3 del registro): en M6 (`cantidad < -1`) no falló ninguna prueba, así que agregué el límite −1 de la cantidad y ahora sí falla. `git diff` del borrador a la revisión: no cambió nada en `app/`.
- **Commit relacionado:** `a286c97` (borrador sin revisar), `ae0402e` (revisión) y `fc827e1` (caso agregado después de romper el código).

### Entrada 14

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Para probar tres funciones, Claude propuso sacar `validar_minimo`, `cajas_vigentes` y `es_vigente` de `productos_por_pedir` a un módulo nuevo, `app/reglas/existencias.py`, y hacer que `productos_por_pedir` las use.
- **Decisión:** Aceptada
- **Por qué:** Las tres reglas ya existían dentro de `productos_por_pedir` y están en el contrato de HU-05, así que no se inventa ninguna regla. Al ser la misma lógica compartida, si rompo `es_vigente` fallan las pruebas de las dos funciones. Lo hice en un commit aparte y antes de generar las pruebas, para que la IA no tocara el código al escribirlas.
- **Verificación:** `python -m pytest`: 23 passed antes y después del refactor; `git diff -- tests` vacío; `python -m app` imprime la misma lista; ruff: All checks passed!
- **Commit relacionado:** `bbabf8c`.

### Entrada 15

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Datos sintéticos (Claude): «Genera datos de prueba para el inventario de una droguería de barrio en Neiva: 6 medicamentos y sus lotes. Sin personas reales ni marcas reales. Incluye casos difíciles: tildes, ñ, apóstrofo, texto vacío, mínimo 0, lote con 0 cajas, un lote que vence hoy, uno que venció ayer y un medicamento sin lotes. Agrega un caso de volumen con 5.000 lotes (RNF-01). Entrégalos como fixtures de pytest en `tests/conftest.py`.»
- **Decisión:** Aceptada con cambios
- **Por qué:** Los datos no tienen personas ni teléfonos (el proyecto aún no maneja clientes) y la marca D'Rosa es inventada. Calculé a mano, lote por lote, las cajas vigentes de cada medicamento y la lista por pedir (registro, sección 4); no tomé el esperado de ejecutar el código. Cambié el lote que vence hoy para que quedara exactamente igual al mínimo (4 de 4), así combina dos límites en un solo dato. El nombre vacío dejó ver la ambigüedad A-6.
- **Verificación:** `test_datos_sinteticos.py`: 9 pruebas pasan; el esperado de 2.500 cajas en los 5.000 lotes sale de 5.000 / 2, porque los pares vencen hoy y los impares vencieron ayer.
- **Commit relacionado:** `25ce969`.

## Backend: capa de datos con SQLite

### Entrada 16

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Agente (Claude) en la rama `backend/capa-datos`. **Rol:** desarrollador Python que trabaja con pruebas primero. **Contexto:** ADR-001 (capas de interfaz, reglas y datos; SQLite), contrato de HU-05, modelos de `app/reglas/modelos.py` y la tabla de Pendientes de `revision_seguridad.md`. **Tarea:** escribir primero las pruebas del repositorio (medicamentos, lotes, escenario 2 al guardar, fechas, inyección SQL y HU-05 con datos leídos de la base) y después la implementación. **Formato:** un commit en rojo y uno en verde. **Restricciones:** solo `sqlite3` de la librería estándar, consultas con `?`, reutilizar `validar_minimo` y `validar_cantidad`, no modificar las pruebas existentes.
- **Decisión:** Aceptada con cambios
- **Por qué:** Cierra dos pendientes de la semana 6: inyección (consultas con parámetros y prueba con `' OR 1=1 --`) y fechas (`datetime` no se acepta; la fecha se guarda como texto ISO y se lee como `date`). La IA propuso exigir el nombre del medicamento: lo acepté solo para el registro, porque HU-05 no lo dice; queda como pregunta para el cliente (ambigüedad A-6).
- **Verificación:** El commit en rojo tenía 23 pruebas nuevas que fallaban con el esqueleto (`NotImplementedError`). Con la implementación: `python -m pytest`: 93 passed, y `git diff` entre los dos commits no toca `tests/`. `ruff check --select E,F,B,S .`: All checks passed! (S608, el aviso de SQL armado con texto, no aparece).
- **Commit relacionado:** `c1f0cbf` (en rojo) y `6d5ea55` (en verde).

## Frontend: pantallas web con Flask

### Entrada 17

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Agente (Claude) en la rama `frontend/pantallas-web`, que sale de `backend/capa-datos`. **Rol:** desarrollador Python y Flask que trabaja con pruebas primero. **Contexto:** ADR-001 (Flask, SQLite, aplicación local en capas), contrato de HU-05, la capa de datos ya hecha y los pendientes de seguridad de la semana 6 (XSS y `SECRET_KEY` en `.env`). **Tarea:** dos pantallas (por pedir e inventario) y los formularios de medicamento, mínimo y lote; primero las pruebas con el cliente de pruebas de Flask y una base temporal. **Formato:** commit en rojo y commit en verde. **Restricciones:** ninguna regla de negocio en las rutas; Flask con versión fijada como única dependencia nueva; no usar `|safe`; no modificar las pruebas existentes.
- **Decisión:** Aceptada con cambios
- **Por qué:** Las rutas solo convierten texto y llaman a las capas de datos y reglas, así que los mensajes que ve el dueño son los mismos de HU-05. La IA propuso python-dotenv para leer `.env`; lo cambié por una función de 10 líneas con la librería estándar para no sumar otra dependencia. Agregó un token en cada formulario (CSRF), que no estaba en mis pendientes pero protege el cambio del mínimo; lo acepté con su prueba de abuso. La fecha «2027-02-30» no existe: se agregó como caso para que muestre el mensaje y no lance un error 500.
- **Verificación:** commit en rojo con 25 pruebas nuevas que fallaban (`NotImplementedError`); con la implementación, `python -m pytest`: 118 passed y `tests/` sin cambios entre los dos commits. `ruff check --select E,F,B,S .`: All checks passed! Abrí las dos pantallas con los datos del documento de requisitos: «Por pedir» muestra ibuprofeno 2 de 5, acetaminofén 3 de 10 y amoxicilina 8 de 10 (igual que `python -m app`), y al cambiar el mínimo del ibuprofeno a −2 sale el mensaje del escenario 2 y el mínimo sigue en 5.
- **Commit relacionado:** `e8ddb3e` (en rojo) y `2b6b82f` (en verde).

## Semanas 8 y 9: aceptación, defectos, pipeline y contenedor

### Entrada 18

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Claude, con acceso al repositorio: «Revisa qué le falta al proyecto para la entrega final según la tarea de la semana 10 y las prácticas de las semanas 8 y 9. Busca defectos probando los formularios con valores fuera de lo normal.» Encontró que un número de 20 cifras en cualquier formulario daba error 500 (`OverflowError` de SQLite) y propuso la prueba en rojo, la corrección y el reporte D-01.
- **Decisión:** Aceptada con cambios
- **Por qué:** El defecto es real: lo reproduje con los 4 formularios. La corrección va en la capa de datos (`_exigir_rango`) y no en `app/reglas/`, porque el límite viene de SQLite y no de HU-05, y yo no quiero meter en las reglas algo que el cliente no pidió. El borrador del reporte marcaba «No usé IA para redactar los pasos»; lo corregí porque no era cierto.
- **Verificación:** Prueba parametrizada en rojo (4 fallos, `9d86a6a`) y en verde con la corrección (`9776ce7`). `python -m pytest`: 122 passed; ruff sin avisos; `git diff 9d86a6a 9776ce7 -- tests` vacío.
- **Commit relacionado:** `9d86a6a`, `9776ce7` y el reporte en `docs/defectos/D-01.md`.

### Entrada 19

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Claude: «Escribe el pipeline de GitHub Actions y el Dockerfile para este proyecto. Contexto: ADR-001 (Flask + SQLite, aplicación local), rama `main`, Python 3.10 a 3.13, `requirements.txt` con versiones fijadas. Restricciones: la lista de revisión de la semana 9 (permisos mínimos, sin secretos en archivos, versiones fijadas, usuario sin privilegios, `.dockerignore`, sin modo debug) y que un fallo de las pruebas haga fallar el pipeline.»
- **Decisión:** Aceptada con cambios
- **Por qué:** Revisé los dos archivos con la lista de la semana 9 (tabla en `docs/revision_configuracion.md`). Al revisarlos apareció que `requirements.txt` mezclaba Flask con pytest y ruff, así que se separó `requirements-dev.txt`. La base SQLite se movió a un volumen para no perderla al borrar el contenedor. Acepté el servidor de desarrollo de Flask solo porque ADR-001 dice aplicación local, y lo dejé como pendiente.
- **Verificación:** En local: 122 passed, ruff sin avisos y el YAML se lee sin errores. Docker no se pudo construir en local (sin acceso a internet para bajar la imagen base); la construcción y el `curl` de prueba los hace el job `imagen` del pipeline. [COMPLETAR: enlace a la ejecución en verde y resultado de hacer fallar una prueba a propósito.]
- **Commit relacionado:** `8896e0f`, `8d39e98` y `db7bc1f`.

### Entrada 20

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Claude, para la entrega final: borrador de la guía de despliegue, el plan de operación, la tabla de criterios de aceptación, el informe final a partir de la plantilla `informe_final_integrador.md` y las diapositivas, con la condición de usar solo evidencias que ya estuvieran en el repositorio y en esta bitácora.
- **Decisión:** Aceptada con cambios
- **Por qué:** La tarea permite usar IA para la redacción y para organizar las diapositivas. Cada caso de la sección 4 del informe sale de una entrada de esta bitácora y tiene su commit. Las filas de los módulos 1 a 3 las completo yo, porque esa parte no estaba en la bitácora.
- **Verificación:** [CONFIRMAR antes de entregar] Abrí cada enlace del informe y busqué cada hash de commit en `git log`.
- **Commit relacionado:** el de esta entrada y el del informe final.

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 5 (entradas 4, 5, 7, 9 y 14) |
| Aceptadas con cambios | 12 (entradas 3, 6, 8, 10, 12, 13, 15, 16, 17, 18, 19 y 20) |
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

### Semana 7

Las pruebas nuevas no encontraron defectos en el código, pero romperlo a propósito sí
encontró un hueco en las pruebas: con `cantidad_actual < -1` en lugar de `< 0` las 60
pruebas pasaban, porque la cantidad negativa solo se probaba con −4. Agregué el límite −1
(registro, sección 3, M6). También vi que el borrador de la IA tenía 32 casos en verde y
aun así varios no habrían fallado con el código roto, como los `pytest.raises` sin mensaje.

## Reflexión final

El asistente me ayudó más a escribir rápido el código repetitivo y a proponer el refactor;
lo más útil fue que dejara escritos sus supuestos, porque así pude convertir uno en prueba.
Las pruebas atraparon el error más grave: el código de clase contaba las cajas vencidas como
vigentes, y a simple vista parecía correcto porque en la tienda funcionaba. Aprendí que un
código que pasa en un contexto no pasa en otro si el contrato cambia, y que el contrato y las
pruebas de límite son los que lo dejan ver. En la próxima funcionalidad escribiré primero los
casos límite que salen de la historia (como «vence hoy» o «igual al mínimo») y le preguntaré
al cliente las dudas antes de decidirlas yo, como la P-12.
