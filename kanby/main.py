import json
import os
import time
import uuid
import argparse
import sys
import signal

# Windows curses compatibility
try:
    import curses
    import curses.textpad
except ImportError:
    try:
        import windows_curses as curses
        import curses.textpad
    except ImportError:
        print("Error: curses library not available.")
        print("For Windows users, please install: pip install windows-curses")
        print("For other systems, curses should be available by default.")
        sys.exit(1)

# --- Package Info ---
__version__ = "1.0.21"
__author__ = "Vlad Arbatov"
__description__ = "A beautiful terminal-based Kanban board"

# --- Configuration ---
DATA_FILE = "kanby_data.json"
DEFAULT_COLUMNS = ["To Do", "In Progress", "Done"]
DEFAULT_PROJECT_NAME = "Default Project"
DEFAULT_COLUMN_WIDTH = 30
MIN_TASK_DISPLAY_HEIGHT = 1 # For single-line Priority + Title format
EMPTY_COLUMN_TEXT = "[No tasks]"
PRIORITIES = ["Low", "Mid", "High"]
DEFAULT_PRIORITY = "Mid"

# --- Color Pair Definitions ---
COLOR_PAIR_PROJECT_NAME = 1
COLOR_PAIR_HEADER = 2
COLOR_PAIR_ACTIVE_HEADER = 3
COLOR_PAIR_SELECTED_TASK = 4
COLOR_PAIR_MESSAGE_INFO = 5
COLOR_PAIR_MESSAGE_ERROR = 6
COLOR_PAIR_BORDER = 7
COLOR_PAIR_MODAL_BORDER = 9
COLOR_PAIR_MODAL_TEXT = 10
COLOR_PAIR_MODAL_SELECTED_ITEM = 11
COLOR_PAIR_MODAL_HEADER = 12
COLOR_PAIR_PRIO_LOW = 13
COLOR_PAIR_PRIO_MID = 14
COLOR_PAIR_PRIO_HIGH = 15

# Splash screen colors
COLOR_PAIR_SPLASH_LOGO = 20
COLOR_PAIR_SPLASH_TAGLINE = 21
COLOR_PAIR_SPLASH_VERSION = 22
COLOR_PAIR_SPLASH_LOADING = 23

# --- Helper Functions ---
def is_key_pressed(key, target_char):
    """
    Simple keyboard detection for ASCII characters only.

    Args:
        key: The key code returned by curses getch()
        target_char: The target character (e.g., 'q', 'p', 'a')

    Returns:
        bool: True if the key matches the target character
    """
    if not isinstance(target_char, str) or len(target_char) != 1:
        return False

    target_lower = target_char.lower()
    target_upper = target_char.upper()

    # Check ASCII characters only
    return key == ord(target_lower) or key == ord(target_upper)

def show_splash_screen(stdscr):
    """Display a cool splash screen on startup."""
    # Get terminal dimensions
    height, width = stdscr.getmaxyx()

    # Kanby ASCII art
    splash_art = [
        "██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗   ██╗",
        "██║ ██╔╝██╔══██╗████╗  ██║██╔══██╗╚██╗ ██╔╝",
        "█████╔╝ ███████║██╔██╗ ██║██████╔╝ ╚████╔╝ ",
        "██╔═██╗ ██╔══██║██║╚██╗██║██╔══██╗  ╚██╔╝  ",
        "██║  ██╗██║  ██║██║ ╚████║██████╔╝   ██║   ",
        "╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝    ╚═╝   "
    ]

    tagline = "Your Beautiful Terminal Kanban Board. Vlad Arbatov 2025"
    version_text = f"v{__version__}"
    loading_text = "Loading your projects..."

    # Clear screen
    stdscr.clear()

    # Calculate positions for centering
    art_start_y = max(0, (height - len(splash_art) - 6) // 2)

    # Initialize colors for splash
    if curses.has_colors():
        try:
            curses.init_pair(COLOR_PAIR_SPLASH_LOGO, curses.COLOR_CYAN, -1)
            curses.init_pair(COLOR_PAIR_SPLASH_TAGLINE, curses.COLOR_YELLOW, -1)
            curses.init_pair(COLOR_PAIR_SPLASH_VERSION, curses.COLOR_GREEN, -1)
            curses.init_pair(COLOR_PAIR_SPLASH_LOADING, curses.COLOR_MAGENTA, -1)
        except curses.error:
            pass

    try:
        # Draw ASCII art
        for i, line in enumerate(splash_art):
            if art_start_y + i < height - 1:
                x_pos = max(0, (width - len(line)) // 2)
                if curses.has_colors():
                    stdscr.addstr(art_start_y + i, x_pos, line, curses.color_pair(COLOR_PAIR_SPLASH_LOGO) | curses.A_BOLD)
                else:
                    stdscr.addstr(art_start_y + i, x_pos, line, curses.A_BOLD)

        # Draw tagline
        tagline_y = art_start_y + len(splash_art) + 1
        if tagline_y < height - 3:
            x_pos = max(0, (width - len(tagline)) // 2)
            if curses.has_colors():
                stdscr.addstr(tagline_y, x_pos, tagline, curses.color_pair(COLOR_PAIR_SPLASH_TAGLINE))
            else:
                stdscr.addstr(tagline_y, x_pos, tagline)

        # Draw version
        version_y = tagline_y + 1
        if version_y < height - 2:
            x_pos = max(0, (width - len(version_text)) // 2)
            if curses.has_colors():
                stdscr.addstr(version_y, x_pos, version_text, curses.color_pair(COLOR_PAIR_SPLASH_VERSION))
            else:
                stdscr.addstr(version_y, x_pos, version_text)

        # Draw loading text with animation
        loading_y = version_y + 2
        if loading_y < height - 1:
            x_pos = max(0, (width - len(loading_text)) // 2)

            # Animated loading
            for i in range(4):
                dots = "." * i
                animated_text = loading_text + dots
                try:
                    if curses.has_colors():
                        stdscr.addstr(loading_y, x_pos, animated_text.ljust(len(loading_text) + 3), curses.color_pair(COLOR_PAIR_SPLASH_LOADING))
                    else:
                        stdscr.addstr(loading_y, x_pos, animated_text.ljust(len(loading_text) + 3))
                    stdscr.refresh()
                    time.sleep(0.3)
                except curses.error:
                    pass

    except curses.error:
        # If screen is too small or other curses error, just show a simple message
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, "KANBY - Terminal Kanban Board")
            stdscr.addstr(1, 0, f"Version {__version__}")
            stdscr.addstr(2, 0, "Loading...")
            stdscr.refresh()
            time.sleep(1.0)
        except curses.error:
            pass

def generate_id():
    """Generates a unique ID for tasks."""
    return str(uuid.uuid4())[:8]

def load_data():
    """Loads all projects and their tasks from the JSON data file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            # Ensure data is not empty and has the new project structure
            if not data:
                 data = {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}

            # Extract metadata if it exists
            meta_data = data.pop("_meta", {})

            # Basic check for old format (dictionary of lists) vs new (dictionary of dictionaries of lists)
            # and migrates if necessary.
            if not all(isinstance(val, dict) and DEFAULT_COLUMNS[0] in val for val in data.values() if val):
                migrated_data = {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}
                # Attempt to migrate tasks from old format if it looks like column names are keys
                for col_name_old_format, tasks_list in data.items():
                    if col_name_old_format in DEFAULT_COLUMNS: # If old key is a default column name
                         migrated_data[DEFAULT_PROJECT_NAME][col_name_old_format] = tasks_list
                    elif isinstance(tasks_list, list): # If it's a list of tasks not under a known column
                         # Add these tasks to the first default column of the default project
                         migrated_data[DEFAULT_PROJECT_NAME][DEFAULT_COLUMNS[0]].extend(
                            task for task in tasks_list if isinstance(task, dict) # Ensure tasks are dicts
                         )
                data = migrated_data

            # Ensure all default columns exist for each project and tasks have IDs and priorities
            final_data = {}
            project_keys = list(data.keys()) # Get project names (excluding _meta)
            if not project_keys: # If there are no projects after loading (e.g. empty file or failed migration)
                project_keys = [DEFAULT_PROJECT_NAME]
                data[DEFAULT_PROJECT_NAME] = {} # Ensure default project key exists if data was empty

            for p_name in project_keys:
                project_content = data.get(p_name, {}) # Get current project's content or empty dict
                final_data[p_name] = {} # Initialize project in final_data
                for col_name in DEFAULT_COLUMNS:
                    final_data[p_name][col_name] = [] # Initialize column in project
                    tasks_in_col = project_content.get(col_name, []) # Get tasks for this column or empty list
                    for task in tasks_in_col:
                        if isinstance(task, dict): # Ensure task is a dictionary
                            if "id" not in task:
                                task["id"] = generate_id()
                            if "priority" not in task:
                                task["priority"] = DEFAULT_PRIORITY
                            final_data[p_name][col_name].append(task)

            # Add back metadata
            if meta_data:
                final_data["_meta"] = meta_data

            if not final_data or not any(key != "_meta" for key in final_data.keys()): # Should be caught by project_keys check, but as a fallback
                final_data = {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}
            return final_data
        except json.JSONDecodeError:
            # If file is corrupted or not valid JSON, return a default structure
            return {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}
    # If file doesn't exist, return a default structure
    return {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}


def save_data(all_projects_data):
    """Saves all projects and tasks to the JSON data file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(all_projects_data, f, indent=4)

def save_last_project_to_data(all_projects_data, project_name):
    """Save the last opened project name in the data structure."""
    if "_meta" not in all_projects_data:
        all_projects_data["_meta"] = {}
    all_projects_data["_meta"]["last_project"] = project_name

def load_last_project_from_data(all_projects_data):
    """Load the last opened project name from the data structure."""
    return all_projects_data.get("_meta", {}).get("last_project")

def get_input(stdscr, y, x, prompt, initial_value="", color_pair=0, input_width=30):
    """Gets input from the user at a specified position with a prompt."""
    try:
        stdscr.addstr(y, x, prompt, color_pair)
        stdscr.refresh()
        # Create a text input window
        input_win = curses.newwin(1, input_width, y, x + len(prompt))
        input_win.addstr(0, 0, initial_value)
        input_win.refresh()
        textbox = curses.textpad.Textbox(input_win)

        # Enable editing
        curses.curs_set(1)  # Show cursor
        result = textbox.edit().strip()
        curses.curs_set(0)  # Hide cursor

        return result
    except curses.error:
        curses.curs_set(0)
        return initial_value

def display_message(stdscr, message, duration=1.5, color_pair=0):
    """Displays a temporary message at the bottom of the screen."""
    height, width = stdscr.getmaxyx()
    try:
        # Clear the message area
        stdscr.addstr(height - 1, 0, " " * (width - 1))
        # Display the message
        stdscr.addstr(height - 1, 0, message[:width-1], color_pair)
        stdscr.refresh()
        time.sleep(duration)
        # Clear the message
        stdscr.addstr(height - 1, 0, " " * (width - 1))
        stdscr.refresh()
    except curses.error:
        pass

def manage_projects_modal(stdscr, all_projects_data, current_project_name, has_colors):
    """Display a modal for managing projects."""
    height, width = stdscr.getmaxyx()

    # Modal dimensions
    modal_height = min(20, height - 4)
    modal_width = min(60, width - 4)
    modal_y = (height - modal_height) // 2
    modal_x = (width - modal_width) // 2

    # Create modal window
    modal_win = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal_win.keypad(True)  # Enable keypad to capture arrow keys properly

    project_names = [key for key in all_projects_data.keys() if key != "_meta"]
    selected_idx = 0
    if current_project_name in project_names:
        selected_idx = project_names.index(current_project_name)

    while True:
        modal_win.clear()

        # Draw border
        if has_colors:
            modal_win.box(curses.ACS_VLINE, curses.ACS_HLINE)
            modal_win.addstr(0, 2, " Project Manager ", curses.color_pair(COLOR_PAIR_MODAL_HEADER) | curses.A_BOLD)
        else:
            modal_win.box()
            modal_win.addstr(0, 2, " Project Manager ", curses.A_BOLD)

        # Instructions
        instructions = [
            "↑/↓: Navigate",
            "Enter: Select project",
            "n: New project",
            "r: Rename project",
            "d: Delete project",
            "q: Cancel"
        ]

        start_y = 2
        for i, instruction in enumerate(instructions):
            if start_y + i < modal_height - 1:
                if has_colors:
                    modal_win.addstr(start_y + i, 2, instruction, curses.color_pair(COLOR_PAIR_MODAL_TEXT))
                else:
                    modal_win.addstr(start_y + i, 2, instruction)

        # Project list
        list_start_y = start_y + len(instructions) + 1
        if list_start_y < modal_height - 1:
            if has_colors:
                modal_win.addstr(list_start_y, 2, "Projects:", curses.color_pair(COLOR_PAIR_MODAL_HEADER) | curses.A_BOLD)
            else:
                modal_win.addstr(list_start_y, 2, "Projects:", curses.A_BOLD)

            for i, project_name in enumerate(project_names):
                if list_start_y + 1 + i < modal_height - 1:
                    display_name = project_name[:modal_width - 6]  # Truncate if too long
                    if i == selected_idx:
                        if has_colors:
                            modal_win.addstr(list_start_y + 1 + i, 2, f"> {display_name}", curses.color_pair(COLOR_PAIR_MODAL_SELECTED_ITEM))
                        else:
                            modal_win.addstr(list_start_y + 1 + i, 2, f"> {display_name}", curses.A_REVERSE)
                    else:
                        if has_colors:
                            modal_win.addstr(list_start_y + 1 + i, 2, f"  {display_name}", curses.color_pair(COLOR_PAIR_MODAL_TEXT))
                        else:
                            modal_win.addstr(list_start_y + 1 + i, 2, f"  {display_name}")

        modal_win.refresh()

        key = modal_win.getch()

        if key == curses.KEY_UP:
            if selected_idx > 0:
                selected_idx -= 1
        elif key == curses.KEY_DOWN:
            if selected_idx < len(project_names) - 1:
                selected_idx += 1
        elif key == ord('\n') or key == curses.KEY_ENTER:
            # Select project
            if project_names:
                return project_names[selected_idx]
            return current_project_name
        elif is_key_pressed(key, 'n'):
            # Create new project
            new_name = get_input(stdscr, height - 2, 0, "New project name: ", "",
                               curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 30)
            if new_name and new_name not in all_projects_data:
                all_projects_data[new_name] = {col: [] for col in DEFAULT_COLUMNS}
                project_names = [key for key in all_projects_data.keys() if key != "_meta"]
                selected_idx = project_names.index(new_name)
                # Save data after project creation
                save_data(all_projects_data)
                display_message(stdscr, f"Created project: {new_name}", 1.0,
                              curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
            elif new_name in all_projects_data:
                display_message(stdscr, "Project already exists!", 1.5,
                              curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)
        elif is_key_pressed(key, 'r'):
            # Rename project
            if project_names:
                old_name = project_names[selected_idx]
                new_name = get_input(stdscr, height - 2, 0, f"Rename '{old_name}' to: ", old_name,
                                   curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 30)
                if new_name and new_name != old_name:
                    if new_name not in all_projects_data:
                        # Rename the project by copying data and deleting old key
                        all_projects_data[new_name] = all_projects_data[old_name]
                        del all_projects_data[old_name]

                        # Update meta data if it referenced the old project
                        if all_projects_data.get("_meta", {}).get("last_project") == old_name:
                            if "_meta" not in all_projects_data:
                                all_projects_data["_meta"] = {}
                            all_projects_data["_meta"]["last_project"] = new_name

                        # Update project names list and selected index
                        project_names = [key for key in all_projects_data.keys() if key != "_meta"]
                        selected_idx = project_names.index(new_name)

                        # Save data after project rename
                        save_data(all_projects_data)
                        display_message(stdscr, f"Renamed project: {old_name} → {new_name}", 1.5,
                                      curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)

                        # If we renamed the current project, return the new name
                        if old_name == current_project_name:
                            current_project_name = new_name
                    else:
                        display_message(stdscr, "Project name already exists!", 1.5,
                                      curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)
                elif new_name == old_name:
                    display_message(stdscr, "Project name unchanged.", 1.0,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
        elif is_key_pressed(key, 'd'):
            # Delete project (with confirmation)
            if len(project_names) > 1:
                project_to_delete = project_names[selected_idx]
                confirm = get_input(stdscr, height - 2, 0, f"Delete '{project_to_delete}'? (y/N): ", "",
                                  curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0, 5)
                if confirm.lower() == 'y':
                    del all_projects_data[project_to_delete]
                    project_names = [key for key in all_projects_data.keys() if key != "_meta"]
                    if selected_idx >= len(project_names):
                        selected_idx = len(project_names) - 1
                    # Save data after project deletion
                    save_data(all_projects_data)
                    display_message(stdscr, f"Deleted project: {project_to_delete}", 1.0,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                    if project_to_delete == current_project_name:
                        return project_names[selected_idx] if project_names else DEFAULT_PROJECT_NAME
            else:
                display_message(stdscr, "Cannot delete the last project!", 1.5,
                              curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)
        elif is_key_pressed(key, 'q') or key == 27:  # 'q' or ESC
            return current_project_name

def draw_board(stdscr, tasks_data, current_column_idx, current_task_idx_in_col, project_name, has_colors):
    """Draws the Kanban board with tasks organized in columns."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()



    # Calculate column width
    col_width = max(DEFAULT_COLUMN_WIDTH, (width - len(DEFAULT_COLUMNS) - 1) // len(DEFAULT_COLUMNS))

    # Draw column headers
    header_y = 1
    for i, col_name in enumerate(DEFAULT_COLUMNS):
        x_pos = i * (col_width + 1)
        try:
            # Get task count info for this column
            tasks = tasks_data.get(col_name, [])
            total_tasks = len(tasks)

            # Calculate visible range if there are tasks
            if total_tasks > 0:
                max_tasks_to_show = (height - 7) // MIN_TASK_DISPLAY_HEIGHT  # Rough calculation
                if i == current_column_idx and current_task_idx_in_col < total_tasks:
                    start_task_idx = max(0, current_task_idx_in_col - max_tasks_to_show + 1)
                    if start_task_idx + max_tasks_to_show > total_tasks:
                        start_task_idx = max(0, total_tasks - max_tasks_to_show)
                else:
                    start_task_idx = 0
                end_task_idx = min(total_tasks, start_task_idx + max_tasks_to_show)

                # Create header with task count info
                if max_tasks_to_show >= total_tasks:
                    # All tasks visible
                    header_text = f"{col_name} ({total_tasks})"
                else:
                    # Show visible range
                    visible_start = start_task_idx + 1
                    visible_end = end_task_idx
                    header_text = f"{col_name} ({visible_start}-{visible_end}/{total_tasks})"
            else:
                header_text = f"{col_name} (0)"

            # Truncate header if too long
            if len(header_text) > col_width:
                header_text = header_text[:col_width-3] + "..."

            # Draw column header
            if i == current_column_idx:
                if has_colors:
                    stdscr.addstr(header_y, x_pos, header_text.center(col_width), curses.color_pair(COLOR_PAIR_ACTIVE_HEADER) | curses.A_BOLD)
                else:
                    stdscr.addstr(header_y, x_pos, header_text.center(col_width), curses.A_REVERSE | curses.A_BOLD)
            else:
                if has_colors:
                    stdscr.addstr(header_y, x_pos, header_text.center(col_width), curses.color_pair(COLOR_PAIR_HEADER))
                else:
                    stdscr.addstr(header_y, x_pos, header_text.center(col_width), curses.A_BOLD)

            # Draw vertical separator
            if i < len(DEFAULT_COLUMNS) - 1:
                for y in range(header_y, height - 2):
                    try:
                        if has_colors:
                            stdscr.addch(y, x_pos + col_width, '|', curses.color_pair(COLOR_PAIR_BORDER))
                        else:
                            stdscr.addch(y, x_pos + col_width, '|')
                    except curses.error:
                        pass
        except curses.error:
            pass

    # Draw horizontal line under headers
    try:
        line_y = header_y + 1
        for x in range(width - 1):
            try:
                if has_colors:
                    stdscr.addch(line_y, x, '-', curses.color_pair(COLOR_PAIR_BORDER))
                else:
                    stdscr.addch(line_y, x, '-')
            except curses.error:
                pass
    except curses.error:
        pass

    # Draw tasks in each column
    task_start_y = header_y + 2
    available_height = height - task_start_y - 2  # Leave space for instructions at bottom

    for col_idx, col_name in enumerate(DEFAULT_COLUMNS):
        x_pos = col_idx * (col_width + 1)
        tasks = tasks_data.get(col_name, [])

        if not tasks:
            # Show empty column message
            try:
                if has_colors:
                    stdscr.addstr(task_start_y, x_pos + 1, EMPTY_COLUMN_TEXT, curses.color_pair(COLOR_PAIR_BORDER))
                else:
                    stdscr.addstr(task_start_y, x_pos + 1, EMPTY_COLUMN_TEXT)
            except curses.error:
                pass
        else:
            # Calculate how many tasks can fit and which ones to display
            max_tasks_to_show = available_height // MIN_TASK_DISPLAY_HEIGHT

            # If this is the current column, try to keep the selected task visible
            if col_idx == current_column_idx and current_task_idx_in_col < len(tasks):
                # Calculate scroll offset to keep selected task visible
                start_task_idx = max(0, current_task_idx_in_col - max_tasks_to_show + 1)
                if start_task_idx + max_tasks_to_show > len(tasks):
                    start_task_idx = max(0, len(tasks) - max_tasks_to_show)
            else:
                start_task_idx = 0

            end_task_idx = min(len(tasks), start_task_idx + max_tasks_to_show)

            # Draw tasks
            current_y = task_start_y
            for task_idx in range(start_task_idx, end_task_idx):
                task = tasks[task_idx]

                # Determine if this task is selected
                is_selected = (col_idx == current_column_idx and task_idx == current_task_idx_in_col)

                # Get priority color
                priority = task.get("priority", DEFAULT_PRIORITY)
                priority_color = COLOR_PAIR_PRIO_MID
                if priority == "Low":
                    priority_color = COLOR_PAIR_PRIO_LOW
                elif priority == "High":
                    priority_color = COLOR_PAIR_PRIO_HIGH

                try:
                    # Get priority abbreviation
                    priority_abbrev = priority[0].upper()  # H, M, L

                    # Combine priority and title on one line
                    title = task.get("title", "Untitled")
                    combined_text = f"[{priority_abbrev}] {title}"

                    # Truncate if too long
                    display_text = combined_text[:col_width]

                    if is_selected:
                        if has_colors:
                            stdscr.addstr(current_y, x_pos + 1, display_text.ljust(col_width - 1), curses.color_pair(COLOR_PAIR_SELECTED_TASK))
                        else:
                            stdscr.addstr(current_y, x_pos + 1, display_text.ljust(col_width - 1), curses.A_REVERSE)
                    else:
                        if has_colors:
                            stdscr.addstr(current_y, x_pos + 1, display_text, curses.color_pair(priority_color))
                        else:
                            stdscr.addstr(current_y, x_pos + 1, display_text)

                except curses.error:
                    pass

                current_y += MIN_TASK_DISPLAY_HEIGHT

    # Draw project name and instructions at the bottom
    instructions = "←→: Columns | ↑↓: Tasks | a: Add | e: Edit | d: Delete | m: Move (+ arrows) | p: Projects | q: Quit"
    version_text = __version__
    try:
        # Calculate available space for instructions (reserve space for version)
        project_start = 1
        version_space = len(version_text) + 1  # +1 for space before version
        available_width = width - len(project_name) - project_start - version_space - 1

        # First draw the project name in bold
        if has_colors:
            stdscr.addstr(height - 1, project_start, project_name, curses.color_pair(COLOR_PAIR_PROJECT_NAME) | curses.A_BOLD)
        else:
            stdscr.addstr(height - 1, project_start, project_name, curses.A_BOLD)

        # Then draw the separator and instructions (truncated if needed)
        separator_and_instructions = f" | {instructions}"
        if available_width > 0:
            truncated_instructions = separator_and_instructions[:available_width]
            if has_colors:
                stdscr.addstr(height - 1, len(project_name) + project_start, truncated_instructions, curses.color_pair(COLOR_PAIR_MESSAGE_INFO))
            else:
                stdscr.addstr(height - 1, len(project_name) + project_start, truncated_instructions)

        # Draw version at the end
        version_x = width - len(version_text) - 1
        if version_x > len(project_name) + project_start:  # Make sure version doesn't overlap
            if has_colors:
                stdscr.addstr(height - 1, version_x, version_text, curses.color_pair(COLOR_PAIR_MESSAGE_INFO))
            else:
                stdscr.addstr(height - 1, version_x, version_text)
    except curses.error:
        pass

    stdscr.refresh()

def main(stdscr):
    try:
        curses.curs_set(0) # Hide cursor
        curses.noecho()    # Don't echo key presses
        stdscr.keypad(True)# Enable keypad for special keys (arrows, etc.)
        stdscr.nodelay(False) # Wait for user input
    except curses.error:
        # If basic curses setup fails, we can't continue
        return

    # Show splash screen
    try:
        show_splash_screen(stdscr)
    except curses.error:
        # If splash screen fails, continue without it
        pass

    # Initialize colors if supported
    has_colors = curses.has_colors()
    if has_colors:
        try:
            curses.start_color()
            curses.use_default_colors() # Use terminal's default background
            # Define color pairs (foreground, background)
            curses.init_pair(COLOR_PAIR_PROJECT_NAME, curses.COLOR_CYAN, -1)
            curses.init_pair(COLOR_PAIR_HEADER, curses.COLOR_BLUE, -1)
            curses.init_pair(COLOR_PAIR_ACTIVE_HEADER, curses.COLOR_GREEN, -1)
            curses.init_pair(COLOR_PAIR_SELECTED_TASK, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(COLOR_PAIR_MESSAGE_INFO, curses.COLOR_GREEN, -1)
            curses.init_pair(COLOR_PAIR_MESSAGE_ERROR, curses.COLOR_RED, -1)
            curses.init_pair(COLOR_PAIR_BORDER, curses.COLOR_WHITE, -1)
            curses.init_pair(COLOR_PAIR_MODAL_BORDER, curses.COLOR_BLUE, -1)
            curses.init_pair(COLOR_PAIR_MODAL_TEXT, curses.COLOR_WHITE, -1)
            curses.init_pair(COLOR_PAIR_MODAL_SELECTED_ITEM, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(COLOR_PAIR_MODAL_HEADER, curses.COLOR_YELLOW, -1)
            curses.init_pair(COLOR_PAIR_PRIO_LOW, curses.COLOR_GREEN, -1)
            curses.init_pair(COLOR_PAIR_PRIO_MID, curses.COLOR_YELLOW, -1)
            curses.init_pair(COLOR_PAIR_PRIO_HIGH, curses.COLOR_RED, -1)
        except curses.error:
            has_colors = False # Fallback if colors can't be initialized

    all_projects_data = load_data()
    project_names_list = [key for key in all_projects_data.keys() if key != "_meta"]

    # Try to load the last opened project from data
    last_project = load_last_project_from_data(all_projects_data)
    if last_project and last_project in project_names_list:
        current_project_name = last_project
    else:
        current_project_name = project_names_list[0] if project_names_list else DEFAULT_PROJECT_NAME

    # Ensure the current project exists in the data
    if current_project_name not in all_projects_data:
        all_projects_data[current_project_name] = {col: [] for col in DEFAULT_COLUMNS}

    # Save the current project as the last opened project
    save_last_project_to_data(all_projects_data, current_project_name)

    current_column_idx = 0  # Start in the first column
    current_task_idx_in_col = 0  # Start with the first task in the column

    # Auto-save helper function
    def auto_save(show_message=False):
        try:
            save_data(all_projects_data)
            if show_message:
                try:
                    height, width = stdscr.getmaxyx()
                    stdscr.addstr(height - 1, width - 10, "💾 Saved",
                                curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                    stdscr.refresh()
                    time.sleep(0.3)
                except curses.error:
                    pass
        except Exception as e:
            # If save fails, we don't want to crash the app
            pass

    try:
        while True:
            # Get current project's tasks
            tasks_data = all_projects_data[current_project_name]

            # Ensure current indices are valid
            if current_column_idx >= len(DEFAULT_COLUMNS):
                current_column_idx = 0

            current_col_tasks = tasks_data.get(DEFAULT_COLUMNS[current_column_idx], [])
            if current_task_idx_in_col >= len(current_col_tasks):
                current_task_idx_in_col = max(0, len(current_col_tasks) - 1)

            # Draw the board
            draw_board(stdscr, tasks_data, current_column_idx, current_task_idx_in_col, current_project_name, has_colors)

            # Get user input
            try:
                key = stdscr.getch()
            except curses.error:
                # If getch fails, break out of loop
                break

            # Handle navigation
            if key == curses.KEY_LEFT:
                current_column_idx = (current_column_idx - 1) % len(DEFAULT_COLUMNS)
                # Reset task index for new column
                new_col_tasks = tasks_data.get(DEFAULT_COLUMNS[current_column_idx], [])
                current_task_idx_in_col = min(current_task_idx_in_col, max(0, len(new_col_tasks) - 1))

            elif key == curses.KEY_RIGHT:
                current_column_idx = (current_column_idx + 1) % len(DEFAULT_COLUMNS)
                # Reset task index for new column
                new_col_tasks = tasks_data.get(DEFAULT_COLUMNS[current_column_idx], [])
                current_task_idx_in_col = min(current_task_idx_in_col, max(0, len(new_col_tasks) - 1))

            elif key == curses.KEY_UP:
                if current_col_tasks:
                    current_task_idx_in_col = (current_task_idx_in_col - 1) % len(current_col_tasks)

            elif key == curses.KEY_DOWN:
                if current_col_tasks:
                    current_task_idx_in_col = (current_task_idx_in_col + 1) % len(current_col_tasks)

            # Handle actions
            elif is_key_pressed(key, 'q'):
                break

            elif is_key_pressed(key, 'p'):
                # Project management
                new_project = manage_projects_modal(stdscr, all_projects_data, current_project_name, has_colors)
                if new_project != current_project_name:
                    current_project_name = new_project
                    current_column_idx = 0
                    current_task_idx_in_col = 0
                    # Save the last project and auto-save data
                    save_last_project_to_data(all_projects_data, current_project_name)
                    auto_save()

            elif is_key_pressed(key, 'a'):
                # Add new task
                title = get_input(stdscr, stdscr.getmaxyx()[0] - 2, 0, "Task title: ", "",
                                 curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 50)
                if title:
                    # Choose priority
                    priority_options = ["Low", "Mid", "High"]
                    priority_choice = get_input(stdscr, stdscr.getmaxyx()[0] - 2, 0, "Priority (L/M/H): ", "M",
                                              curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 5)

                    priority = DEFAULT_PRIORITY
                    if priority_choice.upper().startswith('L'):
                        priority = "Low"
                    elif priority_choice.upper().startswith('H'):
                        priority = "High"

                    new_task = {
                        "id": generate_id(),
                        "title": title,
                        "priority": priority
                    }

                    current_column = DEFAULT_COLUMNS[current_column_idx]
                    tasks_data[current_column].append(new_task)
                    current_task_idx_in_col = len(tasks_data[current_column]) - 1

                    # Auto-save after adding task
                    auto_save(show_message=True)

                    display_message(stdscr, f"Added task: {title}", 1.0,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)

            elif is_key_pressed(key, 'e'):
                # Edit task
                if current_col_tasks:
                    task = current_col_tasks[current_task_idx_in_col]
                    new_title = get_input(stdscr, stdscr.getmaxyx()[0] - 2, 0, "New title: ", task.get("title", ""),
                                        curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 50)
                    if new_title:
                        task["title"] = new_title

                        # Edit priority
                        current_priority = task.get("priority", DEFAULT_PRIORITY)
                        priority_choice = get_input(stdscr, stdscr.getmaxyx()[0] - 2, 0,
                                                  f"Priority (L/M/H) [{current_priority}]: ", "",
                                                  curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0, 5)

                        if priority_choice.upper().startswith('L'):
                            task["priority"] = "Low"
                        elif priority_choice.upper().startswith('H'):
                            task["priority"] = "High"
                        elif priority_choice.upper().startswith('M'):
                            task["priority"] = "Mid"

                        # Auto-save after editing task
                        auto_save(show_message=True)

                        display_message(stdscr, "Task updated", 1.0,
                                      curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                else:
                    display_message(stdscr, "No task to edit", 1.0,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)

            elif is_key_pressed(key, 'm'):
                # Enter move mode - use arrow keys to move tasks
                if current_col_tasks:
                    task = current_col_tasks[current_task_idx_in_col]

                    # Display move mode instructions
                    display_message(stdscr, "Move mode: ← → (columns) ↑ ↓ (reorder) | Enter: confirm | Esc: cancel", 0.1,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)

                    move_mode = True
                    original_col_idx = current_column_idx
                    original_task_idx = current_task_idx_in_col

                    while move_mode:
                        # Redraw board to show current position
                        draw_board(stdscr, tasks_data, current_column_idx, current_task_idx_in_col, current_project_name, has_colors)

                        # Show move mode status
                        height, width = stdscr.getmaxyx()
                        move_msg = "MOVE MODE: ← → (columns) ↑ ↓ (reorder) | Enter: confirm | Esc: cancel"
                        try:
                            stdscr.addstr(height - 1, 0, move_msg[:width-1],
                                        curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                            stdscr.refresh()
                        except curses.error:
                            pass

                        move_key = stdscr.getch()

                        if move_key == curses.KEY_LEFT:
                            # Move to previous column
                            new_col_idx = (current_column_idx - 1) % len(DEFAULT_COLUMNS)
                            if new_col_idx != current_column_idx:
                                # Remove from current column
                                current_col_tasks.pop(current_task_idx_in_col)

                                # Add to new column at the end
                                new_column = DEFAULT_COLUMNS[new_col_idx]
                                tasks_data[new_column].append(task)

                                # Update position
                                current_column_idx = new_col_idx
                                current_task_idx_in_col = len(tasks_data[new_column]) - 1
                                current_col_tasks = tasks_data[DEFAULT_COLUMNS[current_column_idx]]

                        elif move_key == curses.KEY_RIGHT:
                            # Move to next column
                            new_col_idx = (current_column_idx + 1) % len(DEFAULT_COLUMNS)
                            if new_col_idx != current_column_idx:
                                # Remove from current column
                                current_col_tasks.pop(current_task_idx_in_col)

                                # Add to new column at the end
                                new_column = DEFAULT_COLUMNS[new_col_idx]
                                tasks_data[new_column].append(task)

                                # Update position
                                current_column_idx = new_col_idx
                                current_task_idx_in_col = len(tasks_data[new_column]) - 1
                                current_col_tasks = tasks_data[DEFAULT_COLUMNS[current_column_idx]]

                        elif move_key == curses.KEY_UP:
                            # Move task up in current column
                            if current_task_idx_in_col > 0:
                                # Swap with task above
                                current_col_tasks[current_task_idx_in_col], current_col_tasks[current_task_idx_in_col - 1] = \
                                    current_col_tasks[current_task_idx_in_col - 1], current_col_tasks[current_task_idx_in_col]
                                current_task_idx_in_col -= 1

                        elif move_key == curses.KEY_DOWN:
                            # Move task down in current column
                            if current_task_idx_in_col < len(current_col_tasks) - 1:
                                # Swap with task below
                                current_col_tasks[current_task_idx_in_col], current_col_tasks[current_task_idx_in_col + 1] = \
                                    current_col_tasks[current_task_idx_in_col + 1], current_col_tasks[current_task_idx_in_col]
                                current_task_idx_in_col += 1

                        elif move_key == ord('\n') or move_key == curses.KEY_ENTER or move_key == 10:
                            # Confirm move
                            move_mode = False
                            auto_save(show_message=True)

                            if (current_column_idx != original_col_idx or
                                current_task_idx_in_col != original_task_idx):
                                display_message(stdscr, "Task moved successfully!", 1.0,
                                              curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                            else:
                                display_message(stdscr, "Task position unchanged", 0.5,
                                              curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)

                        elif move_key == 27:  # ESC key
                            # Cancel move - restore original position
                            move_mode = False

                            # If we moved columns, need to restore
                            if current_column_idx != original_col_idx:
                                # Remove from current position
                                current_col_tasks.pop(current_task_idx_in_col)

                                # Restore to original position
                                original_column_tasks = tasks_data[DEFAULT_COLUMNS[original_col_idx]]
                                original_column_tasks.insert(original_task_idx, task)

                                current_column_idx = original_col_idx
                                current_task_idx_in_col = original_task_idx
                            elif current_task_idx_in_col != original_task_idx:
                                # Restore original order within same column
                                current_col_tasks.pop(current_task_idx_in_col)
                                current_col_tasks.insert(original_task_idx, task)
                                current_task_idx_in_col = original_task_idx

                            display_message(stdscr, "Move cancelled", 0.5,
                                          curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)

                        # Update current_col_tasks reference
                        current_col_tasks = tasks_data.get(DEFAULT_COLUMNS[current_column_idx], [])
                else:
                    display_message(stdscr, "No task to move", 1.0,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)

            elif is_key_pressed(key, 'd'):
                # Delete task with confirmation
                if current_col_tasks:
                    task = current_col_tasks[current_task_idx_in_col]
                    confirm = get_input(stdscr, stdscr.getmaxyx()[0] - 2, 0, f"Delete '{task.get('title', 'Untitled')}'? (y/N): ", "",
                                      curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0, 5)
                    if confirm.lower() == 'y':
                        current_col_tasks.pop(current_task_idx_in_col)

                        # Adjust task index if it's now out of bounds
                        current_col_tasks_after_del = tasks_data.get(DEFAULT_COLUMNS[current_column_idx], [])
                        if not current_col_tasks_after_del:
                            current_task_idx_in_col = 0
                        elif current_task_idx_in_col >= len(current_col_tasks_after_del):
                            current_task_idx_in_col = len(current_col_tasks_after_del) - 1

                        # Auto-save after deleting task
                        auto_save(show_message=True)

                        display_message(stdscr, "Task deleted", 1.0,
                                      curses.color_pair(COLOR_PAIR_MESSAGE_INFO) if has_colors else 0)
                    else:
                        display_message(stdscr, "Deletion cancelled", 0.5)
                else:
                    display_message(stdscr, "No task to delete", 0.5,
                                  curses.color_pair(COLOR_PAIR_MESSAGE_ERROR) if has_colors else 0)

            elif key == curses.KEY_RESIZE:
                # Handle terminal resize
                pass

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        try:
            auto_save()
        except:
            pass
        # curses.wrapper will handle terminal cleanup
        return
    except curses.error:
        # Handle curses errors gracefully
        try:
            auto_save()
        except:
            pass
        return

    # Final save before exiting (auto_save also called throughout)
    try:
        auto_save()
    except:
        pass

def cli_main():
    """Command line interface entry point for the package."""
    global DATA_FILE

    parser = argparse.ArgumentParser(
        description=__description__,
        prog='kanby'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--data-file',
        default=DATA_FILE,
        help=f'Path to data file (default: {DATA_FILE})'
    )

    args = parser.parse_args()

    # Set custom data file if provided
    DATA_FILE = args.data_file

    try:
        curses.wrapper(main) # Initialize curses and run main
    except KeyboardInterrupt:
        print("\nKanby closed. Your data has been saved.")
        sys.exit(0)
    except curses.error as e:
        # Handle curses-specific errors (e.g., terminal initialization issues)
        print(f"\nTerminal error: {e}")
        print("This may happen if the terminal doesn't support curses or was interrupted during startup.")
        print("Try running in a different terminal or check your terminal settings.")
        sys.exit(1)
    except Exception as e:
        # Handle any other unexpected errors
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Terminal state should be reset. If not, try running 'reset' in your terminal.")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()
