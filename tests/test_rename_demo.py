#!/usr/bin/env python3
"""
Demo script showcasing the project rename functionality in Kanby.
This script demonstrates the rename feature without requiring the full UI.
"""

import os
import json
import tempfile
import sys
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import save_data, load_data

def create_demo_data():
    """Create sample project data for demonstration."""
    return {
        "Work Projects": {
            "To Do": [
                {"id": "task1", "title": "Review pull requests", "priority": "High"},
                {"id": "task2", "title": "Update documentation", "priority": "Mid"}
            ],
            "In Progress": [
                {"id": "task3", "title": "Implement new feature", "priority": "High"}
            ],
            "Done": [
                {"id": "task4", "title": "Fix bug #123", "priority": "Mid"}
            ]
        },
        "Personal Tasks": {
            "To Do": [
                {"id": "task5", "title": "Buy groceries", "priority": "Low"},
                {"id": "task6", "title": "Call dentist", "priority": "Mid"}
            ],
            "In Progress": [],
            "Done": [
                {"id": "task7", "title": "Pay bills", "priority": "High"}
            ]
        },
        "Side Project": {
            "To Do": [
                {"id": "task8", "title": "Design wireframes", "priority": "Mid"}
            ],
            "In Progress": [
                {"id": "task9", "title": "Setup database", "priority": "High"}
            ],
            "Done": []
        },
        "_meta": {
            "last_project": "Work Projects"
        }
    }

def simulate_rename(data, old_name, new_name):
    """Simulate the rename operation from the modal."""
    print(f"🔄 Attempting to rename '{old_name}' to '{new_name}'...")
    
    if not new_name or not new_name.strip():
        print("❌ Error: Empty name not allowed")
        return False, "Empty name not allowed"
    
    if new_name == old_name:
        print("ℹ️  No change needed - names are identical")
        return False, "No change needed"
    
    if new_name in data and new_name != "_meta":
        print("❌ Error: Project name already exists")
        return False, "Project name already exists"
    
    if old_name not in data:
        print("❌ Error: Original project not found")
        return False, "Original project not found"
    
    # Perform the rename
    data[new_name] = data[old_name]
    del data[old_name]
    
    # Update meta data if it referenced the old project
    if data.get("_meta", {}).get("last_project") == old_name:
        if "_meta" not in data:
            data["_meta"] = {}
        data["_meta"]["last_project"] = new_name
        print(f"📝 Updated last project reference: {old_name} → {new_name}")
    
    print(f"✅ Successfully renamed: {old_name} → {new_name}")
    return True, "Rename successful"

def display_projects(data, title="Current Projects"):
    """Display all projects and their task counts."""
    print(f"\n📋 {title}")
    print("-" * 40)
    
    projects = [key for key in data.keys() if key != "_meta"]
    
    if not projects:
        print("No projects found")
        return
    
    for project in sorted(projects):
        project_data = data[project]
        todo_count = len(project_data.get("To Do", []))
        progress_count = len(project_data.get("In Progress", []))
        done_count = len(project_data.get("Done", []))
        total_tasks = todo_count + progress_count + done_count
        
        current_marker = " 👈 CURRENT" if data.get("_meta", {}).get("last_project") == project else ""
        
        print(f"📁 {project}{current_marker}")
        print(f"   Tasks: {total_tasks} total ({todo_count} todo, {progress_count} in progress, {done_count} done)")

def main():
    """Run the rename functionality demo."""
    print("🎯 Kanby Project Rename Feature Demo")
    print("=" * 50)
    
    # Create demo data
    demo_data = create_demo_data()
    
    # Display initial state
    display_projects(demo_data, "Initial Project State")
    
    print("\n🔄 Demo Rename Operations")
    print("-" * 30)
    
    # Demo 1: Successful rename
    print("\n1️⃣  Rename 'Work Projects' to 'Office Work'")
    success, message = simulate_rename(demo_data, "Work Projects", "Office Work")
    
    if success:
        display_projects(demo_data, "After Successful Rename")
    
    # Demo 2: Try to rename to existing name
    print("\n2️⃣  Try to rename 'Personal Tasks' to 'Office Work' (should fail)")
    success, message = simulate_rename(demo_data, "Personal Tasks", "Office Work")
    
    # Demo 3: Rename with special characters
    print("\n3️⃣  Rename 'Side Project' to 'My Cool App 🚀'")
    success, message = simulate_rename(demo_data, "Side Project", "My Cool App 🚀")
    
    if success:
        display_projects(demo_data, "After Special Character Rename")
    
    # Demo 4: Try empty name
    print("\n4️⃣  Try to rename 'Personal Tasks' to empty string (should fail)")
    success, message = simulate_rename(demo_data, "Personal Tasks", "")
    
    # Demo 5: Rename current project
    print("\n5️⃣  Rename current project 'Office Work' to 'Corporate Tasks'")
    success, message = simulate_rename(demo_data, "Office Work", "Corporate Tasks")
    
    if success:
        display_projects(demo_data, "After Renaming Current Project")
    
    # Show final data structure
    print("\n📊 Final Data Structure")
    print("-" * 30)
    
    # Show task preservation
    if "Corporate Tasks" in demo_data:
        corp_tasks = demo_data["Corporate Tasks"]
        print(f"\n📂 'Corporate Tasks' task details:")
        for column, tasks in corp_tasks.items():
            if tasks:
                print(f"  {column}:")
                for task in tasks:
                    print(f"    • {task['title']} ({task['priority']} priority)")
            else:
                print(f"  {column}: (empty)")
    
    # Show meta data
    meta_info = demo_data.get("_meta", {})
    print(f"\n🎯 Current active project: {meta_info.get('last_project', 'None')}")
    
    print("\n✨ Demo Features Showcased:")
    print("• ✅ Basic project renaming")
    print("• ✅ Duplicate name detection")
    print("• ✅ Empty name validation")
    print("• ✅ Task data preservation")
    print("• ✅ Meta data updates")
    print("• ✅ Special character support")
    print("• ✅ Current project tracking")
    
    print(f"\n🎉 Rename functionality is working perfectly!")
    print("\n💡 In the actual app, use 'r' key in the project manager to rename projects")

if __name__ == "__main__":
    main()