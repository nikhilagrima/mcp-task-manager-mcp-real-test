from fastmcp import FastMCP
import os
import json
from datetime import datetime

# Initialize MCP server
mcp = FastMCP("Task Manager MCP Server")

# In-memory task storage (in production, this would be a database)
tasks = {}
task_counter = 0

@mcp.tool()
def create_task(title: str, description: str, priority: str = "medium") -> dict:
    """Create a new task with title, description, and priority"""
    global task_counter
    task_counter += 1
    
    task_id = f"task_{task_counter}"
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    tasks[task_id] = task
    return {
        "success": True,
        "message": f"Task created successfully",
        "task": task
    }

@mcp.tool()
def list_tasks(status: str = "all", priority: str = "all") -> dict:
    """List all tasks, optionally filtered by status and priority"""
    filtered_tasks = []
    
    for task in tasks.values():
        if status != "all" and task["status"] != status:
            continue
        if priority != "all" and task["priority"] != priority:
            continue
        filtered_tasks.append(task)
    
    return {
        "total": len(filtered_tasks),
        "tasks": filtered_tasks,
        "filters": {
            "status": status,
            "priority": priority
        }
    }

@mcp.tool()
def update_task_status(task_id: str, status: str) -> dict:
    """Update the status of a task (pending, in_progress, completed)"""
    if task_id not in tasks:
        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }
    
    valid_statuses = ["pending", "in_progress", "completed"]
    if status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }
    
    tasks[task_id]["status"] = status
    if status == "completed":
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": f"Task {task_id} status updated to {status}",
        "task": tasks[task_id]
    }

@mcp.tool()
def delete_task(task_id: str) -> dict:
    """Delete a task by ID"""
    if task_id not in tasks:
        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }
    
    deleted_task = tasks.pop(task_id)
    return {
        "success": True,
        "message": f"Task {task_id} deleted successfully",
        "deleted_task": deleted_task
    }

@mcp.tool()
def get_task_stats() -> dict:
    """Get statistics about all tasks"""
    total = len(tasks)
    by_status = {"pending": 0, "in_progress": 0, "completed": 0}
    by_priority = {"low": 0, "medium": 0, "high": 0}
    
    for task in tasks.values():
        by_status[task["status"]] = by_status.get(task["status"], 0) + 1
        by_priority[task["priority"]] = by_priority.get(task["priority"], 0) + 1
    
    return {
        "total_tasks": total,
        "by_status": by_status,
        "by_priority": by_priority
    }

@mcp.resource("tasks://all")
def get_all_tasks_resource():
    """Get all tasks as a resource"""
    return {
        "tasks": list(tasks.values()),
        "count": len(tasks)
    }

@mcp.resource("tasks://stats")
def get_stats_resource():
    """Get task statistics as a resource"""
    return get_task_stats()

@mcp.prompt()
def task_summary_prompt(task_id: str) -> str:
    """Generate a summary prompt for a specific task"""
    if task_id not in tasks:
        return f"Task {task_id} not found"
    
    task = tasks[task_id]
    return f"""Task Summary:
Title: {task['title']}
Description: {task['description']}
Priority: {task['priority']}
Status: {task['status']}
Created: {task['created_at']}
Completed: {task['completed_at'] or 'Not completed'}

Please analyze this task and provide recommendations for completion."""
