import pytest
from pyflow.models import Task, Workflow, WorkflowValidationError
from pyflow.graph import topological_order, execution_layers


def dummy(inputs, params):
    return None


def test_empty_workflow():
    wf = Workflow()
    assert topological_order(wf) == []
    assert execution_layers(wf) == []


def test_single_task():
    wf = Workflow()
    wf.add_task(Task("single", dummy))
    assert topological_order(wf) == ["single"]
    assert execution_layers(wf) == [["single"]]


def test_chain():
    wf = Workflow()
    wf.add_task(Task("c", dummy, dependencies=frozenset(["b"])))
    wf.add_task(Task("a", dummy))
    wf.add_task(Task("b", dummy, dependencies=frozenset(["a"])))
    assert topological_order(wf) == ["a", "b", "c"]
    assert execution_layers(wf) == [["a"], ["b"], ["c"]]


def test_independent_tasks():
    wf = Workflow()
    wf.add_task(Task("z", dummy))
    wf.add_task(Task("a", dummy))
    wf.add_task(Task("m", dummy))
    assert topological_order(wf) == ["a", "m", "z"]
    assert execution_layers(wf) == [["a", "m", "z"]]


def test_specification_layers_example():
    wf = Workflow()
    wf.add_task(Task("extract", dummy))
    wf.add_task(Task("clean_b", dummy, dependencies=frozenset(["extract"])))
    wf.add_task(Task("clean_a", dummy, dependencies=frozenset(["extract"])))
    wf.add_task(Task("report", dummy, dependencies=frozenset(["clean_a", "clean_b"])))

    assert topological_order(wf) == ["extract", "clean_a", "clean_b", "report"]
    assert execution_layers(wf) == [["extract"], ["clean_a", "clean_b"], ["report"]]


def test_simple_cycle():
    wf = Workflow()
    wf.add_task(Task("t1", dummy, dependencies=frozenset(["t2"])))
    wf.add_task(Task("t2", dummy, dependencies=frozenset(["t1"])))
    with pytest.raises(WorkflowValidationError):
        topological_order(wf)
    with pytest.raises(WorkflowValidationError):
        execution_layers(wf)


def test_three_node_cycle():
    wf = Workflow()
    wf.add_task(Task("a", dummy, dependencies=frozenset(["c"])))
    wf.add_task(Task("b", dummy, dependencies=frozenset(["a"])))
    wf.add_task(Task("c", dummy, dependencies=frozenset(["b"])))
    with pytest.raises(WorkflowValidationError):
        topological_order(wf)
    with pytest.raises(WorkflowValidationError):
        execution_layers(wf)


def test_missing_dependency():
    wf = Workflow()
    wf.add_task(Task("task", dummy, dependencies=frozenset(["missing"])))
    with pytest.raises(WorkflowValidationError):
        topological_order(wf)
    with pytest.raises(WorkflowValidationError):
        execution_layers(wf)