#!/usr/bin/env python3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class TaskManager:
    """Core task management logic.
    
    Manages tasks stored in a JSON file with operations for creating, reading,
    updating, and deleting tasks. Each task has an id, description, status,
    createdAt, and updatedAt timestamp.
    """

    STATUS_TODO = "todo"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_DONE = "done"

    VALID_STATUSES = {STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE}

    def __init__(self, path: str = "tasks.json") -> None:
        """Initialize TaskManager with a file path.
        
        Args:
            path: Path to the JSON file where tasks are stored. Defaults to "tasks.json".
        """
        self.path = path

    # -----------------------------------------
    #  Internal Methods
    # -----------------------------------------

    def _next_id(self, tasks: List[Dict[str, Any]]) -> int:
        """Get the next available id.
        
        Args:
            tasks: List of existing tasks.
            
        Returns:
            The next available task id. Returns 1 if tasks list is empty,
            otherwise returns the maximum id + 1.
        """
        return 1 if not tasks else max(t["id"] for t in tasks) + 1


    def _get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from file.
        
        Returns:
            List of task dictionaries. Returns empty list if file doesn't exist
            or contains invalid JSON.
            
        Raises:
            ValueError: If there's an OS error reading the file.
        """
        try:
            with open(self.path,"r",encoding="utf-8") as tf:
                return json.load(tf)
        except FileNotFoundError:
            return [] # File doesn't exist yet
        except json.JSONDecodeError:
            return [] # File is empty or invalid JSON
        except OSError as e:
            raise ValueError(f"Failed to read tasks from {self.path}: {e}")

    def _get_timestamp(self) -> str:
        """Get the current timestamp.
        
        Returns:
            ISO format timestamp string (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().isoformat(timespec="seconds")

    def _find_task(self, tasks: List[Dict[str, Any]], task_id: int) -> Optional[Dict[str, Any]]:
        """Find a task by id.
        
        Args:
            tasks: List of tasks to search through.
            task_id: The id of the task to find.
            
        Returns:
            The task dictionary if found, None otherwise.
        """
        for t in tasks:
            if t["id"] == task_id:
                return t
        return None


    def _save_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Save tasks to file.
        
        Args:
            tasks: List of task dictionaries to save.
            
        Raises:
            ValueError: If there's an error writing to the file.
        """
        try:
            with open(self.path,"w", encoding="utf-8") as tf:
                json.dump(tasks, tf, indent=2)
        except (OSError, json.JSONDecodeError):
            raise ValueError(f"Failed to save tasks to {self.path}")


    def _update_task_status(self, task_id: int, new_status: str) -> Dict[str, Any]:
        """Update the status of a task.
        
        Args:
            task_id: The id of the task to update.
            new_status: The new status value (must be a valid status).
            
        Returns:
            The updated task dictionary.
            
        Raises:
            ValueError: If task with given id is not found or if file save fails.
        """
        tasks = self._get_tasks()
        task = self._find_task(tasks, task_id)
        if task is None:
            raise ValueError(f"Task with id {task_id} not found.")
        
        task["status"] = new_status
        task["updatedAt"] = self._get_timestamp()
        self._save_tasks(tasks)
        return task

    # -----------------------------------------
    #  Public Methods
    # -----------------------------------------


    def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task.
        
        Creates a new task with the given description, assigns it the next
        available id, sets status to "todo", and adds timestamps.
        
        Args:
            description: The task description (must be non-empty after stripping whitespace).
            
        Returns:
            A dictionary representing the newly created task with keys:
            - id: Unique integer identifier
            - description: Task description
            - status: "todo"
            - createdAt: ISO format timestamp
            - updatedAt: ISO format timestamp
            
        Raises:
            ValueError: If description is empty or if file save fails.
        """

        if not description or not description.strip():
            raise ValueError("Task Description cannot be empty.")

        tasks = self._get_tasks()
        new_id = self._next_id(tasks)  # get next available id
        timestamp = self._get_timestamp()
        
        task = {
            "id": new_id,
            "description": description,
            "status": self.STATUS_TODO,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }

        tasks.append(task)
        self._save_tasks(tasks)

        return task


    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status.
        
        Args:
            status: Optional status filter. Must be one of: "todo", "in-progress", "done".
                   If None, returns all tasks.
                   
        Returns:
            List of task dictionaries matching the status filter (or all tasks if
            status is None). Each task dictionary contains: id, description, status,
            createdAt, updatedAt.
            
        Raises:
            ValueError: If status is provided but is not a valid status value.
        """
        
        tasks = self._get_tasks()
        if status is None:
            return tasks
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status filter: {status}")
        
        return [t for t in tasks if t.get("status") == status]  # filter tasks by status


    def update_task(self, id: int, updated_description: str) -> Dict[str, Any]:
        """Update an existing task's description.
        
        Updates the description and updatedAt timestamp of a task with the given id.
        
        Args:
            id: The id of the task to update.
            updated_description: The new description (must be non-empty after stripping whitespace).
            
        Returns:
            The updated task dictionary with the new description and updatedAt timestamp.
            
        Raises:
            ValueError: If description is empty, task with given id is not found,
                       or if file save fails.
        """

        if not updated_description or not updated_description.strip():
            raise ValueError("Updated Task Description cannot be empty.")

        tasks = self._get_tasks()
        task = self._find_task(tasks, id)
        if task is None:
            raise ValueError(f"Task with id {id} not found.")
        
        task["description"] = updated_description
        task["updatedAt"] = self._get_timestamp()

        self._save_tasks(tasks)
        return task


    def delete_task(self, id: int) -> Dict[str, Any]:
        """Delete an existing task.
        
        Removes a task from the task list and saves the updated list to file.
        
        Args:
            id: The id of the task to delete.
            
        Returns:
            The deleted task dictionary.
            
        Raises:
            ValueError: If task with given id is not found or if file save fails.
        """

        tasks = self._get_tasks()
        task = self._find_task(tasks, id)
        if task is None:
            raise ValueError(f"Task with id {id} not found.")
        
        tasks.remove(task)
        self._save_tasks(tasks)
        return task

    def mark_in_progress(self, id: int) -> Dict[str, Any]:
        """Mark a task as in progress.
        
        Updates the task status to "in-progress" and updates the updatedAt timestamp.
        
        Args:
            id: The id of the task to mark as in progress.
            
        Returns:
            The updated task dictionary with status "in-progress" and updated updatedAt.
            
        Raises:
            ValueError: If task with given id is not found or if file save fails.
        """
        return self._update_task_status(id, self.STATUS_IN_PROGRESS)


    def mark_done(self, id: int) -> Dict[str, Any]:
        """Mark a task as done.
        
        Updates the task status to "done" and updates the updatedAt timestamp.
        
        Args:
            id: The id of the task to mark as done.
            
        Returns:
            The updated task dictionary with status "done" and updated updatedAt.
            
        Raises:
            ValueError: If task with given id is not found or if file save fails.
        """
        return self._update_task_status(id, self.STATUS_DONE)