"""Jerarquía pública de excepciones de chile-hub."""


class ChileHubError(Exception):
    """Clase base para errores de ejecución esperados de chile-hub."""


class ChileHubDataError(ChileHubError, RuntimeError):
    """Se lanza cuando los datos de una release no pueden resolverse o verificarse."""


class _ChileHubKeyError(ChileHubError, KeyError):
    """Variante de KeyError con representación de cadena para el usuario."""

    def __str__(self) -> str:
        if not self.args:
            return ""
        return str(self.args[0])


class ChileHubDatasetError(_ChileHubKeyError):
    """Se lanza cuando un nombre de dataset no está registrado en el catálogo."""


class ChileHubOutputError(_ChileHubKeyError):
    """Se lanza cuando un tipo de salida de dataset no está disponible."""


class ChileHubExampleError(_ChileHubKeyError):
    """Se lanza cuando un tipo de ejemplo no está disponible para un dataset."""
