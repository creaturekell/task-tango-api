#! /usr/bin/env python3
import argparse
from task_manager import TaskManager

tm = TaskManager()

def command_add(args: argparse.Namespace) -> None:
    """Add a new task.
    
    Args:
        args: Argument namespace containing:
            - description: The task description to add.
            
    Prints:
        A confirmation message with the task id, description, and status.
        
    Raises:
        ValueError: If task description is empty or file save fails.
    """
    t = tm.add_task(args.description)
    print(f"Task added: {t['id']} - {t['description']} - {t['status']}")


def command_list(args: argparse.Namespace) -> None:
    """List all tasks, optionally filtered by status.
    
    Args:
        args: Argument namespace containing:
            - status: Optional status filter ("todo", "in-progress", or "done").
            
    Prints:
        A formatted list of tasks with their id, description, and status.
        If no tasks are found, prints an appropriate message.
        
    Raises:
        ValueError: If status is provided but is not a valid status value.
    """
    status = args.status # optional status filter

    try:
        tasks = tm.list_tasks(status=status)
    except ValueError as e:
        print(f"Error: {e}")
        return

    if not tasks:
        if status:
            print(f"No tasks found with status: {status}.")
        else:
            print("No tasks found.")
        return

    print(f"\nListing {len(tasks)} tasks:")
    print("-" * 40)
    for t in tasks:
        print(f"{t['id']} - {t['description']} - {t['status']}")

    print("\n")


def command_update(args: argparse.Namespace) -> None:
    """Update an existing task's description.
    
    Args:
        args: Argument namespace containing:
            - id: The task id to update (must be a valid integer).
            - description: The new task description.
            
    Prints:
        A confirmation message with the updated task id, description, and status.
        If an error occurs, prints an error message.
    """
    try: 
        task_id = int(args.id)
    except ValueError:
        print(f"Error: Invalid task ID: {args.id}")
        return
    
    try:
        t = tm.update_task(task_id, args.description)
        print(f"Task updated: {t['id']} - {t['description']} - {t['status']}")
    except ValueError as e:
        print(f"Error: {e}")
        return


def command_delete(args: argparse.Namespace) -> None:
    """Delete an existing task.
    
    Args:
        args: Argument namespace containing:
            - id: The task id to delete (must be a valid integer).
            
    Prints:
        A confirmation message with the deleted task id.
        If an error occurs, prints an error message.
    """
    try:
        task_id = int(args.id)
    except ValueError:
        print(f"Error: Invalid task ID: {args.id}")
        return
    
    try:
        tm.delete_task(task_id)
        print(f"Task deleted: {task_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return


def command_mark_in_progress(args: argparse.Namespace) -> None:
    """Mark a task as in progress.
    
    Args:
        args: Argument namespace containing:
            - id: The task id to mark as in progress (must be a valid integer).
            
    Prints:
        A confirmation message with the task id.
        If an error occurs, prints an error message.
    """
    try:
        task_id = int(args.id)
    except ValueError:
        print(f"Error: Invalid task ID: {args.id}")
        return
    
    try:
        tm.mark_in_progress(task_id)
        print(f"Task marked as in progress: {task_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return


def command_mark_done(args: argparse.Namespace) -> None:
    """Mark a task as done.
    
    Args:
        args: Argument namespace containing:
            - id: The task id to mark as done (must be a valid integer).
            
    Prints:
        A confirmation message with the task id.
        If an error occurs, prints an error message.
    """
    try:
        task_id = int(args.id)
    except ValueError:
        print(f"Error: Invalid task ID: {args.id}")
        return
    
    try:
        tm.mark_done(task_id)
        print(f"Task marked as done: {task_id}")
    except ValueError as e:
        print(f"Error: {e}")
        return


def command_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser.
    
    Sets up subcommands for task management operations:
    - add: Add a new task
    - list: List tasks (optionally filtered by status)
    - update: Update a task's description
    - delete: Delete a task
    - mark-in-progress: Mark a task as in progress
    - mark-done: Mark a task as done
    
    Returns:
        Configured ArgumentParser instance with all subcommands and their
        respective arguments set up.
    """
    parser = argparse.ArgumentParser(
        description="Task Manager CLI.",
        usage="%(prog)s <command> [inputs/options]"   
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add 
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("description", help="Description of the task")
    p_add.set_defaults(func=command_add)

    # list
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument("status", nargs="?", help="Optional status filter: todo, in-progress, done")
    p_list.set_defaults(func=command_list)

    # update
    p_update = subparsers.add_parser("update", help="Update an existing task")
    p_update.add_argument("id", help="ID of the task to update")
    p_update.add_argument("description", help="New description")
    p_update.set_defaults(func=command_update)

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a task")
    p_delete.add_argument("id", help="ID of the task to delete")
    p_delete.set_defaults(func=command_delete)

    # mark-in-progress
    p_mip = subparsers.add_parser("mark-in-progress", help="Mark task as in progress")
    p_mip.add_argument("id", help="ID of the task")
    p_mip.set_defaults(func=command_mark_in_progress)

    # mark-done
    p_md = subparsers.add_parser("mark-done", help="Mark task as done")
    p_md.add_argument("id", help="ID of the task")
    p_md.set_defaults(func=command_mark_done)

    return parser 


def main() -> None:
    """Main entry point for the CLI application.
    
    Parses command-line arguments and executes the appropriate command function.
    The subparser attaches a 'func' attribute to the args namespace that
    corresponds to the selected subcommand.
    """
    args = command_parser().parse_args()
    # subparsers attach a 'func' attribute 
    args.func(args)


if __name__ == "__main__":
    main()