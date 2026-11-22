# Registro de pruebas: tabla de casos y pruebas de la IA

Proyecto: Sistema de inventario para una droguería de barrio, con control de lotes y fechas de vencimiento
Estudiante: Alejandra Vargas Baquero
Fecha: 2026-11-22
Rama: `semana7/suite-pruebas` (sale de `main` en `b661415`, entrega de la semana 6)

Funciones probadas (todas en la capa de reglas, sin Flask ni SQLite, ADR-001):

| Función | Archivo | Tipo de regla | Archivo de pruebas |
|---|---|---|---|
| `validar_minimo` | app/reglas/existencias.py | Validación | tests/test_validar_minimo.py |
| `cajas_vigentes` | app/reglas/existencias.py | Cálculo | tests/test_cajas_vigentes.py |
| `productos_por_pedir` | app/reglas/pedidos.py | Varias condiciones (tabla de decisión) | tests/test_decision_pedidos.py y tests/test_pedidos.py |

`validar_minimo` y `cajas_vigentes` ya existían dentro de `productos_por_pedir`. En el
commit `refactor: extrae validar_minimo, cajas_vigentes y es_vigente` se sacaron a
`existencias.py` para probarlas por separado, sin cambiar el comportamiento (las 23
pruebas de las semanas 5 y 6 siguieron pasando y `tests/` no cambió). Ese commit es
anterior a las pruebas nuevas: la IA no modificó el código al generar las pruebas.

Resultado final: `python -m pytest -v` → **70 passed** (23 de antes y 47 nuevas).
`python -m ruff check --select E,F,B,S .` → All checks passed!

Los decimales no aplican: todas las cantidades son cajas enteras, así que no se usa
`pytest.approx`. Los mensajes esperados se copian de la regla en cada archivo de prueba
y no se importan del código, para que el oráculo no salga del código.

## 1. Tabla de casos

### Regla 1: `validar_minimo(minimo)`. El mínimo que define el dueño es un entero ≥ 0

**Regla completa (el oráculo):** HU-05, escenario 2: «Dado que estoy configurando el
mínimo del ibuprofeno de 400 mg, cuando escribo −2, entonces el sistema no lo guarda y
muestra "El mínimo debe ser un número igual o mayor que cero"». Contrato de HU-05:
el mínimo es un entero ≥ 0 y el 0 significa «no pedir nunca» (supuesto 5). Semana 6
(H-03): si el mínimo no es un entero (texto, decimal, booleano o vacío), el mensaje es
«El mínimo debe ser un número entero de cajas». Si es válido, se devuelve igual.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición válida | Entero positivo | 10 | 10 | test_minimo_valido_se_devuelve_igual[10-10] |
| Límite | Primer entero positivo | 1 | 1 | test_minimo_valido_se_devuelve_igual[1-1] |
| Límite | Primer valor válido («no pedir nunca») | 0 | 0 | test_minimo_valido_se_devuelve_igual[0-0] |
| Límite | Último entero inválido | −1 | ValueError «…igual o mayor que cero» | test_minimo_negativo_lanza_error_del_escenario_2[-1] |
| Partición inválida | Entero negativo (escenario 2) | −2 | ValueError «…igual o mayor que cero» | test_minimo_negativo_lanza_error_del_escenario_2[-2] |
| Partición inválida | Texto | "10" | ValueError «…número entero de cajas» | test_minimo_que_no_es_entero_lanza_error[10] |
| Partición inválida | Texto negativo | "-2" | ValueError «…número entero de cajas» (A-2) | test_minimo_que_no_es_entero_lanza_error[-2] |
| Partición inválida | Decimal | 2.5 | ValueError «…número entero de cajas» | test_minimo_que_no_es_entero_lanza_error[2.5] |
| Partición inválida | Decimal con valor entero | 10.0 | ValueError «…número entero de cajas» (A-1) | test_minimo_que_no_es_entero_lanza_error[10.0] |
| Partición inválida | Booleano | True | ValueError «…número entero de cajas» | test_minimo_que_no_es_entero_lanza_error[True] |
| Partición inválida | Booleano que vale 0 | False | ValueError «…número entero de cajas» | test_minimo_que_no_es_entero_lanza_error[False] |
| Partición inválida | Vacío | None | ValueError «…número entero de cajas» | test_minimo_que_no_es_entero_lanza_error[None] |

**Ambigüedades encontradas:**

- **A-1.** ¿Un 10.0 es un mínimo válido? La regla dice «número entero de cajas». Decidí
  que no: en la capa de reglas solo se acepta `int`. Cuando exista el formulario (capa
  web), allí se convertirá el texto a entero antes de llamar a la regla.
- **A-2.** Con «−2» escrito como texto se cumplen dos errores a la vez. Decidí que gana
  el de tipo («…número entero de cajas»), porque primero hay que saber si es un número
  para poder decir si es negativo.

### Regla 2: `cajas_vigentes(medicamento_id, lotes, hoy)`. Suma de cajas no vencidas

**Regla completa (el oráculo):** contrato de HU-05, supuestos 1, 2 y 4: «La cantidad
vigente de un medicamento es la suma de `cantidad_actual` de sus lotes con
`fecha_vencimiento >= hoy`. Un lote que vence hoy todavía cuenta como vigente. Los
lotes vencidos no cuentan, aunque todavía no se hayan dado de baja (HU-06). Un
medicamento sin lotes tiene 0 cajas vigentes.» Errores (semana 6): «El lote L-xxxx
tiene una cantidad negativa» y «El lote L-xxxx tiene una cantidad que no es entera».
Hoy = 24/10/2026, como en el documento de requisitos.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | Sin lotes | [] | 0 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes0-0] |
| Partición | Un lote vigente | L-0627: 3 cajas, vence 30/06/2027 | 3 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes1-3] |
| Partición | Varios lotes vigentes | L-0127: 15 y L-0627: 3 | 18 (ejemplo 2 del README) | test_suma_solo_las_cajas_de_lotes_vigentes[lotes2-18] |
| Partición | Solo vencidos | L-0925: 12, venció 30/09/2026 | 0 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes3-0] |
| Partición | Vigentes y vencidos | L-0925: 12 (vencido) y L-0627: 3 | 3 (ejemplo 1) | test_suma_solo_las_cajas_de_lotes_vigentes[lotes4-3] |
| Partición | Lote vigente con 0 cajas | L-0000: 0 | 0 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes5-0] |
| Límite | Último vencido: venció ayer | 10 cajas, 23/10/2026 | 0 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes6-0] |
| Límite | Primer vigente: vence hoy | 10 cajas, 24/10/2026 | 10 | test_suma_solo_las_cajas_de_lotes_vigentes[lotes7-10] |
| Partición | Lotes de otro medicamento | med. 1: 3 y med. 2: 8 | 3 | test_no_suma_lotes_de_otro_medicamento |
| Partición | Lote inválido de otro medicamento | med. 2 con −1 | 0, sin error (A-4) | test_no_valida_lotes_de_otro_medicamento |
| Partición inválida | Cantidad negativa en lote vigente | −4 | ValueError «El lote L-0001 tiene una cantidad negativa» | test_cantidad_negativa_lanza_error_con_el_lote[-4-fecha0] |
| Partición inválida | Cantidad negativa en lote vencido | −4, vencido | ValueError, mismo mensaje (A-3) | test_cantidad_negativa_lanza_error_con_el_lote[-4-fecha1] |
| Límite | Último negativo | −1 | ValueError, mismo mensaje | test_cantidad_negativa_lanza_error_con_el_lote[-1-fecha2] |
| Límite | Primer valor válido de cantidad | 0 | 0 cajas (fila «lote vigente con 0 cajas») | test_suma_solo_las_cajas_de_lotes_vigentes[lotes5-0] |
| Partición inválida | Cantidad decimal, texto o booleano | 2.5, "5", True | ValueError «El lote L-0002 tiene una cantidad que no es entera» | test_cantidad_no_entera_lanza_error_con_el_lote[...] |

**Ambigüedades encontradas:**

- **A-3.** ¿Un lote vencido con cantidad negativa es un error, si de todos modos no se
  suma? Decidí que sí: la cantidad negativa es un dato dañado sin importar la fecha, y
  así se comporta `productos_por_pedir` desde la semana 6.
- **A-4.** ¿`cajas_vigentes` debe validar los lotes de otros medicamentos? Decidí que no:
  solo valida los lotes que suma. La validación de todos los lotes la sigue haciendo
  `productos_por_pedir`, que sí los recorre todos.

### Regla 3: `productos_por_pedir(medicamentos, lotes, hoy)`. Productos bajo el mínimo

**Regla completa (el oráculo):** HU-05: «Como dueño de la droguería, quiero ver los
medicamentos cuya cantidad vigente está por debajo del mínimo que yo defino para hacer
el pedido antes de que se agoten». Escenario 1: con mínimo 10 y 3 cajas vigentes del
L-0627, el acetaminofén aparece con «3 de 10 cajas». Contrato: la cantidad vigente es la
de la regla 2; «por debajo» es menor estricto (supuesto 3, pregunta P-12); un mínimo de
0 nunca aparece (supuesto 5); la lista va de menor a mayor cantidad vigente y con empate
conserva el orden de llegada; si un dato es inválido se lanza `ValueError` y no se
devuelve una lista parcial.

Las particiones y los límites de esta función ya estaban en `tests/test_pedidos.py`
(semanas 5 y 6). Esta semana se agrega la tabla de decisión y los límites de las
condiciones B y C, en `tests/test_decision_pedidos.py`.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | Bajo el mínimo, con vencidas | Acetaminofén mín. 10, L-0925 (12, vencido) y L-0627 (3) | «3 de 10 cajas» | test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir |
| Partición | Por encima del mínimo | 15 + 3 = 18 vigentes, mín. 10 | [] | test_suma_los_lotes_vigentes_y_no_aparece_si_supera_el_minimo |
| Límite | Último que aparece | 9 vigentes, mín. 10 | «9 de 10 cajas» | test_tabla_de_decision[10-lotes6-esperado6] |
| Límite | Primero que no aparece (igual al mínimo) | 10 vigentes, mín. 10 | [] | test_tabla_de_decision[10-lotes7-esperado7] y test_vigentes_iguales_al_minimo_no_aparece |
| Límite | Mínimo 0 sin cajas | mín. 0, sin lotes | [] | test_minimo_cero_nunca_aparece_aunque_no_haya_cajas y test_tabla_de_decision[0-lotes0-esperado0] |
| Límite | Mínimo 1 sin cajas | mín. 1, sin lotes | «0 de 1 cajas» (A-5) | test_tabla_de_decision[1-lotes8-esperado8] |
| Límite | Lote que vence hoy | 10 cajas que vencen hoy, mín. 10 | [] | test_lote_que_vence_hoy_todavia_cuenta_como_vigente |
| Partición | Solo vencidos | mín. 10, L-0925 vencido | «0 de 10 cajas» | test_medicamento_con_todos_los_lotes_vencidos_aparece_con_cero |
| Partición | Sin lotes | mín. 10 | 0 vigentes | test_medicamento_sin_lotes_aparece_con_cero |
| Partición | Lista vacía | [] | [] | test_sin_medicamentos_devuelve_lista_vacia |
| Partición | Orden | ibuprofeno 2 de 5 y amoxicilina 8 de 10 | [Ibuprofeno, Amoxicilina] | test_resultado_ordenado_de_menor_a_mayor_cantidad_vigente |
| Partición | Empate | dos con 0 de 5 | orden de llegada | test_con_empate_conserva_el_orden_de_llegada |
| Partición inválida | Mínimo negativo | −2 | ValueError | test_minimo_negativo_lanza_error_con_el_mensaje_de_la_historia y test_r1_… |
| Partición inválida | Lote de medicamento no registrado | lote del id 99 | ValueError «…no registrado» | test_lote_de_medicamento_no_registrado_lanza_error |
| Partición inválida | Id repetido | dos con id 1 | ValueError «…id 1 está repetido» | test_medicamento_con_id_repetido_lanza_error |
| Partición inválida | Mínimo o cantidad no enteros | "10", 2.5, True, None… | ValueError | test_minimo_que_no_es_entero_lanza_error_claro y test_cantidad_de_lote_que_no_es_entera_lanza_error |

#### Tabla de decisión

Condiciones:

- **A.** Los datos son válidos (mínimos enteros ≥ 0, ids únicos, cantidades enteras ≥ 0
  y cada lote es de un medicamento registrado).
- **B.** El mínimo es mayor que 0.
- **C.** Las cajas vigentes son menores que el mínimo.
- **D.** El medicamento tiene cajas vencidas.

| Regla | A | B | C | D | Acción | Entrada de la prueba | Esperado |
|---|---|---|---|---|---|---|---|
| R1 | No | – | – | – | ValueError, sin lista parcial | acetaminofén mín. 10 sin cajas + ibuprofeno mín. −2 | ValueError «El mínimo debe ser un número igual o mayor que cero» |
| R2 | Sí | No | – (imposible: 0 < 0 es falso) | No | No aparece | mín. 0, sin lotes | [] |
| R3 | Sí | No | – (imposible) | Sí | No aparece | mín. 0, 5 vencidas | [] |
| R4 | Sí | Sí | Sí | No | Aparece con sus vigentes | mín. 10, 3 vigentes | «3 de 10 cajas» |
| R5 | Sí | Sí | Sí | Sí | Aparece solo con las vigentes | mín. 10, 3 vigentes + 12 vencidas | «3 de 10 cajas» (si contara las vencidas serían 15 y no aparecería) |
| R6 | Sí | Sí | No | No | No aparece | mín. 10, 18 vigentes | [] |
| R7 | Sí | Sí | No | Sí | No aparece | mín. 10, 18 vigentes + 12 vencidas | [] |

Simplificación: cuando A es «No», B, C y D no importan (R1). Cuando B es «No», C no puede
ser «Sí» porque las cajas vigentes nunca son menores que 0, así que solo quedan R2 y R3.
D no cambia la acción, pero sí la cantidad que se muestra (R5): por eso se conservan las
filas con D = Sí.

**Ambigüedades encontradas:**

- **P-12 (sigue abierta).** Si un medicamento tiene exactamente las cajas del mínimo
  (10 de 10), ¿el dueño ya lo quiere ver? Hoy no aparece porque HU-05 dice «por debajo».
- **A-5.** Con mínimo 1 el texto queda «0 de 1 cajas», en plural. La regla solo da el
  formato «3 de 10 cajas». Se deja como está y se agrega a las preguntas para la capa
  web (decir «1 caja» es un tema de presentación, no de la regla).
- **A-6.** La regla no dice si un medicamento puede tener el nombre vacío. Hoy se acepta
  (`test_lista_por_pedir_del_inventario_sintetico` lo usa). Queda para la capa de datos,
  donde el formulario de registro debería exigirlo; no se cambió la regla sin preguntar.

## 2. Pruebas de la IA descartadas o corregidas

**Prompt usado** (bitácora, entrada 13): «Actúa como desarrollador Python que escribe
pruebas con pytest. Contexto: capa de reglas del inventario de una droguería [...].
Te paso la regla completa de `validar_minimo`, `cajas_vigentes` y `productos_por_pedir`
y mi tabla de casos revisada. Tarea: escribe las pruebas de cada fila. Formato: un
archivo por función, `@pytest.mark.parametrize` con un comentario por fila, `pytest.raises`
con el tipo de error exacto y esperados fijos escritos a mano. Restricciones: no
modifiques el código de `app/`; el esperado sale de la regla, no de ejecutar el código.»

El borrador quedó guardado tal cual en el commit `test: borrador de pruebas generado
con IA [...] (sin revisar)` y la revisión en el commit siguiente, para que se vea qué
cambió. El borrador tenía 32 casos nuevos y todos pasaban: que pasen no dice nada, por
eso se revisó cada uno con las tres preguntas (¿el esperado sale de la regla?, ¿fallaría
si rompo el código?, ¿cubre algo que otra prueba no cubre?).

| Prueba generada | Decisión | Por qué | En su lugar |
|---|---|---|---|
| test_validar_minimo: `test_minimo_negativo_lanza_error` con `pytest.raises(ValueError)` sin mensaje | Corregida | Débil (pregunta 2): pasaría aunque un negativo lanzara el mensaje de «no entero». El escenario 2 exige un mensaje exacto | `match` con el mensaje completo del escenario 2, anclado con `^…$` |
| test_validar_minimo: fila `(500, 500)` «entero grande» | Descartada | Redundante (pregunta 3): misma partición que 10 | Nada; el 10 cubre la partición |
| test_validar_minimo: fila `-100` | Descartada | Redundante: misma partición que −2 | Nada; quedan −1 (límite) y −2 (escenario 2) |
| test_validar_minimo: `test_validar_minimo_devuelve_un_entero` con `isinstance(..., int)` | Descartada | Débil: pasaría si devolviera siempre 0. Ya lo cubren los asserts de igualdad | Nada |
| test_validar_minimo: `match="entero"` en los no enteros | Corregida | Una palabra suelta acepta mensajes distintos al de la regla | Mensaje completo «El mínimo debe ser un número entero de cajas» |
| test_validar_minimo: faltaban True, False, 10.0 y "-2" | Agregadas | Particiones de la regla de la semana 6 que el borrador no tenía. False es importante porque vale 0 y podría pasar como «no pedir nunca» | Filas nuevas con su comentario y las ambigüedades A-1 y A-2 |
| test_cajas_vigentes: `test_cajas_vigentes_es_cero_o_mas` (`>= 0`) | Descartada | Débil (pasaría si devolviera siempre 0) y redundante con la fila «solo vencido → 0» | Nada |
| test_cajas_vigentes: fila «vence mañana cuenta» | Descartada | Redundante: el valor límite es el par ayer/hoy (último de una partición y primero de la siguiente); mañana es otra fila de la partición vigente | Nada; quedan ayer y hoy |
| test_cajas_vigentes: `test_lote_con_cantidad_negativa_lanza_error` y `..._decimal_...` sin mensaje | Corregidas | Débiles: no comprobaban el mensaje ni que dijera el número de lote | Pruebas parametrizadas con el mensaje exacto con el lote (L-0001, L-0002) |
| test_cajas_vigentes: faltaban lote con 0 cajas, lote vencido con cantidad negativa, cantidad en texto o booleana y lote inválido de otro medicamento | Agregadas | Particiones que el borrador no tenía; dos dejaron ver ambigüedades (A-3 y A-4) | Filas y pruebas nuevas |
| test_decision_pedidos: `assert (len(resultado) == 1) == aparece` | Corregida | Débil: solo miraba si aparece. Con una función que siempre contara 0 cajas, R4 y R5 seguían pasando | Se compara la lista de textos exacta: `["3 de 10 cajas"]` |
| test_decision_pedidos: `test_r1_datos_invalidos_lanza_error` sin mensaje y con un solo medicamento | Corregida | Débil: no comprobaba el mensaje ni que no se devuelva una lista parcial | Dos medicamentos (uno que sí habría que pedir y uno inválido) y mensaje exacto |
| test_decision_pedidos: `test_vigentes_igual_al_minimo_no_aparece` | Descartada | Redundante: es la misma prueba que `test_pedidos.py::test_vigentes_iguales_al_minimo_no_aparece` | Fila «10 de 10» dentro de la tabla, junto al límite 9 |
| test_decision_pedidos: `test_resultado_no_es_none` | Descartada | Débil: la función nunca devuelve None; pasa con cualquier implementación | Nada |
| test_decision_pedidos: faltaban los límites 9/10 de C y mínimo 1 de B | Agregadas | La tabla de decisión sola no prueba los bordes de cada condición | Tres filas nuevas |

**Decisión:** Conservada, Corregida o Descartada. Las filas que no aparecen en esta tabla
se conservaron como estaban (por ejemplo, las particiones de `cajas_vigentes` con los
ejemplos 1 y 2 del README, cuyo esperado coincide con la regla).

Ninguna prueba se ajustó al código: en ningún caso el esperado se cambió para que
pasara. No apareció ningún defecto del código; las pruebas que fallaron fueron solo las
del paso 5, con el código roto a propósito.

## 3. Romper el código a propósito

Cada cambio se hizo solo, se corrió `python -m pytest -q` y se deshizo con
`git restore <archivo>` antes del siguiente. Primera ronda con 60 pruebas (después de la
revisión); segunda ronda con las 70 finales.

| Id | Cambio introducido | Archivo y línea | ¿Alguna prueba falló? (60 / 70 pruebas) | Qué hice |
|---|---|---|---|---|
| M1 | `fecha_vencimiento >= hoy` por `>` | existencias.py:66 (`es_vigente`) | Sí: 2 / 5. Entre ellas `test_suma_solo_las_cajas_de_lotes_vigentes[lotes7-10]` (vence hoy) y `test_lote_que_vence_hoy_todavia_cuenta_como_vigente` | Nada: la suite protege el borde de la fecha |
| M2 | `vigentes < stock_minimo` por `<=` | pedidos.py:48 | Sí: 6 / 7. Entre ellas `test_tabla_de_decision[10-lotes7-esperado7]` (10 de 10) y las de mínimo 0 (R2, R3) | Nada |
| M3 | `minimo < 0` por `minimo < -1` | existencias.py:46 (`validar_minimo`) | Sí: 1 / 1. Solo `test_minimo_negativo_lanza_error_del_escenario_2[-1]` | Nada; confirma que el límite −1 que se agregó en la revisión era necesario (con el −100 del borrador no se habría notado) |
| M4 | `cajas_vigentes` siempre suma 0 (`total += 0`) | existencias.py:94 | Sí: 5 / 10 | Nada |
| M5 | `es_entero` deja pasar booleanos | existencias.py:24 | Sí: 5 / 5, entre ellas `test_minimo_que_no_es_entero_lanza_error[False]` | Nada |
| M6 | `cantidad_actual < 0` por `< -1` | existencias.py:60 (`validar_cantidad`) | **No: 60 passed** / Sí: 2 | Faltaba el límite −1 de la cantidad (solo se probaba con −4). Se agregó la fila `(-1, …)` en `test_cantidad_negativa_lanza_error_con_el_lote` (commit `test: agrega el límite -1 …`). Con el código roto, ahora falla `[-1-fecha2]` |
| M7 | El orden queda al revés (`reverse=True`) | pedidos.py:57 | Sí: 1 / 2 (`test_resultado_ordenado_de_menor_a_mayor_cantidad_vigente`) | Nada |
| M8 | `cajas_vigentes` no filtra por medicamento | existencias.py:90 | Sí: 2 / 8 | Nada |

## 4. Datos de prueba

**Origen:** sintéticos, propuestos con IA (Claude, bitácora entrada 15) y revisados a mano.
Están en los fixtures `inventario_neiva` y `cinco_mil_lotes` de `tests/conftest.py` y los
usa `tests/test_datos_sinteticos.py`. Confirmo que no hay datos de personas reales: el
proyecto todavía no maneja clientes ni usuarios, así que no hay nombres de personas ni
teléfonos. Los productos son genéricos y la única marca (D'Rosa) es inventada.

**Contexto local:** droguería de barrio en Neiva; productos de mostrador comunes en
Colombia (acetaminofén, suero oral sabor a guanábana, jarabe para la tos, loratadina) y
códigos de lote con el formato del documento de requisitos (L-0627).

**Casos difíciles incluidos:**

| Caso | Dato | Esperado (calculado a mano con la regla) |
|---|---|---|
| Tilde | «Acetaminofén 500 mg», «caléndula», «guanábana» | El nombre sale igual en la lista |
| ñ | «Jarabe para la tos niños 120 ml», lote «NIÑ-01» y «NIÑ-02» | El mensaje de error conserva la ñ: «El lote NIÑ-02 tiene una cantidad negativa» |
| Apóstrofo | «Crema de caléndula D'Rosa 30 g» | Aparece con «0 de 2 cajas» |
| Texto vacío | Medicamento con nombre "" | Aparece con «1 de 3 cajas» (ambigüedad A-6) |
| Mínimo en cero | «Suero oral sabor a guanábana», mínimo 0 y sin lotes | No aparece |
| Lote con 0 cajas | CR-08 con 0 cajas | Suma 0 |
| Vence hoy e igual al mínimo | NIÑ-01: 4 cajas que vencen hoy, mínimo 4 | 4 vigentes y no aparece |
| Venció ayer | CR-07: 6 cajas | No suma |
| Volumen (RNF-01) | 5.000 lotes de 1 caja: 2.500 vencen hoy y 2.500 vencieron ayer | 2.500 vigentes; con mínimo 3.000 aparece «2500 de 3000 cajas» |

Cálculo a mano del inventario de Neiva (hoy = 24/10/2026): acetaminofén 3 (12 vencidas no
cuentan), jarabe 4, crema 0 (6 vencidas y 0 vigentes), sin nombre 1, suero 0, loratadina 7.
Aparecen los que tienen menos que su mínimo: crema 0 < 2, sin nombre 1 < 3 y acetaminofén
3 < 10. No aparecen el jarabe (4 = 4), el suero (mínimo 0) ni la loratadina (7 > 5).
Orden de menor a mayor: crema, sin nombre, acetaminofén.
