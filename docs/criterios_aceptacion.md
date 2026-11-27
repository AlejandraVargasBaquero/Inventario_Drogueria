# Criterios de aceptación automatizados (semana 8)

Historia: **HU-05. Productos bajo el mínimo** (Must). Cada escenario se clasificó antes de automatizarlo: ¿se automatiza ya, le falta un dato o no es observable?

| Escenario | Clasificación | Prueba de aceptación (cliente de pruebas de Flask, base temporal) | Prueba de la regla |
|---|---|---|---|
| 1. Acetaminofén con 3 vigentes de 10 aparece con «3 de 10 cajas» | Se automatiza: tiene los datos exactos (L-0627, mínimo 10) | `test_escenario_1_acetaminofen_aparece_con_3_de_10_cajas` ([test_pantallas.py](../tests/test_pantallas.py)) | `test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir` ([test_pedidos.py](../tests/test_pedidos.py)) |
| 2. Mínimo −2: no se guarda y se muestra el mensaje | Se automatiza: el mensaje está escrito en el criterio | `test_escenario_2_minimo_negativo_al_registrar_no_se_guarda` y `test_escenario_2_cambiar_minimo_a_negativo_no_lo_guarda` | `test_validar_minimo.py` |
| Igual al mínimo (10 de 10) | Le faltaba un dato: la regla dice «por debajo». Se decidió menor estricto (supuesto 3) y quedó la pregunta P-12 | — | `test_vigentes_iguales_al_minimo_no_aparece` |
| Lote que vence hoy | Le faltaba un dato: ¿cuenta o no? Se decidió que sí (supuesto 1) | `test_el_inventario_marca_los_lotes_vencidos_y_el_que_vence_hoy` | `test_lote_que_vence_hoy_todavia_cuenta_como_vigente` |
| «Hacer el pedido antes de que se agoten» | No es observable: el sistema no hace pedidos. Se comprueba con el escenario 1 | — | — |

Cada prueba de aceptación comprueba todo el «entonces»: el texto en pantalla **y** que la base no cambió cuando hay error.

## Cobertura

El pipeline mide la cobertura de ramas de la lógica del negocio y falla si baja del 90 %:

```bash
python -m pytest --cov=app.reglas --cov=app.datos --cov-branch --cov-report=term-missing --cov-fail-under=90
```

Resultado local: las pruebas recorren el 100 % de las líneas de `app/reglas` y `app/datos`. El porcentaje de ramas queda en cada ejecución del pipeline (pestaña Actions).

## Defectos encontrados

- [D-01](defectos/D-01.md): un número de 20 cifras en cualquier formulario daba error 500. No lo encontró ninguna prueba derivada de los criterios. Apareció al probar un valor fuera de toda partición razonable (el límite físico de SQLite). Se corrigió con prueba en rojo primero (`9d86a6a`) y luego la corrección (`9776ce7`).
