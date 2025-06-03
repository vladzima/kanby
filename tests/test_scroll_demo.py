#!/usr/bin/env python3
"""
Demo script to verify scroll indicators in column headers.
Creates test data and shows how headers display task counts and ranges.
"""

import os
import sys

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_test_data_small():
    """Create test data with few tasks (no scrolling needed)."""
    return {
        "To Do": [
            {"id": "1", "title": "Review code", "priority": "High"},
            {"id": "2", "title": "Write tests", "priority": "Mid"}
        ],
        "In Progress": [
            {"id": "3", "title": "Implement feature", "priority": "High"}
        ],
        "Done": [
            {"id": "4", "title": "Fix bug", "priority": "Low"}
        ]
    }

def create_test_data_large():
    """Create test data with many tasks (scrolling needed)."""
    return {
        "To Do": [
            {"id": f"task{i}", "title": f"Task {i}: Long task name that might get truncated", "priority": "High" if i % 3 == 0 else "Mid" if i % 3 == 1 else "Low"}
            for i in range(1, 16)  # 15 tasks
        ],
        "In Progress": [
            {"id": f"prog{i}", "title": f"In Progress Task {i}", "priority": "High"}
            for i in range(1, 8)  # 7 tasks
        ],
        "Done": [
            {"id": f"done{i}", "title": f"Completed Task {i}", "priority": "Low"}
            for i in range(1, 12)  # 11 tasks
        ]
    }

def simulate_header_display(data, current_col, current_task, screen_height):
    """Simulate how headers would be displayed with given data."""
    from kanby.main import DEFAULT_COLUMNS, MIN_TASK_DISPLAY_HEIGHT
    
    print(f"\n📱 Screen Height: {screen_height}, Current Column: {current_col}, Current Task: {current_task}")
    print("─" * 60)
    
    for i, col_name in enumerate(DEFAULT_COLUMNS):
        tasks = data.get(col_name, [])
        total_tasks = len(tasks)
        
        # Calculate display parameters (simplified version of the actual logic)
        max_tasks_to_show = max(1, (screen_height - 7) // MIN_TASK_DISPLAY_HEIGHT)
        
        if total_tasks > 0:
            if i == current_col and current_task < total_tasks:
                start_task_idx = max(0, current_task - max_tasks_to_show + 1)
                if start_task_idx + max_tasks_to_show > total_tasks:
                    start_task_idx = max(0, total_tasks - max_tasks_to_show)
            else:
                start_task_idx = 0
            end_task_idx = min(total_tasks, start_task_idx + max_tasks_to_show)
            
            # Create header text
            if max_tasks_to_show >= total_tasks:
                header_text = f"{col_name} ({total_tasks})"
            else:
                visible_start = start_task_idx + 1
                visible_end = end_task_idx
                header_text = f"{col_name} ({visible_start}-{visible_end}/{total_tasks})"
        else:
            header_text = f"{col_name} (0)"
        
        # Show header with indicator if it's the current column
        current_indicator = " 👈 CURRENT" if i == current_col else ""
        print(f"│ {header_text:<25} {current_indicator}")
        
        # Show a few sample tasks
        if total_tasks > 0:
            display_start = start_task_idx
            display_end = min(start_task_idx + 3, end_task_idx)  # Show max 3 for demo
            for idx in range(display_start, display_end):
                task = tasks[idx]
                selected = " ►" if i == current_col and idx == current_task else "  "
                print(f"│{selected} [{task['priority']}] {task['title'][:20]}...")
            if end_task_idx < total_tasks:
                remaining = total_tasks - end_task_idx
                print(f"│   ... and {remaining} more below")
        else:
            print("│   [No tasks]")
        print("│")

def main():
    """Run scroll indicator demo."""
    print("🎯 Kanby Scroll Indicators Demo")
    print("=" * 60)
    print("This demo shows how column headers display task counts and ranges")
    print("when there are more tasks than can fit on screen.")
    print("=" * 60)
    
    print("\n🔹 SCENARIO 1: Small dataset (all tasks visible)")
    print("Expected: Simple count format like 'To Do (2)'")
    small_data = create_test_data_small()
    simulate_header_display(small_data, 0, 0, 25)  # Large screen
    
    print("\n🔹 SCENARIO 2: Large dataset on small screen (scrolling needed)")
    print("Expected: Range format like 'To Do (1-5/15)'")
    large_data = create_test_data_large()
    simulate_header_display(large_data, 0, 0, 15)  # Small screen
    
    print("\n🔹 SCENARIO 3: Scrolled to middle of large dataset")
    print("Expected: Different ranges showing middle tasks")
    simulate_header_display(large_data, 0, 8, 15)  # Selected task in middle
    
    print("\n🔹 SCENARIO 4: Scrolled to end of large dataset")
    print("Expected: Range showing end tasks")
    simulate_header_display(large_data, 0, 14, 15)  # Selected last task
    
    print("\n🔹 SCENARIO 5: Different column selected")
    print("Expected: In Progress column shows range, others show from start")
    simulate_header_display(large_data, 1, 4, 15)  # Focus on In Progress
    
    print("\n✨ Demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("• Headers show simple count (N) when all tasks fit")
    print("• Headers show range (X-Y/N) when scrolling needed") 
    print("• Range updates based on selected task position")
    print("• Each column calculates independently")
    print("• Current column gets priority for optimal task visibility")
    
    print("\n🎮 In the actual app:")
    print("• Use ↑↓ arrows to scroll through tasks")
    print("• Watch headers update as you scroll")
    print("• Switch columns with ←→ arrows")
    print("• Headers will show exactly which tasks are visible")

if __name__ == "__main__":
    main()