"""Repositorio SQLite (en construcción: primero van las pruebas)."""


def conectar(ruta):
    raise NotImplementedError


def crear_esquema(con):
    raise NotImplementedError


def guardar_medicamento(con, nombre, stock_minimo):
    raise NotImplementedError


def cambiar_minimo(con, medicamento_id, nuevo_minimo):
    raise NotImplementedError


def guardar_lote(con, medicamento_id, numero_lote, fecha_vencimiento, cantidad):
    raise NotImplementedError


def listar_medicamentos(con):
    raise NotImplementedError


def listar_lotes(con):
    raise NotImplementedError
