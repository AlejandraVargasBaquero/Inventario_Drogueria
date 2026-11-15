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
python -m pytest -v                          # resultado esperado: 23 passed
python -m ruff check --select E,F,B,S .      # resultado esperado: All checks passed!
pip-audit -r requirements.txt                # auditoría de dependencias
```

La configuración de ruff está en `pyproject.toml`. El informe de la revisión de código y
seguridad de la semana 6 está en [revision_seguridad.md](revision_seguridad.md).

## 6. Estructura

La estructura sigue el ADR-001 (aplicación local en capas: interfaz, reglas de
inventario y acceso a datos). Por ahora solo existe la capa de reglas, que no depende de
Flask ni de SQLite y por eso se puede probar sola.

```
inventario-drogueria/
├── app/
│   ├── __init__.py
│   ├── __main__.py            # Demostración: python -m app
│   └── reglas/                # Capa de reglas de inventario
│       ├── __init__.py
│       ├── modelos.py         # Medicamento, Lote y ProductoPorPedir
│       └── pedidos.py         # productos_por_pedir (HU-05)
├── tests/
│   └── test_pedidos.py        # Pruebas de HU-05 (normales, límite, error y abuso)
├── docs/evidencias/           # Capturas de la revisión de la semana 6
├── .env.example               # Plantilla de variables de entorno (sin valores reales)
├── bitacora_ia.md             # Bitácora de uso de IA
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
integrarlo a `main`.

## 8. Autora y licencia

- Autora: Alejandra Vargas Baquero.
- Docente: Jorge Luis Trujillo. Fundación Escuela Tecnológica de Neiva (FET), 2026.
- Licencia: proyecto académico, todos los derechos reservados.

## 9. Funcionalidades

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
