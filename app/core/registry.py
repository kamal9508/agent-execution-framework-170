"""Tool registry for workflow execution."""
from typing import Dict, Callable, Any


class ToolRegistry:
    """Registry for workflow tools."""

    def __init__(self):
        """Initialize registry."""
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """Register a tool.

        Args:
            name: Tool name
            func: Tool function
        """
        self._tools[name] = func

    def get(self, name: str) -> Callable | None:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None
        """
        return self._tools.get(name)

    def list(self) -> Dict[str, Callable]:
        """List all registered tools.

        Returns:
            Dictionary of tools
        """
        return self._tools.copy()

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()


tool_registry = ToolRegistry()




