# Sistema de inventario de la Droguería San Rafael

## 1. Qué es

Sistema de inventario para una droguería de barrio en Neiva, con control de lotes y
fechas de vencimiento. Le avisa al dueño qué medicamentos están por debajo del mínimo
contando solo las cajas de lotes que no han vencido. Proyecto final del Seminario de
Inteligencia Artificial Aplicada al Ciclo de Vida del Software (FET, 2026). Los nombres
del cliente y del negocio son ficticios.

Documentos base: requisitos (semana 3) y diseño (semana 4, ADR-001 y ADR-002).
Funcionalidad implementada: HU-05 «Productos bajo el mínimo» (ver la sección 9).

## 2. Requisitos

- Python 3.10 o superior (desarrollado con Python 3.13).
- Git.
- Dependencias con versión fijada en `requirements.txt`: `pytest==9.1.1` (pruebas) y
  `ruff==0.16.9` (linter). La capa de reglas solo usa la librería estándar (ADR-001).

## 3. Instalación

```bash
git clone https://github.com/AlejandraVargasBaquero/Inventario_Drogueria.git
cd Inventario_Drogueria
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate       # Linux o macOS
python -m pip install -r requirements.txt
```

Cuando existan la capa web y la de datos, copia `.env.example` como `.env` y pon tus
valores. El archivo `.env` nunca se sube (está en `.gitignore`).

## 4. Ejecución

Por ahora solo existe la capa de reglas. Para ver HU-05 con los datos del documento de
requisitos (hoy = 24/10/2026):

```bash
python -m app
```

Salida esperada:

```
Productos por pedir al 24/10/2026:
- Ibuprofeno 400 mg: 2 de 5 cajas
- Acetaminofén 500 mg: 3 de 10 cajas
- Amoxicilina 500 mg: 8 de 10 cajas
```

## 5. Pruebas y calidad

```bash
python -m pytest -v                          # resultado esperado: 93 passed
python -m ruff check --select E,F,B,S .      # resultado esperado: All checks passed!
pip-audit -r requirements.txt                # auditoría de dependencias
```

La configuración de ruff está en `pyproject.toml`. El informe de la revisión de código y
seguridad de la semana 6 está en [revision_seguridad.md](revision_seguridad.md). Las tablas
de casos, la revisión de las pruebas de la IA y el resultado de romper el código
(semana 7) están en [registro_pruebas.md](registro_pruebas.md).

## 6. Estructura

La estructura sigue el ADR-001 (aplicación local en capas: interfaz, reglas de
inventario y acceso a datos). La capa de reglas no depende de Flask ni de SQLite y por
eso se puede probar sola. La capa de datos (`app/datos/`, rama `backend/capa-datos`)
guarda en SQLite y aplica las mismas reglas antes de guardar.

```
inventario-drogueria/
├── app/
│   ├── __init__.py
│   ├── __main__.py            # Demostración: python -m app
│   ├── datos/                 # Capa de acceso a datos (backend)
│   │   ├── __init__.py
│   │   └── repositorio.py     # Medicamentos y lotes en SQLite
│   └── reglas/                # Capa de reglas de inventario
│       ├── __init__.py
│       ├── existencias.py     # validar_minimo, cajas_vigentes y es_vigente (semana 7)
│       ├── modelos.py         # Medicamento, Lote y ProductoPorPedir
│       └── pedidos.py         # productos_por_pedir (HU-05)
├── tests/
│   ├── conftest.py            # Datos sintéticos en fixtures (semana 7)
│   ├── test_pedidos.py        # Pruebas de HU-05 (normales, límite, error y abuso)
│   ├── test_validar_minimo.py # Particiones y límites del mínimo (semana 7)
│   ├── test_cajas_vigentes.py # Particiones y límites de las cajas vigentes (semana 7)
│   ├── test_decision_pedidos.py # Tabla de decisión de productos_por_pedir (semana 7)
│   ├── test_datos_sinteticos.py # Pruebas con los datos sintéticos (semana 7)
│   └── test_repositorio.py    # Capa de datos con SQLite (backend)
├── docs/evidencias/           # Capturas de la revisión de la semana 6
├── .env.example               # Plantilla de variables de entorno (sin valores reales)
├── bitacora_ia.md             # Bitácora de uso de IA
├── registro_pruebas.md        # Tablas de casos y revisión de las pruebas (semana 7)
├── revision_seguridad.md      # Informe de revisión de código y seguridad
├── pyproject.toml             # Configuración de ruff
├── pytest.ini
├── requirements.txt
└── README.md
```

## 7. Uso de IA

Usé GitHub Copilot, Gemini y Claude para escribir, revisar y refactorizar código. Cada
sugerencia se verificó con las pruebas antes de aceptarla. El detalle de qué acepté,
ajusté o rechacé está en [bitacora_ia.md](bitacora_ia.md). En la semana 6, Claude
trabajó como agente en la rama `agente/revision-semana6` y yo revisé el diff antes de
integrarlo a `main`. En la semana 7, Claude propuso los casos, escribió el borrador
de las pruebas y los datos sintéticos en la rama `semana7/suite-pruebas`; el borrador
quedó en su propio commit y mi revisión en el siguiente (ver `registro_pruebas.md`).

## 8. Autora y licencia

- Autora: Alejandra Vargas Baquero.
- Docente: Jorge Luis Trujillo. Fundación Escuela Tecnológica de Neiva (FET), 2026.
- Licencia: proyecto académico, todos los derechos reservados.

## 9. Funcionalidades

### Capa de datos con SQLite (backend)

Funciones de `app/datos/repositorio.py`:

| Función | Qué hace | Errores (`ValueError`, no guarda nada) |
|---|---|---|
| `conectar(ruta)` | Abre la base con las llaves foráneas activadas (`":memory:"` en las pruebas) | — |
| `crear_esquema(con)` | Crea las tablas `medicamento` y `lote` si no existen; no borra datos | — |
| `guardar_medicamento(con, nombre, stock_minimo)` | Registra un medicamento y devuelve su id | Nombre vacío; mínimo no entero o negativo (escenario 2 de HU-05) |
| `cambiar_minimo(con, medicamento_id, nuevo_minimo)` | Cambia el mínimo | Mínimo inválido; medicamento que no existe |
| `guardar_lote(con, medicamento_id, numero_lote, fecha, cantidad)` | Registra un lote | Número vacío; fecha que no es `date` (incluido `datetime`); cantidad inválida; medicamento que no existe; lote repetido para el mismo medicamento |
| `listar_medicamentos(con)` | Medicamentos en el orden de registro | — |
| `listar_lotes(con)` | Lotes con la fecha convertida a `date` | — |

Decisiones:

- Todas las consultas usan parámetros `?`. Prueba de abuso: los nombres `' OR 1=1 --` y
  `Jarabe'); DROP TABLE medicamento; --` se guardan como texto y la tabla sigue intacta
  (pendiente de inyección de la semana 6).
- Las fechas se guardan como texto ISO (AAAA-MM-DD) y se leen como `date`; un `datetime`
  no se acepta (pendiente de fechas de la semana 6).
- El nombre del medicamento es obligatorio al guardar (ambigüedad A-6 de la semana 7).
  Es una validación del registro, no de HU-05; queda por confirmar con el cliente.
- Las tablas también tienen `CHECK` para el mínimo y la cantidad, por si alguien escribe
  directamente en la base.

### HU-05 (semana 5)

#### Historia de usuario

**HU-05. Productos bajo el mínimo** (prioridad Must).
Como dueño de la droguería, quiero ver los medicamentos cuya cantidad vigente está por
debajo del mínimo que yo defino para hacer el pedido antes de que se agoten.
Necesidad de origen: N-05, «Del lote nuevo solo quedaban tres cajas y nadie había hecho
el pedido.»

Criterios de aceptación:

- **Escenario 1: Producto bajo el mínimo.** Dado que definí un mínimo de 10 cajas para
  el acetaminofén de 500 mg y solo quedan 3 vigentes del lote L-0627, cuando abro la
  lista de productos por pedir, entonces el acetaminofén aparece con «3 de 10 cajas».
- **Escenario 2 (error): Mínimo inválido.** Dado que estoy configurando el mínimo del
  ibuprofeno de 400 mg, cuando escribo −2, entonces el sistema no lo guarda y muestra
  «El mínimo debe ser un número igual o mayor que cero».

#### Contrato de la función

**Firma**

```python
def productos_por_pedir(
    medicamentos: list[Medicamento],
    lotes: list[Lote],
    hoy: date,
) -> list[ProductoPorPedir]:
```

Los tipos están en `app/reglas/modelos.py`:

| Tipo | Campos |
|---|---|
| `Medicamento` | `id: int`, `nombre: str`, `stock_minimo: int` |
| `Lote` | `medicamento_id: int`, `numero_lote: str`, `fecha_vencimiento: date`, `cantidad_actual: int` |
| `ProductoPorPedir` | `medicamento_id: int`, `nombre: str`, `vigentes: int`, `minimo: int` y la propiedad `texto` («3 de 10 cajas») |

**Qué recibe**

- `medicamentos`: los medicamentos registrados, cada uno con su mínimo (entero ≥ 0).
- `lotes`: los lotes de esos medicamentos, con su fecha de vencimiento y su cantidad
  actual (entero ≥ 0).
- `hoy`: la fecha contra la que se decide qué lote está vencido. Se recibe como
  parámetro para que las pruebas no dependan del día en que se ejecutan.

**Qué devuelve**

Una lista nueva de `ProductoPorPedir` con los medicamentos cuya cantidad vigente es
**menor** que su mínimo, ordenada de menor a mayor cantidad vigente. Si dos tienen la
misma cantidad, se conserva el orden en que llegaron los medicamentos. No modifica las
listas recibidas.

**Supuestos**

1. La cantidad vigente de un medicamento es la suma de `cantidad_actual` de sus lotes
   con `fecha_vencimiento >= hoy`. Un lote que vence hoy todavía cuenta como vigente.
2. Los lotes vencidos no cuentan, aunque todavía no se hayan dado de baja (HU-06).
3. «Por debajo del mínimo» significa estrictamente menor: si la cantidad vigente es igual
   al mínimo, el medicamento no aparece. Queda como pregunta P-12 para el cliente.
4. Un medicamento sin lotes tiene 0 cajas vigentes.
5. Un mínimo de 0 significa «no pedir nunca»: ese medicamento nunca aparece.
6. Solo se usa la librería estándar de Python (ADR-001).

**Casos límite**

| Caso | Resultado |
|---|---|
| Lista de medicamentos vacía | Lista vacía |
| Vigentes igual al mínimo (10 de 10) | No aparece |
| Lote que vence hoy | Cuenta como vigente |
| Todos los lotes vencidos | Aparece con 0 vigentes |
| Medicamento sin lotes | Aparece con 0 vigentes (si su mínimo es mayor que 0) |
| Mínimo igual a 0 | Nunca aparece |

**Errores** (lanza `ValueError`, no devuelve una lista parcial)

| Caso | Mensaje |
|---|---|
| Un medicamento tiene mínimo negativo | «El mínimo debe ser un número igual o mayor que cero» |
| Un lote tiene cantidad negativa | «El lote L-xxxx tiene una cantidad negativa» |
| Un lote es de un medicamento que no está en la lista | «El lote L-xxxx es de un medicamento no registrado» |
| Un mínimo no es un entero (texto, decimal o booleano) — semana 6 | «El mínimo debe ser un número entero de cajas» |
| Una cantidad de lote no es un entero — semana 6 | «El lote L-xxxx tiene una cantidad que no es entera» |
| Dos medicamentos tienen el mismo id — semana 6 | «El medicamento con id N está repetido» |

**Ejemplos** (hoy = 24/10/2026, los mismos datos del documento de requisitos)

| # | Entrada | Salida |
|---|---|---|
| 1 | Acetaminofén, mínimo 10. Lotes: L-0925 con 12 cajas (venció 30/09/2026) y L-0627 con 3 (vence 30/06/2027) | `[Acetaminofén, 3 de 10 cajas]` |
| 2 | Acetaminofén, mínimo 10. Lotes: L-0127 con 15 (vence 31/01/2027) y L-0627 con 3 | `[]` (18 vigentes, no está bajo el mínimo) |
| 3 | Amoxicilina con 8 vigentes y mínimo 10; ibuprofeno con 2 vigentes y mínimo 5 | `[Ibuprofeno 2 de 5, Amoxicilina 8 de 10]` |
| 4 | Loratadina con 10 vigentes y mínimo 10 (límite) | `[]` |
| 5 | `[]` | `[]` |
| 6 | Ibuprofeno con mínimo −2 (error) | `ValueError`: «El mínimo debe ser un número igual o mayor que cero» |

#### Pregunta nueva para el cliente

- **P-12.** Si un medicamento tiene exactamente las cajas del mínimo (por ejemplo, 10 de 10),
  ¿ya lo quiere ver en la lista por pedir? Por ahora no aparece, porque HU-05 dice «por
  debajo del mínimo».
