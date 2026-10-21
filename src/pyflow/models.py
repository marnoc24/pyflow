from dataclasses import dataclass, field
from typing import Callable, Any, Mapping
import copy


class WorkflowValidationError(Exception):
    pass


@dataclass
class Task:
    name: str
    function: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: str | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Task name cannot be empty")

        if not callable(self.function):
            raise TypeError("Function must be callable")

        self.dependencies = frozenset(self.dependencies)
        if self.name in self.dependencies:
            raise ValueError("Task cannot depend on itself")

        self.params = copy.deepcopy(dict(self.params))


class Workflow:
    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise TypeError("Expected Task object")
        if task.name in self.tasks:
            raise WorkflowValidationError(f"Task '{task.name}' already exists in workflow")
        self.tasks[task.name] = task

    def validate(self):
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise WorkflowValidationError(f"Task '{task.name}' depends on unknown task '{dep}'")

        from pyflow.graph import topological_order
        topological_order(self)