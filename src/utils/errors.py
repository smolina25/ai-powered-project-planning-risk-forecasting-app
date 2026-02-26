class TaskGenerationError(RuntimeError):
    """Raised when task generation via LLM fails or returns invalid output."""


class GraphValidationError(RuntimeError):
    """Raised when task dependencies fail DAG validation."""


class StorageError(RuntimeError):
    """Raised when persistence operations fail."""
