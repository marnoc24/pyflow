from pyflow.models import Workflow, WorkflowValidationError


def _check_missing_deps(workflow: Workflow):
    for task in workflow.tasks.values():
        for dep in task.dependencies:
            if dep not in workflow.tasks:
                raise WorkflowValidationError(f"Task '{task.name}' depends on unregistered task '{dep}'")


def topological_order(workflow: Workflow) -> list[str]:
    _check_missing_deps(workflow)

    in_degree = {name: len(task.dependencies) for name, task in workflow.tasks.items()}
    dependents = {name: [] for name in workflow.tasks}

    for name, task in workflow.tasks.items():
        for dep in task.dependencies:
            dependents[dep].append(name)

    available = sorted([name for name, deg in in_degree.items() if deg == 0])
    order = []

    while available:
        current = available.pop(0)
        order.append(current)

        for nxt in dependents[current]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                available.append(nxt)

        available.sort()

    if len(order) != len(workflow.tasks):
        raise WorkflowValidationError("Cycle detected in workflow")

    return order


def execution_layers(workflow: Workflow) -> list[list[str]]:
    _check_missing_deps(workflow)

    if not workflow.tasks:
        return []

    in_degree = {name: len(task.dependencies) for name, task in workflow.tasks.items()}
    dependents = {name: [] for name in workflow.tasks}

    for name, task in workflow.tasks.items():
        for dep in task.dependencies:
            dependents[dep].append(name)

    current_layer = sorted([name for name, deg in in_degree.items() if deg == 0])
    layers = []
    processed = 0

    while current_layer:
        layers.append(current_layer)
        processed += len(current_layer)
        next_candidates = []

        for node in current_layer:
            for nxt in dependents[node]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    next_candidates.append(nxt)

        current_layer = sorted(next_candidates)

    if processed != len(workflow.tasks):
        raise WorkflowValidationError("Cycle detected in workflow")

    return layers