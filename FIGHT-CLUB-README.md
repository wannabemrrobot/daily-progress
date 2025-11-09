# Fight Club - Alter Ego Mission Manager

## 🥊 Overview

**Fight Club** is an all-in-one Python script for managing your alter ego missions and daily progress. It provides an interactive command-line interface to create, track, modify, and complete missions for your three alter egos: **Kei**, **Mr-Robot**, and **Tyler**.

## 📋 Features

### ✅ Implemented Features

1. **🎯 Create New Mission**
   - Select alter ego (Kei, Mr-Robot, or Tyler)
   - Auto-generates mission ID (K01, M02, T03, etc.)
   - Set mission details (title, description, difficulty)
   - Define progress tracking (e.g., 10 days, 50 tasks)
   - Set start and due dates
   - Configure stat changes for completion/failure
   - Customize ability bonuses/penalties per alter ego

2. **✅ Mark Mission as Completed**
   - Move mission to completed folder
   - Set completion date automatically
   - Display earned rewards (health, energy, abilities)
   - Update mission status

3. **❌ Mark Mission as Failed**
   - Move mission to completed folder with failed status
   - Set failure date automatically
   - Display penalties applied (health, energy, abilities)
   - Update mission status

4. **📈 Update Mission Progress**
   - Update current progress for ongoing missions
   - Automatically update status (not-started → in-progress)
   - Show progress percentage

5. **✏️ Modify Mission**
   - Edit mission details (title, description, difficulty)
   - Update progress values (current/total)
   - Change due dates
   - Modify mission status
   - Auto-rename files if title changes
   - Move missions between folders based on status

6. **🗑️ Delete Mission**
   - Delete missions from any folder
   - Confirmation prompt to prevent accidents

7. **📊 View All Missions**
   - List all not-completed missions
   - List all completed missions
   - Show mission details (archetype, status, progress, due date)

8. **📝 Add Daily Progress Entry** *(Coming Soon)*
   - Integration with daily progress tracking system

## 🏗️ Mission JSON Structure

Missions follow this exact structure:

```json
{
    "archetype": "kei|mr-robot|tyler",
    "mission_code": "K01|M01|T01",
    "title": "Mission Title",
    "description": "Mission description",
    "difficulty": "easy|medium|hard",
    "status": "not-started|in-progress|completed|failed",
    "progress": {
        "current": 0,
        "total": 10
    },
    "archetype_stat_change": {
        "on_complete": {
            "health": 10,
            "energy": 10,
            "abilities": {
                "ability1": 10,
                "ability2": 15
            }
        },
        "on_failure": {
            "health": -10,
            "energy": -10,
            "abilities": {
                "ability1": -10,
                "ability2": -15
            }
        }
    },
    "reward": [],
    "mission_icon": "assets/badges/icon.png",
    "due_date": "2025-12-31",
    "start_date": "2025-11-09",
    "completion_date": null
}
```

### Filename Format
Missions are saved as: `{mission_code}-{title-kebab-case}.json`

Example: `K01-meditate-10.json`, `T02-quit-smoking-75.json`

## 🦸 Alter Egos & Abilities

### 啓 Kei - The Monk of Still Waters
**Prefix:** K

**Abilities:**
- self-control
- peace
- wisdom
- focus
- resilience
- harmony
- mindfulness
- intuition

### Mr-Robot - The Architect of Systems
**Prefix:** M

**Abilities:**
- intelligence
- logic
- adaptability
- innovation
- focus
- systemization
- precision
- speed

### 狼 Tyler - The Untamed Wolf
**Prefix:** T

**Abilities:**
- strength
- discipline
- agression
- confidence
- dominance
- pain tolerance
- honor
- determination

## 📂 Directory Structure

```
daily-progress/
├── fight-club.py              # Main script
├── gamification/
│   └── missions/
│       ├── not-completed/     # Active missions
│       │   ├── K01-mission.json
│       │   ├── M01-mission.json
│       │   └── T01-mission.json
│       └── completed/         # Completed/Failed missions
│           └── K02-mission.json
```

## 🚀 Usage

### Running the Script

```bash
cd daily-progress
python3 fight-club.py
```

Or make it executable:

```bash
chmod +x fight-club.py
./fight-club.py
```

### Example Workflow

#### 1. Create a New Mission

```
Select option: 2 (Create New Mission)
→ Select alter ego: 1 (Kei)
→ Mission ID auto-generated: K01
→ Enter title: "Meditate daily for 10 days"
→ Enter description: "Build mindfulness practice"
→ Select difficulty: 1 (Easy)
→ Total units: 10
→ Start date: 2025-11-09
→ Due date: 2025-11-19
→ Mission icon: assets/badges/meditate.png
→ On completion: Health +5, Energy +10
→ Abilities: peace +15, mindfulness +20
→ On failure: Health -5, peace -10
```

**Result:** Creates `K01-meditate-daily-for-10-days.json` in `not-completed/`

#### 2. Update Progress

```
Select option: 5 (Update Mission Progress)
→ Select mission: K01
→ Current: 0/10
→ New progress: 3
```

**Result:** Mission status changes to "in-progress", progress = 3/10 (30%)

#### 3. Complete Mission

```
Select option: 3 (Mark Mission as Completed)
→ Select mission: K01
```

**Result:** 
- Moves to `completed/` folder
- Sets completion_date
- Displays earned rewards
- Status = "completed"

## 🎨 Color-Coded Output

The script uses terminal colors for better readability:

- **🔵 Blue:** Headers and labels
- **🟢 Green:** Success messages and completed items
- **🟡 Yellow:** Warnings and info messages
- **🔴 Red:** Errors and failure messages
- **🟣 Purple:** Section headers

## 🔮 Future Features

### Planned Enhancements

1. **📝 Daily Progress Integration**
   - Add daily progress entries
   - Link missions to daily logs
   - Track daily activity

2. **📊 Statistics Dashboard**
   - View alter ego stats
   - Mission completion rates
   - Ability progress tracking

3. **🎁 Reward System**
   - Define custom rewards
   - Track locked/unlocked rewards
   - Reward redemption

4. **📈 Analytics**
   - Mission success/failure rates
   - Time tracking
   - Productivity insights

5. **🔄 Mission Templates**
   - Save mission templates
   - Quick mission creation
   - Recurring missions

6. **💾 Backup & Export**
   - Backup mission data
   - Export to different formats
   - Import missions

## 🛠️ Technical Details

### Dependencies
- Python 3.7+
- Standard library only (no external dependencies)

### File Locations
- Script: `daily-progress/fight-club.py`
- Missions: `daily-progress/gamification/missions/`
- Config: Uses ALTER_EGOS dictionary in script

### Error Handling
- Validates all user inputs
- Graceful handling of missing files
- Confirmation prompts for destructive actions
- Color-coded error messages

## 📖 Mission ID System

Mission IDs follow this pattern:

```
{PREFIX}{NUMBER}
```

- **PREFIX:** K (Kei), M (Mr-Robot), T (Tyler)
- **NUMBER:** Two-digit sequential number (01, 02, 03...)

Examples:
- K01 → First Kei mission
- M03 → Third Mr-Robot mission
- T10 → Tenth Tyler mission

IDs are auto-generated and increment based on existing missions in **both** completed and not-completed folders.

## 🎯 Mission Status Flow

```
not-started → in-progress → completed
                         → failed
```

- **not-started:** Progress = 0
- **in-progress:** 0 < Progress < Total
- **completed:** Progress = Total, moved to completed folder
- **failed:** Moved to completed folder with failed status

## 💡 Tips

1. **Consistent Naming:** Use descriptive mission titles that reflect the goal
2. **Realistic Progress:** Set achievable total units for tracking
3. **Balanced Stats:** Set failure penalties lower than completion bonuses
4. **Due Dates:** Set realistic deadlines to maintain motivation
5. **Regular Updates:** Update progress frequently for accurate tracking

## 🚨 Important Notes

- **First rule of Fight Club:** You do not talk about Fight Club.
- **Second rule of Fight Club:** You DO NOT talk about Fight Club.
- Mission files are JSON - can be manually edited if needed
- Failed missions are stored in completed folder with status="failed"
- Deleting missions is permanent - use with caution
- Press Ctrl+C to interrupt at any time

## 🤝 Integration with Manager.py

Fight Club is designed to work alongside `manager.py`:

- **fight-club.py:** Mission management
- **manager.py:** Daily progress entries

Both scripts share the same directory structure and can be used independently or together.

## 📄 License

Part of the Alter Ego gamification system. See LICENSE file for details.

---

**Stay strong! 💪**

*"It's only after we've lost everything that we're free to do anything."*
