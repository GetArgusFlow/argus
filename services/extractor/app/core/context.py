# argus/services/extractor/app/core/context.py

from contextvars import ContextVar
from typing import Dict, Any


class SharedContextManager:
    """
    A wrapper class that provides an intuitive and safe interface
    for managing the request-scoped context (ContextVar).
    """

    def __init__(self):
        # The ContextVar is now a 'private' implementation detail.
        self._context_var: ContextVar[Dict[str, Any]] = ContextVar(
            "shared_context", default={}
        )

    def initialize(self, initial_data: Dict[str, Any]) -> None:
        """Sets the initial context for a new request."""
        self._context_var.set(initial_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves one specific value from the context."""
        return self._context_var.get().get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Retrieves the complete context dictionary."""
        return self._context_var.get()

    def update(self, key: str, value: Any) -> None:
        """
        The method you suggested: update the context safely.
        This performs the 'get -> modify -> set' cycle internally.
        """
        current_context = self._context_var.get().copy()  # Work with a copy
        current_context[key] = value
        self._context_var.set(current_context)


# Create a single global instance of the manager.
# Other modules will import this instance.
shared_context = SharedContextManager()
