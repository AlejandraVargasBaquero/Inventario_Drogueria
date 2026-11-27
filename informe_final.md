# Informe final del proyecto integrador

Proyecto: Sistema de inventario de la Droguería San Rafael (lotes y fechas de vencimiento)\
Estudiante: Alejandra Vargas Baquero\
Repositorio: https://github.com/AlejandraVargasBaquero/Inventario_Drogueria\
Fecha: 2026-11-27

## 1. Resumen

El dueño de una droguería de barrio en Neiva lleva el inventario en Excel y no sabe cuántas de sus cajas ya están vencidas. Por eso pide tarde los medicamentos que se están acabando. El sistema registra medicamentos y lotes con su fecha de vencimiento y muestra la lista «Por pedir» (HU-05): los medicamentos con menos cajas vigentes que el mínimo que el dueño define. Es una aplicación local en tres capas (Flask, reglas en Python puro y SQLite), con 122 pruebas, linter, pipeline de GitHub Actions y contenedor Docker. Usé IA (GitHub Copilot, Gemini y Claude) en las seis fases. Cada uso quedó en la [bitácora](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/bitacora_ia.md) (20 entradas: 5 aceptadas, 12 aceptadas con cambios y 3 rechazadas). El resultado principal de la verificación: el código de clase hecho con IA *parecía* correcto, pero contaba como vigentes las cajas vencidas. Lo atraparon las pruebas escritas desde la historia de usuario, no la lectura del código.

## 2. Problema y usuario

Usuario: el dueño de la droguería, que atiende el mostrador y hace los pedidos al distribuidor.
Cómo lo resolvía antes: una hoja de Excel con el total de cajas por medicamento, sin separar lotes. En la entrevista dijo: «En el Excel me salen 30 cajas de acetaminofén, pero no sé cuántas de esas ya están vencidas» y «Del lote nuevo solo quedaban tres cajas y nadie había hecho el pedido» (necesidad N-05).
Qué necesita: saber, sin hacer cuentas, qué pedir hoy, contando solo cajas que se pueden vender.

Evidencias: propuesta del módulo 1 y documento de requisitos con la entrevista del módulo 2 ([índice de documentos](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/README.md)); historia HU-05 con sus criterios en la [sección 9 del README](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/README.md#9-funcionalidades).

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hiciste con IA | Herramienta | Evidencia (enlace) | Cómo verificaste |
|---|---|---|---|---|
| 1. Fundamentos | [COMPLETAR: p. ej. definir el problema y el alcance] | [COMPLETAR] | `docs/modulo1_propuesta.pdf` | [COMPLETAR] |
| 2. Requisitos | [COMPLETAR: p. ej. redactar historias y criterios a partir de la entrevista]. En la semana 5 la IA trajo el contrato de clase con «menor o igual» y lo rechacé (caso 1) | [COMPLETAR] / Copilot | `docs/modulo2_requisitos.pdf`; bitácora [entrada 2](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/bitacora_ia.md#entrada-2) | Comparé cada criterio con la frase del cliente; las dudas quedaron como preguntas (P-12) |
| 3. Diseño | [COMPLETAR: ADR-001 y modelo de datos]. Semana 5: Copilot propuso un `Protocol` y lo cambié por las entidades del modelo de datos | [COMPLETAR] / Copilot | `docs/modulo3_diseno_adr.pdf`; [entrada 3](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/bitacora_ia.md#entrada-3); [`f296f9d`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/f296f9d) | Las dependencias propuestas se comparan con el ADR-001 (caso 5) |
| 4. Código | Implementar HU-05 con pruebas primero, refactor, revisión de seguridad con IA y agente en rama aparte; capa de datos y capa web con agente | Claude, Gemini, Copilot | [entradas 4 a 11, 16 y 17](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/bitacora_ia.md); [revision_seguridad.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/revision_seguridad.md) | Pruebas en rojo antes del código, `git diff -- tests` vacío en cada refactor, ruff con reglas de seguridad, lectura del diff del agente antes de integrar |
| 5. Pruebas | Casos con particiones, límites y tabla de decisión; borrador de pruebas; datos sintéticos; defecto D-01 | Claude | [registro_pruebas.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/registro_pruebas.md); [criterios_aceptacion.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/criterios_aceptacion.md); [D-01](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/defectos/D-01.md); entradas 12 a 15 y 18 | Revisé cada prueba con tres preguntas; rompí el código 8 veces a propósito; esperados calculados a mano |
| 6. Operación | Pipeline de GitHub Actions, Dockerfile, guía de despliegue y plan de operación | Claude | [ci.yml](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/.github/workflows/ci.yml); [Dockerfile](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/Dockerfile); [revision_configuracion.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/revision_configuracion.md); entrada 19 | Lista de revisión de la semana 9 línea por línea; el pipeline construye la imagen y comprueba que responde |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

### Caso 1: «menor o igual» en lugar de «por debajo» (requisitos)

- Fase: requisitos.
- Qué propuso la IA: el contrato del taller de clase (Copilot) decía «existencias menores o iguales a su mínimo», y la implementación usaba `<=`.
- Qué estaba mal: HU-05 dice «por debajo del mínimo». Con `<=`, la loratadina con 10 de 10 cajas salía en la lista por pedir.
- Cómo lo detectaste: comparando el contrato con la frase de la historia. Lo confirmaron las pruebas límite `test_vigentes_iguales_al_minimo_no_aparece` y `test_lote_que_vence_hoy_todavia_cuenta_como_vigente`, que fallaban con `<=`.
- Qué hiciste: dejé el menor estricto como supuesto 3 del contrato y no lo decidí sola: quedó como pregunta P-12 para el cliente. Commits [`2c428b2`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/2c428b2) (pruebas en rojo) y [`efe5599`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/efe5599). Bitácora, entrada 2.

### Caso 2: el código de la IA contaba las cajas vencidas (código)

- Fase: código.
- Qué propuso la IA: reutilizar la implementación de Copilot de la tienda (`[p for p in productos if p.existencias <= p.minimo]`), sumando todas las cajas de los lotes.
- Qué estaba mal: sumaba también los lotes vencidos. El acetaminofén con 12 cajas vencidas y 3 vigentes salía con 15 y no aparecía por pedir. Es justo el problema del cliente.
- Cómo lo detectaste: con las 14 pruebas escritas antes desde el escenario 1 de HU-05: 8 fallaron (`assert 0 == 1` en `test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir`, e `IndexError` con todos los lotes vencidos).
- Qué hiciste: rechacé la versión y escribí la regla «solo cuentan los lotes con `fecha_vencimiento >= hoy`». Commit [`efe5599`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/efe5599). Bitácora, entrada 1.

### Caso 3: `isinstance(True, int)` deja pasar un booleano (código, revisión de seguridad)

- Fase: código (revisión de seguridad de la semana 6).
- Qué propuso la IA: para el hallazgo H-03 (tipos sin validar), validar con `isinstance(valor, int)`.
- Qué estaba mal: en Python `bool` es subclase de `int`, así que un mínimo `True` seguía pasando y mostraba «0 de True cajas». Además, de los 6 hallazgos de la revisión con IA, 3 eran falsos positivos (`sorted` inestable, XSS en una capa que no genera HTML y S101 en las pruebas). La IA tampoco vio que `.gitignore` ignoraba `.env.example`.
- Cómo lo detectaste: llamé a la función con `True`, `"10"`, `2.5` y `None` en pruebas parametrizadas escritas antes de la corrección (en rojo). Los falsos positivos los descarté con la documentación de `sorted` y la prueba de empate.
- Qué hiciste: creé `es_entero`, que excluye `bool`, con sus pruebas. Commit [`ead80c7`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/ead80c7). Bitácora, entradas 8 y 10.

### Caso 4: pruebas de la IA que pasaban con el código roto (pruebas)

- Fase: pruebas.
- Qué propuso la IA: un borrador de 32 casos, todos en verde, guardado tal cual en [`a286c97`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/a286c97).
- Qué estaba mal: varios `pytest.raises(ValueError)` no comprobaban el mensaje (pasaban con el error equivocado). La tabla de decisión solo miraba si el medicamento aparecía, no con cuántas cajas. Había pruebas que pasan con cualquier implementación (`resultado is not None`).
- Cómo lo detectaste: revisé cada prueba con tres preguntas (¿el esperado sale de la regla?, ¿fallaría con el código roto?, ¿es redundante?) y rompí el código 8 veces. Con el mutante M6 (`cantidad < -1`) ninguna de las 60 pruebas falló.
- Qué hiciste: corregí 6, descarté 7, agregué 15 filas y el límite −1 de la cantidad. Commits [`ae0402e`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/ae0402e) y [`fc827e1`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/fc827e1). Bitácora, entrada 13; registro de pruebas, secciones 2 y 3.

### Caso 5: una dependencia que el diseño no permitía (diseño y operación)

- Fase: diseño y operación.
- Qué propuso la IA: en la capa web, `python-dotenv` para leer `.env`. En la configuración de la semana 9, un `requirements.txt` que mezclaba Flask con pytest y ruff.
- Qué estaba mal: el ADR-001 pide la menor cantidad de dependencias (Flask y la librería estándar). Una dependencia más es otro paquete que auditar. Con los requisitos mezclados, la imagen Docker habría llevado herramientas de desarrollo.
- Cómo lo detectaste: revisé el diff contra el ADR-001 y el Dockerfile con la lista de la semana 9.
- Qué hiciste: cambié `python-dotenv` por una función de 10 líneas (`_cargar_env`), commit [`2b6b82f`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/2b6b82f). Separé `requirements-dev.txt`, commit [`8896e0f`](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/commit/8896e0f). Bitácora, entradas 17 y 19.

## 5. Estado final del sistema

- Arquitectura: aplicación local en tres capas según el ADR-001. La interfaz es Flask (`app/web`) y solo convierte texto y muestra mensajes. Las reglas están en Python puro (`app/reglas`) y se prueban solas. Los datos van en SQLite con consultas parametrizadas (`app/datos`). Se despliega con Python o Docker ([guía de despliegue](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/guia_despliegue.md)). Diseño y ADR: `docs/modulo3_diseno_adr.pdf`.
- Funcionalidades terminadas: HU-05 «Productos bajo el mínimo» (Must), terminada, con sus dos escenarios automatizados. Registro de medicamentos, cambio del mínimo y registro de lotes, con la pantalla de inventario que marca lotes vencidos y vigentes.
- Pruebas: 122 pruebas (reglas, datos, web, aceptación, abuso y datos sintéticos con 5.000 lotes). El pipeline exige cobertura de ramas ≥ 90 % en `app.reglas` y `app.datos`: [COMPLETAR con el porcentaje y el enlace a la última ejecución del pipeline](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/actions).
- Pendientes: dar de baja lotes vencidos (HU-06); usuarios y roles (hoy la aplicación es local, de un solo usuario); servidor de producción (gunicorn) si se publica; preguntas P-12 (¿igual al mínimo ya se pide?) y A-6 (¿nombre obligatorio?) para el cliente.

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | El sistema no guarda datos de personas: solo medicamentos, lotes y cantidades. No registra clientes ni fórmulas médicas, porque esos serían datos sensibles de salud (art. 5) y necesitarían autorización expresa. Todos los datos de prueba son sintéticos y no usan marcas reales. La base y la `SECRET_KEY` nunca se suben (`.gitignore`, `.dockerignore`) | [conftest.py](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/tests/conftest.py); bitácora, entrada 15 |
| Sesgo | No hay un modelo de IA en producción; el sesgo que encontré fue de la IA de desarrollo. Trajo la regla de una tienda (existencias únicas, `<=`) a una droguería, donde vencer importa. Los datos de prueba incluyen tildes, ñ y apóstrofos para que los nombres locales funcionen | Casos 1 y 2; datos sintéticos |
| Transparencia | La pantalla «Por pedir» muestra la fecha usada, avisa que «solo cuentan las cajas de lotes que no han vencido» y muestra «3 de 10 cajas», así que el dueño ve con qué cuenta se decidió. El uso de IA está declarado en el README (sección 7) y en la bitácora, con prompts y decisiones | README; bitácora |
| Responsabilidad | La IA propone y yo respondo por lo que se integra. Nada entra a `main` sin pruebas en verde y revisión del diff. Las decisiones de negocio (P-12, A-6) son del cliente, no mías ni de la IA | Entradas 9, 16 y 17; pipeline |
| Propiedad intelectual y política de uso | El código generado con IA se revisó línea por línea y se declara. Las dependencias tienen licencias permisivas (Flask, BSD-3). No se usan marcas ni datos reales. El uso respeta la política del seminario: IA permitida, declarada y verificada | Bitácora; `requirements.txt` |

Dilema. El código de clase hecho con IA funcionaba y pasaba sus pruebas en la tienda. Aceptarlo era lo más rápido. Pero en una droguería, contar las 12 cajas vencidas como existencias tiene dos efectos. El dueño no pide a tiempo el acetaminofén. Y el sistema le hace creer que tiene producto que no se puede vender legalmente ni con seguridad. Elegí no aceptar código que no pudiera justificar con la historia de usuario, aunque costara más tiempo: escribí primero las pruebas desde el criterio del cliente y rechacé la versión de la IA. Por la misma razón no decidí sola el caso «10 de 10» ni la obligatoriedad del nombre: los dejé escritos como preguntas para el cliente.

## 7. Aprendizajes

Ahora sé escribir una historia de usuario como contrato con supuestos, casos límite y errores. También sé probarla con particiones, límites y tablas de decisión, y comprobar que mis pruebas sirven rompiendo el código a propósito. Sé darle a un agente una tarea delimitada en una rama y revisar el diff antes de integrarlo, y armar un pipeline y un contenedor sin secretos ni permisos de más.

Confié de más en la IA en dos momentos. Cuando el borrador de pruebas salió todo en verde y parecía terminado, y cuando el código de clase «ya funcionaba». En los dos casos, lo que parecía correcto no lo era en mi contexto.

Lo que haría distinto: escribir los casos límite que salen de la historia («vence hoy», «igual al mínimo») antes de pedirle nada a la IA. Preguntarle al cliente las dudas antes de decidirlas. Y documentar en la bitácora desde el módulo 1, no desde el 5.

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/bitacora_ia.md)
- Documentos de cada módulo: [docs/README.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/docs/README.md)
- Revisión de código y seguridad: [revision_seguridad.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/revision_seguridad.md)
- Registro de pruebas: [registro_pruebas.md](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/blob/main/registro_pruebas.md)
- Pipeline: [GitHub Actions](https://github.com/AlejandraVargasBaquero/Inventario_Drogueria/actions)
