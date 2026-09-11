"""
Task registry for cloud-automation-lab.

All automation tasks are registered here and discovered dynamically.
Add new tasks by creating a module in src/tasks/ and registering it with
the @register_task decorator.
"""

from typing import Dict, Callable, Optional

# Task registry: task_name -> (run_function, description)
_registry: Dict[str, tuple] = {}


def register_task(name: str, description: str = ""):
    """Decorator to register a task function in the global registry.

    Args:
        name: Task name (used for CLI and workflow selection)
        description: Human-readable description

    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        _registry[name] = (func, description)
        return func
    return decorator


def get_task(name: str) -> Optional[Callable]:
    """Retrieve a task function by name.

    Args:
        name: Task name

    Returns:
        Task function or None if not found
    """
    entry = _registry.get(name)
    if entry:
        return entry[0]
    return None


def list_tasks() -> Dict[str, str]:
    """List all registered tasks with descriptions.

    Returns:
        Dictionary of task_name -> description
    """
    return {name: desc for name, (_, desc) in _registry.items()}


def get_task_names() -> list:
    """Get all registered task names.

    Returns:
        List of task names
    """
    return list(_registry.keys())


def discover_tasks():
    """Import all task modules to populate the registry.

    Call this once at startup before using get_task() or list_tasks().
    """
    import importlib
    import pkgutil

    import src.tasks as tasks_package

    for importer, modname, ispkg in pkgutil.iter_modules(tasks_package.__path__):
        if modname.startswith("_"):
            continue
        importlib.import_module(f"src.tasks.{modname}")