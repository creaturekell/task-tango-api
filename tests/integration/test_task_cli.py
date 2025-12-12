"""Integration tests for task_cli.py and task_manager.py interaction."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from task_cli import (
    command_add,
    command_delete,
    command_list,
    command_mark_done,
    command_mark_in_progress,
    command_update,
)
from task_manager import TaskManager


def make_tm_with_path(tmp_path: Path) -> TaskManager:
    """Helper to create a TaskManager with a temporary file path.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        
    Returns:
        A TaskManager instance configured to use a temporary tasks.json file.
    """
    tasks_path = tmp_path / "tasks.json"
    return TaskManager(str(tasks_path))


def test_cli_add_command_integration(tmp_path, capsys):
    """Test that CLI add command integrates with TaskManager correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Task is added via TaskManager
        - Correct output message is printed
        - Task is persisted to file
    """
    tm = make_tm_with_path(tmp_path)
    
    # Patch the global TaskManager instance in task_cli
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'description': 'Buy groceries'})()
        command_add(args)
        
        captured = capsys.readouterr()
        assert "Task added:" in captured.out
        assert "Buy groceries" in captured.out
        
        # Verify task was persisted
        tasks = tm._get_tasks()
        assert len(tasks) == 1
        assert tasks[0]["description"] == "Buy groceries"


def test_cli_list_command_integration_all_tasks(tmp_path, capsys):
    """Test that CLI list command shows all tasks correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - All tasks are listed with correct formatting
        - Output includes task count and separator
    """
    tm = make_tm_with_path(tmp_path)
    
    # Add some tasks
    tm.add_task("Task 1")
    tm.add_task("Task 2")
    tm.add_task("Task 3")
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'status': None})()
        command_list(args)
        
        captured = capsys.readouterr()
        assert "Listing 3 tasks:" in captured.out
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "Task 3" in captured.out
        assert "-" * 40 in captured.out


def test_cli_list_command_integration_filtered_by_status(tmp_path, capsys):
    """Test that CLI list command filters by status correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Only tasks with matching status are shown
        - Correct count is displayed
    """
    tm = make_tm_with_path(tmp_path)
    
    # Add tasks with different statuses
    task1 = tm.add_task("Todo task")
    task2 = tm.add_task("Another todo")
    tm.mark_in_progress(task1["id"])
    tm.mark_done(task2["id"])
    
    with patch('task_cli.tm', tm):
        # Test filtering by in-progress
        args = type('Args', (), {'status': 'in-progress'})()
        command_list(args)
        
        captured = capsys.readouterr()
        assert "Listing 1 tasks:" in captured.out
        assert "Todo task" in captured.out
        assert "in-progress" in captured.out


def test_cli_list_command_integration_no_tasks(tmp_path, capsys):
    """Test that CLI list command handles empty task list correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Appropriate message is shown when no tasks exist
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'status': None})()
        command_list(args)
        
        captured = capsys.readouterr()
        assert "No tasks found." in captured.out


def test_cli_list_command_integration_invalid_status(tmp_path, capsys):
    """Test that CLI list command handles invalid status filter correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for invalid status
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'status': 'invalid-status'})()
        command_list(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Invalid status filter" in captured.out


def test_cli_update_command_integration(tmp_path, capsys):
    """Test that CLI update command integrates with TaskManager correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Task description is updated
        - Correct output message is printed
        - Changes are persisted
    """
    tm = make_tm_with_path(tmp_path)
    task = tm.add_task("Original description")
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': str(task["id"]), 'description': 'Updated description'})()
        command_update(args)
        
        captured = capsys.readouterr()
        assert "Task updated:" in captured.out
        assert "Updated description" in captured.out
        
        # Verify task was updated
        tasks = tm._get_tasks()
        assert tasks[0]["description"] == "Updated description"


def test_cli_update_command_integration_invalid_id(tmp_path, capsys):
    """Test that CLI update command handles invalid task ID correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for invalid ID format
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': 'not-a-number', 'description': 'Test'})()
        command_update(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Invalid task ID" in captured.out


def test_cli_update_command_integration_nonexistent_task(tmp_path, capsys):
    """Test that CLI update command handles nonexistent task ID correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for nonexistent task
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': '999', 'description': 'Test'})()
        command_update(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "not found" in captured.out


def test_cli_delete_command_integration(tmp_path, capsys):
    """Test that CLI delete command integrates with TaskManager correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Task is deleted
        - Correct output message is printed
        - Task is removed from file
    """
    tm = make_tm_with_path(tmp_path)
    task1 = tm.add_task("Task 1")
    task2 = tm.add_task("Task 2")
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': str(task1["id"])})()
        command_delete(args)
        
        captured = capsys.readouterr()
        assert "Task deleted:" in captured.out
        assert str(task1["id"]) in captured.out
        
        # Verify task was deleted
        tasks = tm._get_tasks()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task2["id"]


def test_cli_delete_command_integration_invalid_id(tmp_path, capsys):
    """Test that CLI delete command handles invalid task ID correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for invalid ID format
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': 'invalid'})()
        command_delete(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Invalid task ID" in captured.out


def test_cli_mark_in_progress_command_integration(tmp_path, capsys):
    """Test that CLI mark-in-progress command integrates with TaskManager correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Task status is updated to in-progress
        - Correct output message is printed
        - Changes are persisted
    """
    tm = make_tm_with_path(tmp_path)
    task = tm.add_task("Test task")
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': str(task["id"])})()
        command_mark_in_progress(args)
        
        captured = capsys.readouterr()
        assert "Task marked as in progress:" in captured.out
        assert str(task["id"]) in captured.out
        
        # Verify status was updated
        tasks = tm._get_tasks()
        assert tasks[0]["status"] == "in-progress"


def test_cli_mark_done_command_integration(tmp_path, capsys):
    """Test that CLI mark-done command integrates with TaskManager correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Task status is updated to done
        - Correct output message is printed
        - Changes are persisted
    """
    tm = make_tm_with_path(tmp_path)
    task = tm.add_task("Test task")
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': str(task["id"])})()
        command_mark_done(args)
        
        captured = capsys.readouterr()
        assert "Task marked as done:" in captured.out
        assert str(task["id"]) in captured.out
        
        # Verify status was updated
        tasks = tm._get_tasks()
        assert tasks[0]["status"] == "done"


def test_cli_mark_commands_integration_invalid_id(tmp_path, capsys):
    """Test that CLI mark commands handle invalid task ID correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for invalid ID format
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        # Test mark-in-progress
        args = type('Args', (), {'id': 'not-a-number'})()
        command_mark_in_progress(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Invalid task ID" in captured.out


def test_cli_mark_commands_integration_nonexistent_task(tmp_path, capsys):
    """Test that CLI mark commands handle nonexistent task ID correctly.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Error message is printed for nonexistent task
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        args = type('Args', (), {'id': '999'})()
        command_mark_done(args)
        
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "not found" in captured.out


def test_cli_full_workflow_integration(tmp_path, capsys):
    """Test a complete workflow through the CLI.
    
    Args:
        tmp_path: Pytest temporary directory fixture for isolated test data.
        capsys: Pytest fixture to capture stdout/stderr.
        
    Asserts:
        - Complete workflow (add, list, update, mark, delete) works correctly
        - All operations are properly integrated
    """
    tm = make_tm_with_path(tmp_path)
    
    with patch('task_cli.tm', tm):
        # Add tasks
        args_add1 = type('Args', (), {'description': 'First task'})()
        command_add(args_add1)
        
        args_add2 = type('Args', (), {'description': 'Second task'})()
        command_add(args_add2)
        
        # List all tasks
        args_list = type('Args', (), {'status': None})()
        command_list(args_list)
        
        captured = capsys.readouterr()
        assert "Task added:" in captured.out
        assert "First task" in captured.out
        assert "Second task" in captured.out
        assert "Listing 2 tasks:" in captured.out
        
        # Update a task
        tasks = tm._get_tasks()
        task_id = tasks[0]["id"]
        args_update = type('Args', (), {'id': str(task_id), 'description': 'Updated first task'})()
        command_update(args_update)
        
        # Mark as in progress
        args_mip = type('Args', (), {'id': str(task_id)})()
        command_mark_in_progress(args_mip)
        
        # Mark as done
        command_mark_done(args_mip)
        
        # Delete task
        command_delete(args_mip)
        
        # Verify final state
        final_tasks = tm._get_tasks()
        assert len(final_tasks) == 1
        assert final_tasks[0]["description"] == "Second task"
