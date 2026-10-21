import pytest
from pyflow.models import Task, Workflow, WorkflowValidationError


def dummy(inputs, params):
    return 123


def test_task_creation():
    t = Task("step", dummy, frozenset(["prev"]), {"a": 1}, "desc")
    assert t.name == "step"
    assert t.dependencies == frozenset(["prev"])
    assert t.params["a"] == 1
    assert t.description == "desc"


def test_task_empty_name():
    with pytest.raises(ValueError):
        Task("", dummy)
    with pytest.raises(ValueError):
        Task("   ", dummy)


def test_task_non_callable():
    with pytest.raises(TypeError):
        Task("step", "not_callable")


def test_task_self_dependency():
    with pytest.raises(ValueError):
        Task("step", dummy, dependencies=frozenset(["step"]))


def test_task_params_and_deps_immutability():
    input_deps = {"dep1"}
    input_params = {"list": [1, 2]}
    t = Task("step", dummy, dependencies=input_deps, params=input_params)
    input_deps.add("dep2")
    input_params["list"].append(3)
    assert "dep2" not in t.dependencies
    assert t.params["list"] == [1, 2]


def test_workflow_duplicates():
    wf = Workflow()
    t1 = Task("task1", dummy)
    t2 = Task("task1", dummy)
    wf.add_task(t1)
    with pytest.raises(WorkflowValidationError):
        wf.add_task(t2)


def test_workflow_validate_missing_dep():
    wf = Workflow()
    wf.add_task(Task("b", dummy, dependencies=frozenset(["a"])))
    with pytest.raises(WorkflowValidationError):
        wf.validate()


def test_workflow_validate_ok():
    wf = Workflow()
    wf.add_task(Task("a", dummy))
    wf.add_task(Task("b", dummy, dependencies=frozenset(["a"])))
    wf.validate()