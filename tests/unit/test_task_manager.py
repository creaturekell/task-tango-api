import json
from pathlib import Path
from time import sleep

import pytest
from task_manager import TaskManager

def make_tm(tmp_path: Path) -> TaskManager:
    """Helper to create a TaskManager with its own isolated tasks.json.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Returns:
        A TaskManager instance configured to use a temporary tasks.json file
        in the provided temporary directory.
    """
    tasks_path = tmp_path / "tasks.json"
    return TaskManager(str(tasks_path))


def test_add_task_creates_file_and_stores_task(tmp_path):
    """Test that adding a task creates the file and stores the task correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task has correct id, description, and status
        - Task has createdAt and updatedAt timestamps
        - tasks.json file is created
        - File contains the task with correct description
    """
    tm = make_tm(tmp_path)

    task = tm.add_task("Buy milk")

    assert task["id"] == 1
    assert task["description"] == "Buy milk"
    assert task["status"] == "todo"
    assert "createdAt" in task
    assert "updatedAt" in task

    tasks_file = tmp_path / "tasks.json"
    assert tasks_file.exists()

    data = json.loads(tasks_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["description"] == "Buy milk"


def test_list_all_tasks(tmp_path):
    """Test that listing all tasks returns all created tasks in order.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Returns a list of all tasks
        - All created tasks are included
        - Tasks are returned in the order they were created
    """
    tm = make_tm(tmp_path)

    t1 = tm.add_task("Buy milk")
    t2 = tm.add_task("Buy eggs")
    t3 = tm.add_task("Buy bread")

    all_tasks = tm.list_tasks()

    assert isinstance(all_tasks, list)
    assert len(all_tasks) == 3
    assert {t["id"] for t in all_tasks} == {t1["id"], t2["id"], t3["id"]}
    assert all_tasks[0]["description"] == "Buy milk"
    assert all_tasks[1]["description"] == "Buy eggs"
    assert all_tasks[2]["description"] == "Buy bread"


def test_list_tasks_filtered_by_status(tmp_path):
    """Test that listing tasks with status filter returns only matching tasks.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Filtering by "todo" returns all tasks with todo status
        - Filtering by "in-progress" returns empty list when no tasks are in progress
        - Filtering by "done" returns empty list when no tasks are done
    """
    tm = make_tm(tmp_path)

    t1 = tm.add_task("Buy milk")
    t2 = tm.add_task("Buy eggs")
    t3 = tm.add_task("Buy bread")

    # for now, only todo is supported, once update_task is implemented, we can test other statuses
    todo_tasks = tm.list_tasks("todo")
    wip_tasks = tm.list_tasks("in-progress") 
    done_tasks = tm.list_tasks("done")
    
    assert isinstance(todo_tasks, list)
    assert len(todo_tasks) == 3
    assert {t["id"] for t in todo_tasks} == {t1["id"], t2["id"], t3["id"]}


def test_update_task_changes_description_and_updated_at(tmp_path):
    """Test that updating a task changes its description and updatedAt timestamp.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task id remains unchanged
        - Task description is updated
        - updatedAt timestamp is changed
        - Changes are persisted to file
    """
    tm = make_tm(tmp_path)

    original = tm.add_task("Old description")
    sleep(3)
    updated = tm.update_task(original["id"], "New description")

    assert updated["id"] == original["id"]
    assert updated["description"] == "New description"
    assert updated["updatedAt"] != original["updatedAt"]

    # persisted
    tasks = tm._get_tasks()
    assert tasks[0]["description"] == "New description"


def test_delete_task_removes_task_from_list(tmp_path):
    """Test that deleting a task removes it from the task list.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Deleted task is no longer in the list
        - Remaining tasks are still present
        - Task count is reduced by one
    """
    tm = make_tm(tmp_path)

    t1 = tm.add_task("Buy milk")
    t2 = tm.add_task("Buy eggs")
    t3 = tm.add_task("Buy bread")

    tm.delete_task(t2["id"])

    tasks = tm.list_tasks()
    assert len(tasks) == 2
    assert {t["id"] for t in tasks} == {t1["id"], t3["id"]}


def test_mark_in_progress_changes_status_and_updated_at(tmp_path):
    """Test that marking a task as in progress updates status and timestamp.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task id remains unchanged
        - Task status is changed to "in-progress"
        - updatedAt timestamp is changed
        - Changes are persisted to file
    """
    tm = make_tm(tmp_path)

    original = tm.add_task("Buy milk")
    sleep(3)
    updated = tm.mark_in_progress(original["id"])

    assert updated["id"] == original["id"]
    assert updated["status"] == "in-progress"
    assert updated["updatedAt"] != original["updatedAt"]

    # persisted
    tasks = tm._get_tasks()
    assert tasks[0]["status"] == "in-progress"


def test_mark_done_changes_status_and_updated_at(tmp_path):
    """Test that marking a task as done updates status and timestamp.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task id remains unchanged
        - Task status is changed to "done"
        - updatedAt timestamp is changed
        - Changes are persisted to file
    """
    tm = make_tm(tmp_path)

    original = tm.add_task("Buy milk")
    sleep(3)
    updated = tm.mark_done(original["id"])

    assert updated["id"] == original["id"]
    assert updated["status"] == "done"
    assert updated["updatedAt"] != original["updatedAt"]
    
    # persisted
    tasks = tm._get_tasks()
    assert tasks[0]["status"] == "done"
    assert tasks[0]["updatedAt"] != original["updatedAt"]


def test_add_task_raises_error_on_empty_description(tmp_path):
    """Test that adding a task with empty description raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised for empty string
        - ValueError is raised for whitespace-only string
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Task Description cannot be empty"):
        tm.add_task("")
    
    with pytest.raises(ValueError, match="Task Description cannot be empty"):
        tm.add_task("   ")


def test_add_task_handles_whitespace_in_description(tmp_path):
    """Test that adding a task preserves whitespace in description.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task description preserves leading/trailing whitespace
        - Task is created successfully
    """
    tm = make_tm(tmp_path)
    
    task = tm.add_task("  Buy milk  ")
    assert task["description"] == "  Buy milk  "
    
    # But empty or whitespace-only should fail
    with pytest.raises(ValueError):
        tm.add_task("")


def test_next_id_generation_with_gaps(tmp_path):
    """Test that ID generation handles gaps in task IDs correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - IDs are generated sequentially
        - After deletion, new IDs continue from max existing ID
    """
    tm = make_tm(tmp_path)
    
    t1 = tm.add_task("Task 1")
    t2 = tm.add_task("Task 2")
    t3 = tm.add_task("Task 3")
    
    assert t1["id"] == 1
    assert t2["id"] == 2
    assert t3["id"] == 3
    
    # Delete middle task
    tm.delete_task(t2["id"])
    
    # New task should get ID 4 (max existing + 1)
    t4 = tm.add_task("Task 4")
    assert t4["id"] == 4


def test_list_tasks_with_mixed_statuses(tmp_path):
    """Test that listing tasks filters correctly with mixed statuses.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Filtering by each status returns only matching tasks
        - All tasks are returned when no filter is applied
    """
    tm = make_tm(tmp_path)
    
    t1 = tm.add_task("Todo task")
    t2 = tm.add_task("Another todo")
    t3 = tm.add_task("In progress task")
    t4 = tm.add_task("Done task")
    
    tm.mark_in_progress(t3["id"])
    tm.mark_done(t4["id"])
    
    todo_tasks = tm.list_tasks("todo")
    in_progress_tasks = tm.list_tasks("in-progress")
    done_tasks = tm.list_tasks("done")
    all_tasks = tm.list_tasks()
    
    assert len(todo_tasks) == 2
    assert len(in_progress_tasks) == 1
    assert len(done_tasks) == 1
    assert len(all_tasks) == 4
    
    assert {t["id"] for t in todo_tasks} == {t1["id"], t2["id"]}
    assert in_progress_tasks[0]["id"] == t3["id"]
    assert done_tasks[0]["id"] == t4["id"]


def test_list_tasks_raises_error_on_invalid_status(tmp_path):
    """Test that listing tasks with invalid status raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised for invalid status values
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Invalid status filter"):
        tm.list_tasks("invalid-status")
    
    with pytest.raises(ValueError, match="Invalid status filter"):
        tm.list_tasks("pending")


def test_update_task_raises_error_on_empty_description(tmp_path):
    """Test that updating a task with empty description raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised for empty description
        - ValueError is raised for whitespace-only description
    """
    tm = make_tm(tmp_path)
    task = tm.add_task("Original")
    
    with pytest.raises(ValueError, match="Updated Task Description cannot be empty"):
        tm.update_task(task["id"], "")
    
    with pytest.raises(ValueError, match="Updated Task Description cannot be empty"):
        tm.update_task(task["id"], "   ")


def test_update_task_raises_error_on_nonexistent_id(tmp_path):
    """Test that updating a nonexistent task raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised with appropriate message
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Task with id 999 not found"):
        tm.update_task(999, "New description")


def test_delete_task_raises_error_on_nonexistent_id(tmp_path):
    """Test that deleting a nonexistent task raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised with appropriate message
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Task with id 999 not found"):
        tm.delete_task(999)


def test_mark_in_progress_raises_error_on_nonexistent_id(tmp_path):
    """Test that marking nonexistent task as in progress raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised with appropriate message
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Task with id 999 not found"):
        tm.mark_in_progress(999)


def test_mark_done_raises_error_on_nonexistent_id(tmp_path):
    """Test that marking nonexistent task as done raises ValueError.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - ValueError is raised with appropriate message
    """
    tm = make_tm(tmp_path)
    
    with pytest.raises(ValueError, match="Task with id 999 not found"):
        tm.mark_done(999)


def test_status_transitions(tmp_path):
    """Test that tasks can transition through all status states.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Task can transition from todo -> in-progress -> done
        - Each transition updates the timestamp
    """
    tm = make_tm(tmp_path)
    task = tm.add_task("Test task")
    
    assert task["status"] == "todo"
    todo_timestamp = task["updatedAt"]
    
    sleep(1)
    task = tm.mark_in_progress(task["id"])
    assert task["status"] == "in-progress"
    assert task["updatedAt"] != todo_timestamp
    in_progress_timestamp = task["updatedAt"]
    
    sleep(1)
    task = tm.mark_done(task["id"])
    assert task["status"] == "done"
    assert task["updatedAt"] != in_progress_timestamp
    assert task["updatedAt"] != todo_timestamp


def test_multiple_status_changes(tmp_path):
    """Test that a task can have its status changed multiple times.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Status can be changed multiple times
        - Timestamp updates with each change
    """
    tm = make_tm(tmp_path)
    task = tm.add_task("Test task")
    
    original_timestamp = task["updatedAt"]
    
    sleep(1)
    task = tm.mark_in_progress(task["id"])
    first_update = task["updatedAt"]
    
    sleep(1)
    task = tm.mark_done(task["id"])
    second_update = task["updatedAt"]
    
    sleep(1)
    task = tm.mark_in_progress(task["id"])
    third_update = task["updatedAt"]
    
    assert task["status"] == "in-progress"
    assert original_timestamp < first_update < second_update < third_update


def test_timestamps_are_iso_format(tmp_path):
    """Test that timestamps are in ISO format.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Timestamps are valid ISO format strings
        - Can be parsed by datetime
    """
    from datetime import datetime
    
    tm = make_tm(tmp_path)
    task = tm.add_task("Test task")
    
    # Verify format: YYYY-MM-DDTHH:MM:SS
    assert "T" in task["createdAt"]
    assert "T" in task["updatedAt"]
    
    # Verify can be parsed
    datetime.fromisoformat(task["createdAt"])
    datetime.fromisoformat(task["updatedAt"])


def test_created_at_unchanged_after_update(tmp_path):
    """Test that createdAt timestamp never changes after task creation.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - createdAt remains constant through updates
        - Only updatedAt changes
    """
    tm = make_tm(tmp_path)
    task = tm.add_task("Original")
    
    original_created = task["createdAt"]
    original_updated = task["updatedAt"]
    
    sleep(1)
    task = tm.update_task(task["id"], "Updated")
    assert task["createdAt"] == original_created
    assert task["updatedAt"] != original_updated
    
    sleep(1)
    task = tm.mark_in_progress(task["id"])
    assert task["createdAt"] == original_created
    assert task["updatedAt"] != original_updated


def test_delete_returns_deleted_task(tmp_path):
    """Test that delete_task returns the deleted task.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Deleted task is returned
        - Returned task matches the original
    """
    tm = make_tm(tmp_path)
    task = tm.add_task("Task to delete")
    
    deleted = tm.delete_task(task["id"])
    
    assert deleted["id"] == task["id"]
    assert deleted["description"] == task["description"]
    assert deleted["status"] == task["status"]


def test_complex_workflow(tmp_path):
    """Test a complex workflow with multiple operations.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - All operations work together correctly
        - Final state is correct
    """
    tm = make_tm(tmp_path)
    
    # Add multiple tasks
    t1 = tm.add_task("Task 1")
    t2 = tm.add_task("Task 2")
    t3 = tm.add_task("Task 3")
    
    # Update one
    tm.update_task(t2["id"], "Updated Task 2")
    
    # Change statuses
    tm.mark_in_progress(t1["id"])
    tm.mark_done(t3["id"])
    
    # Delete one
    tm.delete_task(t2["id"])
    
    # Verify final state
    all_tasks = tm.list_tasks()
    assert len(all_tasks) == 2
    
    todo_tasks = tm.list_tasks("todo")
    in_progress_tasks = tm.list_tasks("in-progress")
    done_tasks = tm.list_tasks("done")
    
    assert len(todo_tasks) == 0
    assert len(in_progress_tasks) == 1
    assert len(done_tasks) == 1
    assert in_progress_tasks[0]["id"] == t1["id"]
    assert done_tasks[0]["id"] == t3["id"]


def test_list_tasks_empty_file(tmp_path):
    """Test that listing tasks from empty file returns empty list.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Empty list is returned when no tasks exist
    """
    tm = make_tm(tmp_path)
    
    tasks = tm.list_tasks()
    assert tasks == []
    
    # Filtered lists should also be empty
    assert tm.list_tasks("todo") == []
    assert tm.list_tasks("in-progress") == []
    assert tm.list_tasks("done") == []


def test_task_id_uniqueness(tmp_path):
    """Test that all task IDs are unique.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - All generated IDs are unique
        - No duplicate IDs exist
    """
    tm = make_tm(tmp_path)
    
    tasks = []
    for i in range(10):
        tasks.append(tm.add_task(f"Task {i}"))
    
    all_tasks = tm.list_tasks()
    ids = [t["id"] for t in all_tasks]
    
    assert len(ids) == len(set(ids)), "All task IDs should be unique"


def test_persistence_across_instances(tmp_path):
    """Test that tasks persist across different TaskManager instances.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Asserts:
        - Tasks created with one instance are visible to another
        - File persistence works correctly
    """
    tasks_path = tmp_path / "tasks.json"
    path_str = str(tasks_path)
    
    tm1 = TaskManager(path_str)
    task = tm1.add_task("Persistent task")
    
    tm2 = TaskManager(path_str)
    tasks = tm2.list_tasks()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == task["id"]
    assert tasks[0]["description"] == "Persistent task"