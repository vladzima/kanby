# 🧪 Manual Testing Instructions for Kanby

## Testing Data Persistence (Ctrl+C Issue Fix)

### 🎯 Objective
Verify that Kanby properly saves data when interrupted with Ctrl+C and that data persists between sessions.

### 📋 Test Steps

#### Test 1: Basic Data Persistence
1. **Start Kanby**:
   ```
   kanby
   ```

2. **Add a test task**:
   - Press `a` to add task
   - Enter title: "Test Task 1"
   - Set priority: `H` (High)
   - You should see "💾 Saved" briefly appear

3. **Exit with Ctrl+C**:
   - Press `Ctrl+C` to interrupt the application
   - Application should exit gracefully

4. **Restart Kanby**:
   ```
   kanby
   ```

5. **Verify data persistence**:
   - Check that "Test Task 1" is still there
   - ✅ PASS: Task persists
   - ❌ FAIL: Task is missing

#### Test 2: Multiple Operations
1. **Start fresh or continue from Test 1**

2. **Perform multiple operations**:
   - Add 2-3 more tasks
   - Edit one task (press `e`)
   - Move one task to "In Progress" (press `m`, then `→`, then `Enter`)
   - Reorder a task within a column (press `m`, then `↑` or `↓`, then `Enter`)
   - Delete one task (press `d`, confirm with `y`)

3. **Each operation should show "💾 Saved"**

4. **Exit with Ctrl+C**

5. **Restart and verify all changes persisted**

#### Test 3: Project Management
1. **Start Kanby**

2. **Create new project**:
   - Press `p` to open project manager
   - Press `n` to create new project
   - Enter name: "Test Project"
   - Add some tasks to this project

3. **Switch between projects**:
   - Press `p` and select different projects
   - Verify tasks are different in each project

4. **Exit with Ctrl+C**

5. **Restart and verify**:
   - All projects should exist
   - Tasks should be in correct projects

#### Test 4: Custom Data File
1. **Test with custom data file**:
   ```
   kanby --data-file test_kanban.json
   ```

2. **Add some tasks**

3. **Exit with Ctrl+C**

4. **Verify file exists**:
   ```
   ls -la test_kanban.json
   cat test_kanban.json
   ```

5. **Restart with same file**:
   ```
   kanby --data-file test_kanban.json
   ```

6. **Verify data persists**

#### Test 5: Demo Data
1. **Start with demo data**:
   ```
   kanby --data-file demo_data.json
   ```

2. **Explore the demo projects**:
   - Press `p` to see "Work Project", "Personal", "Home Improvement"
   - Navigate through different tasks
   - Try editing/moving some tasks (use `m` + arrows + `Enter`)

3. **Exit with Ctrl+C**

4. **Restart and verify changes persisted**

### 🔍 What to Look For

#### ✅ Expected Behavior:
- "💾 Saved" message appears after each operation
- Ctrl+C exits gracefully without errors
- All data persists between sessions
- No data loss when interrupted
- JSON files are created/updated properly

#### ❌ Signs of Problems:
- No "💾 Saved" message after operations
- Ctrl+C causes errors or crashes
- Data disappears after restart
- JSON file is empty or corrupted
- Tasks appear in wrong projects

### 🚨 Emergency Reset
If data gets corrupted during testing:
```
rm kanby_data.json
rm test_kanban.json
kanby  # Will start fresh
```

Note: Last project preference is now stored directly in the data file under `_meta.last_project`, so removing the data file also resets the project memory.

### 📊 Expected Results
After implementing the auto-save fix:
- ✅ Data persists through Ctrl+C interruption
- ✅ Visual feedback shows when saving
- ✅ Signal handler ensures graceful shutdown
- ✅ Multiple rapid operations work correctly
- ✅ All project data is preserved

### 🎉 Success Criteria
The fix is successful if:
1. No data is lost when using Ctrl+C
2. Users see visual confirmation of saves
3. Data persists across all scenarios
4. Performance remains smooth
5. No crashes or errors occur