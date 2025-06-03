# 🔥 Kanby

**A Beautiful Terminal-Based Kanban Board**

![Screenshot](https://cdn.arbatov.dev/FUb3NPhuYzVMEY5uSQJ0TS6TY.jpg)

Kanby brings the power of Kanban boards directly to your terminal with a clean, intuitive interface built using Python's curses library.

## ✨ Features

- 🎯 **Multiple Projects**: Organize different projects separately
- 📊 **Customizable Columns**: Default "To Do", "In Progress", "Done"
- 🎨 **Priority Levels**: Low, Mid, High priority tasks with color coding
- 💾 **Persistent Storage**: All data saved locally in JSON format
- ⌨️ **Keyboard Navigation**: Full keyboard control for efficiency
- 🎭 **Beautiful UI**: Clean, colorful terminal interface with splash screen
- 🚀 **Fast & Lightweight**: Minimal dependencies (Windows curses auto-installed on Windows)
- 🌍 **Cross-Platform**: Works on Linux, macOS, and Windows with proper curses support
- 🔧 **CLI Options**: Custom data file locations and more

## 📦 Installation

### Using pip
```bash
pip install kanby
```

**Windows Users**: The `windows-curses` dependency will be automatically installed on Windows systems.

### Using uv
```bash
uv add kanby
```

### From source
```bash
git clone https://github.com/vladzima/kanby
cd kanby
pip install -e .
```

### Windows Compatibility
Kanby automatically handles Windows curses compatibility. If you encounter issues on Windows, ensure you have:
- Python 3.7 or later
- The `windows-curses` package (installed automatically)


## 🚀 Usage

Simply run:
```bash
kanby
```

Or with custom data file:
```bash
kanby --data-file /path/to/your/kanban.json
```

For help:
```bash
kanby --help
```

## ⌨️ Keyboard Controls

### Navigation
| Key | Action |
|-----|--------|
| `←` `→` | Navigate between columns |
| `↑` `↓` | Navigate between tasks |

### Task Management
| Key | Action |
|-----|--------|
| `a` | Add new task |
| `e` | Edit selected task |
| `d` | Delete selected task |
| `m` | Move task (+ arrow keys) |

### Project Management
| Key | Action |
|-----|--------|
| `p` | Open project manager |

#### In Project Manager
| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate projects |
| `Enter` | Select project |
| `n` | New project |
| `r` | Rename project |
| `d` | Delete project |
| `q` | Cancel/Exit |

### Application
| Key | Action |
|-----|--------|
| `q` | Quit application |

## 🎯 Task Management

### Creating Tasks
1. Press `a` to add a new task
2. Enter the task title
3. Choose priority (L/M/H for Low/Mid/High)
4. Task appears in current column

### Editing Tasks
1. Navigate to a task using arrow keys
2. Press `e` to edit
3. Modify title and/or priority
4. Changes are saved automatically

### Moving Tasks
1. Select a task with arrow keys
2. Press `m` to enter move mode
3. Use arrow keys to move:
   - `←` `→` : Move between columns
   - `↑` `↓` : Reorder within current column
4. Press `Enter` to confirm or `Esc` to cancel

### Task Visibility & Scrolling
Column headers show task counts and visibility information:
- **All visible**: `To Do (5)` - shows total count when all tasks fit
- **Scrolling needed**: `To Do (3-7/15)` - shows visible range when scrolling
- **Empty column**: `To Do (0)` - indicates no tasks in column

Navigate through long task lists with `↑` `↓` arrows. Headers automatically update to show which tasks are currently visible on screen.

### Priority Levels
Tasks display with compact priority indicators on the same line:
- **[H] Task title**: High priority (red color coding)
- **[M] Task title**: Mid priority (yellow color coding)
- **[L] Task title**: Low priority (green color coding)

This space-efficient format allows 3x more tasks to be visible on screen compared to the previous multi-line format.

## 📁 Project Management

### Multiple Projects
- Press `p` to open the project manager
- Navigate with `↑` `↓` arrow keys
- Press `Enter` to switch to selected project

### Creating Projects
1. In project manager, press `n`
2. Enter new project name
3. Project is created with default columns

### Renaming Projects
1. In project manager, select project to rename
2. Press `r` to rename
3. Enter new project name
4. All tasks and data are preserved
5. Cannot rename to an existing project name

### Deleting Projects
1. In project manager, select project
2. Press `d` to delete
3. Confirm with `y`
4. Cannot delete the last remaining project

## 🔧 Configuration

### Data Storage
Kanby stores data in `kanby_data.json` in your current directory by default.

### Custom Data File
Specify a custom location:
```bash
kanby --data-file ~/.config/kanby/my-projects.json
```

### Data Format
The JSON file contains all projects and tasks:
```json
{
  "Project Name": {
    "To Do": [
      {
        "id": "abc123",
        "title": "Task title",
        "priority": "High"
      }
    ],
    "In Progress": [],
    "Done": []
  }
}
```

## 🎨 Color Scheme

Kanby uses a carefully designed color scheme:
- **Project names**: Cyan
- **Column headers**: Blue (active: Green)
- **Task priorities**: Green (Low), Yellow (Mid), Red (High)
- **Selected items**: Yellow background
- **Messages**: Green (info), Red (error)
- **Borders**: White

## 💻 System Requirements

- Python 3.7 or higher
- Terminal with curses support
- Unix-like system (Linux, macOS) or Windows with proper terminal

## 🛠️ Development

### Setup
```bash
git clone https://github.com/vladzima/kanby
cd kanby
pip install -e .
```

### Running Tests
```bash
python -m pytest
```

### Code Structure
```
kanby/
├── kanby/
│   ├── __init__.py    # Package initialization
│   └── main.py        # Main application logic
├── pyproject.toml     # Package configuration
├── README.md          # This file
└── LICENSE           # MIT License
```

## 🐛 Troubleshooting

### Terminal Issues
If your terminal becomes corrupted after an error:
```bash
reset
```

### Color Issues
If colors don't display properly, your terminal may not support them. Kanby will fall back to a monochrome display.

### Size Issues
Kanby adapts to your terminal size, but works best with at least 80x24 characters.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Reporting Issues
Please use the GitHub issue tracker to report bugs or request features.


**Made with ❤️ for terminal enthusiasts and productivity lovers**
