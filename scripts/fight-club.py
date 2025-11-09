#!/usr/bin/env python3
"""
Fight Club - Alter Ego Management System
==========================================
All-in-one script for managing alter egos, missions, and daily progress.

Features:
- Add/Modify/Delete missions
- Mark missions as completed/failed
- Add/Modify daily progress entries
- Manage alter ego stats
- Move missions between folders (not-completed, completed, failed)
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuration
REPO_ROOT = Path(__file__).parent.parent
MISSIONS_DIR = REPO_ROOT / "gamification" / "missions"
MISSIONS_NOT_COMPLETED = MISSIONS_DIR / "not-completed"
MISSIONS_COMPLETED = MISSIONS_DIR / "completed"
ALTER_EGOS_DIR = REPO_ROOT / "gamification" / "alter-egoes"
DAILY_PROGRESS_DIR = REPO_ROOT / "gamification" / "daily-progress"
REWARDS_DIR = REPO_ROOT / "gamification" / "rewards"
REWARDS_LOCKED = REWARDS_DIR / "locked"
REWARDS_UNLOCKED = REWARDS_DIR / "unlocked"
CONFIGS_DIR = REPO_ROOT / "gamification" / "configs"
XP_RULES_FILE = CONFIGS_DIR / "xp-rules.json"
SYNERGY_RULES_FILE = CONFIGS_DIR / "synergy-rules.json"
DAILY_PROGRESS_RULES_FILE = CONFIGS_DIR / "daily-progress-rules.json"
HISTORY_FILE = REPO_ROOT / "gamification" / "history.json"
SYNERGY_FILE = REPO_ROOT / "gamification" / "synergy.json"

# Ensure directories exist
MISSIONS_NOT_COMPLETED.mkdir(parents=True, exist_ok=True)
MISSIONS_COMPLETED.mkdir(parents=True, exist_ok=True)
REWARDS_LOCKED.mkdir(parents=True, exist_ok=True)
REWARDS_UNLOCKED.mkdir(parents=True, exist_ok=True)
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

# Synergy mapping: archetype -> synergy category
SYNERGY_MAPPING = {
    "tyler": "body",
    "mr-robot": "mind",
    "kei": "soul"
}

# Alter ego configurations with abilities
ALTER_EGOS = {
    "kei": {
        "name": "Kei",
        "role": "The Monk of Still Waters",
        "prefix": "K",
        "abilities": [
            "self-control",
            "peace",
            "wisdom",
            "focus",
            "resilience",
            "harmony",
            "mindfulness",
            "intuition"
        ]
    },
    "mr-robot": {
        "name": "Mr-Robot",
        "role": "The Architect of Systems",
        "prefix": "M",
        "abilities": [
            "intelligence",
            "logic",
            "adaptability",
            "innovation",
            "focus",
            "systemization",
            "precision",
            "speed"
        ]
    },
    "tyler": {
        "name": "Tyler",
        "role": "The Untamed Wolf",
        "prefix": "T",
        "abilities": [
            "strength",
            "discipline",
            "agression",
            "confidence",
            "dominance",
            "pain tolerance",
            "honor",
            "determination"
        ]
    }
}

def print_header(text: str):
    """Print a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
    return value if value else (default if default else "")

def get_choice(options: List[str], prompt: str = "Select an option") -> int:
    """Display options and get user choice."""
    print(f"\n{Colors.BOLD}{prompt}:{Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.OKBLUE}{i}.{Colors.ENDC} {option}")
    
    while True:
        try:
            choice = int(get_input("\nEnter choice"))
            if 1 <= choice <= len(options):
                return choice
            print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")

def load_json(file_path: Path) -> Dict:
    """Load JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print_error(f"Invalid JSON in file: {file_path}")
        return {}

def save_json(file_path: Path, data: Dict, indent: int = 4):
    """Save data to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print_error(f"Failed to save file: {e}")
        return False

def get_mission_files(folder: Path) -> List[Path]:
    """Get all mission JSON files in a folder."""
    if not folder.exists():
        return []
    return sorted([f for f in folder.glob("*.json")])

def get_next_mission_id(alter_ego: str) -> str:
    """Generate next mission ID for an alter ego (e.g., K01, M02, T03)."""
    prefix = ALTER_EGOS[alter_ego]["prefix"]
    
    # Check all folders for existing mission IDs with this prefix
    all_missions = []
    for folder in [MISSIONS_NOT_COMPLETED, MISSIONS_COMPLETED]:
        if folder.exists():
            all_missions.extend(folder.glob(f"{prefix}*.json"))
    
    # Extract numbers from existing IDs
    existing_numbers = []
    for mission_file in all_missions:
        # Extract number from filename like "K01-title.json"
        try:
            num_str = mission_file.stem.split('-')[0][1:]  # Get "01" from "K01"
            existing_numbers.append(int(num_str))
        except (ValueError, IndexError):
            continue
    
    # Get next number
    next_num = max(existing_numbers, default=0) + 1
    return f"{prefix}{next_num:02d}"


def title_to_filename(title: str) -> str:
    """Convert title to lowercase hyphenated filename.
    Example: 'Create Alter Ego Dashboard' -> 'create-alter-ego-dashboard'
    """
    return title.lower().replace(' ', '-')


def get_next_reward_id() -> str:
    """Generate next reward ID (R01, R02, R03...)."""
    all_rewards = []
    for folder in [REWARDS_LOCKED, REWARDS_UNLOCKED]:
        if folder.exists():
            all_rewards.extend(folder.glob("R*.json"))
    
    # Extract numbers from existing reward IDs
    existing_numbers = []
    for reward_file in all_rewards:
        try:
            num_str = reward_file.stem.split('-')[0][1:]  # Get "01" from "R01"
            existing_numbers.append(int(num_str))
        except (ValueError, IndexError):
            continue
    
    next_num = max(existing_numbers, default=0) + 1
    return f"R{next_num:02d}"


def load_xp_rules() -> Dict:
    """Load XP progression rules from xp-rules.json."""
    try:
        with open(XP_RULES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: XP rules file not found at {XP_RULES_FILE}{Colors.ENDC}")
        return {}
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Invalid JSON in XP rules file{Colors.ENDC}")
        return {}


def load_alter_ego(archetype: str) -> Optional[Dict]:
    """Load alter-ego JSON data."""
    ego_file = ALTER_EGOS_DIR / f"{archetype}.json"
    try:
        with open(ego_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: Alter-ego file not found: {ego_file}{Colors.ENDC}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Invalid JSON in alter-ego file: {ego_file}{Colors.ENDC}")
        return None


def save_alter_ego(archetype: str, data: Dict) -> bool:
    """Save updated alter-ego JSON data."""
    ego_file = ALTER_EGOS_DIR / f"{archetype}.json"
    try:
        with open(ego_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error saving alter-ego: {e}{Colors.ENDC}")
        return False


def get_next_history_index() -> int:
    """Get next history index from history.json."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        if not history:
            return 1
        return max(entry.get('history_index', 0) for entry in history) + 1
    except FileNotFoundError:
        return 1
    except json.JSONDecodeError:
        print(f"{Colors.WARNING}Warning: Invalid JSON in history file, starting from index 1{Colors.ENDC}")
        return 1


def apply_stat_changes(ego_data: Dict, changes: Dict, xp_rules: Dict) -> Dict:
    """
    Apply stat changes to alter-ego data with overflow and level-up logic.
    
    Args:
        ego_data: The alter-ego data to modify (will be modified in place)
        changes: Dict with keys like 'xp', 'health', 'energy', 'abilities'
        xp_rules: XP progression rules
    
    Returns:
        Dict containing the actual delta changes applied (after overflow handling)
    """
    delta_applied = {
        'xp': 0,
        'health': 0,
        'energy': 0,
        'abilities': {}
    }
    
    # Apply XP changes and handle level-up (if XP is provided)
    if 'xp' in changes and changes['xp'] != 0:
        xp_change = changes['xp']
        ego_data['xp_details']['current_xp'] += xp_change
        delta_applied['xp'] = xp_change
        
        # Handle level-up
        current_level = ego_data['level']
        level_data = xp_rules.get('levels', {}).get(str(current_level), {})
        xp_to_next = level_data.get('xp_to_next_level')
        
        while xp_to_next and ego_data['xp_details']['current_xp'] >= xp_to_next:
            # Level up!
            ego_data['xp_details']['current_xp'] -= xp_to_next
            ego_data['level'] += 1
            
            # Update title and xp_to_next_level from new level
            new_level_data = xp_rules.get('levels', {}).get(str(ego_data['level']), {})
            ego_data['title'] = new_level_data.get('title', ego_data['title'])
            ego_data['xp_details']['xp_to_next_level'] = new_level_data.get('xp_to_next_level')
            
            print(f"{Colors.OKGREEN}🎉 LEVEL UP! {ego_data['name']} is now Level {ego_data['level']} - {ego_data['title']}!{Colors.ENDC}")
            
            # Check if there's another level to reach
            xp_to_next = ego_data['xp_details']['xp_to_next_level']
    
    # Apply health changes with overflow
    if 'health' in changes and changes['health'] != 0:
        health_change = changes['health']
        ego_data['health_details']['current_health'] += health_change
        delta_applied['health'] = health_change
        
        # Handle overflow
        overflow_config = xp_rules.get('health_energy_overflow', {})
        if ego_data['health_details']['current_health'] >= ego_data['health_details']['max_health']:
            overflow_reset_pct = overflow_config.get('overflow_reset_percentage', 20)
            overflow_bonus = overflow_config.get('overflow_bonus_to_other_stat', 10)
            
            # Reset health to overflow_reset_percentage%
            ego_data['health_details']['current_health'] = overflow_reset_pct
            
            # Give bonus to energy
            ego_data['energy_details']['current_energy'] += overflow_bonus
            delta_applied['energy'] = delta_applied.get('energy', 0) + overflow_bonus
            
            print(f"{Colors.OKCYAN}💫 Health overflow! Reset to {overflow_reset_pct}, +{overflow_bonus} energy{Colors.ENDC}")
    
    # Apply energy changes with overflow
    if 'energy' in changes and changes['energy'] != 0:
        energy_change = changes['energy']
        ego_data['energy_details']['current_energy'] += energy_change
        delta_applied['energy'] = delta_applied.get('energy', 0) + energy_change
        
        # Handle overflow
        overflow_config = xp_rules.get('health_energy_overflow', {})
        if ego_data['energy_details']['current_energy'] >= ego_data['energy_details']['max_energy']:
            overflow_reset_pct = overflow_config.get('overflow_reset_percentage', 20)
            overflow_bonus = overflow_config.get('overflow_bonus_to_other_stat', 10)
            
            # Reset energy to overflow_reset_percentage%
            ego_data['energy_details']['current_energy'] = overflow_reset_pct
            
            # Give bonus to health
            ego_data['health_details']['current_health'] += overflow_bonus
            delta_applied['health'] = delta_applied.get('health', 0) + overflow_bonus
            
            print(f"{Colors.OKCYAN}💫 Energy overflow! Reset to {overflow_reset_pct}, +{overflow_bonus} health{Colors.ENDC}")
    
    # Apply ability changes
    if 'abilities' in changes:
        for ability, value in changes['abilities'].items():
            if value != 0:  # Only apply non-zero changes
                if ability in ego_data['abilities']:
                    ego_data['abilities'][ability] += value
                    delta_applied['abilities'][ability] = value
                else:
                    print(f"{Colors.WARNING}Warning: Unknown ability '{ability}' for {ego_data['name']}{Colors.ENDC}")
    
    return delta_applied


def record_history(event_data: Dict):
    """Add entry to history.json."""
    try:
        # Load existing history
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    except json.JSONDecodeError:
        print(f"{Colors.WARNING}Warning: Invalid JSON in history file, starting fresh{Colors.ENDC}")
        history = []
    
    # Add new entry
    history.append(event_data)
    
    # Save updated history
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"{Colors.FAIL}Error saving history: {e}{Colors.ENDC}")


def load_synergy() -> Optional[Dict]:
    """Load synergy.json data."""
    try:
        with open(SYNERGY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: Synergy file not found: {SYNERGY_FILE}{Colors.ENDC}")
        return None
    except json.JSONDecodeError:
        print(f"{Colors.FAIL}Error: Invalid JSON in synergy file{Colors.ENDC}")
        return None


def save_synergy(data: Dict) -> bool:
    """Save updated synergy.json data."""
    try:
        with open(SYNERGY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error saving synergy: {e}{Colors.ENDC}")
        return False


def calculate_synergy_xp() -> int:
    """
    Calculate total synergy XP from all alter-egos.
    Sum of all alter-ego XP values.
    """
    total_xp = 0
    for archetype in ["tyler", "mr-robot", "kei"]:
        ego_data = load_alter_ego(archetype)
        if ego_data:
            total_xp += ego_data.get('xp_details', {}).get('current_xp', 0)
    return total_xp


def calculate_synergy_stats() -> Dict[str, float]:
    """
    Calculate synergy stats (mind, body, soul) from all alter-egos.
    Calculate average of all abilities for each alter-ego mapped to their synergy category.
    - mind = average of mr-robot abilities
    - body = average of tyler abilities
    - soul = average of kei abilities
    """
    synergy_stats = {"mind": 0.0, "body": 0.0, "soul": 0.0}
    
    for archetype, synergy_type in SYNERGY_MAPPING.items():
        ego_data = load_alter_ego(archetype)
        if ego_data:
            abilities = ego_data.get('abilities', {})
            if abilities:
                # Calculate average of all ability values for this alter-ego
                ability_values = list(abilities.values())
                average = sum(ability_values) / len(ability_values)
                synergy_stats[synergy_type] = round(average, 2)
    
    return synergy_stats


def count_missions() -> Dict[str, int]:
    """Count missions by status."""
    counts = {
        "total": 0,
        "completed": 0,
        "failed": 0,
        "not-started": 0,
        "in-progress": 0
    }
    
    # Count not-completed missions
    for mission_file in MISSIONS_NOT_COMPLETED.glob("*.json"):
        mission_data = load_json(mission_file)
        if mission_data:
            counts["total"] += 1
            status = mission_data.get("status", "not-started")
            if status in counts:
                counts[status] += 1
    
    # Count completed missions
    for mission_file in MISSIONS_COMPLETED.glob("*.json"):
        mission_data = load_json(mission_file)
        if mission_data:
            counts["total"] += 1
            status = mission_data.get("status", "completed")
            if status == "completed":
                counts["completed"] += 1
            elif status == "failed":
                counts["failed"] += 1
    
    return counts


def count_rewards() -> Dict[str, int]:
    """Count rewards by lock status."""
    counts = {
        "total": 0,
        "unlocked": 0,
        "locked": 0
    }
    
    # Count locked rewards
    for reward_file in REWARDS_LOCKED.glob("*.json"):
        counts["total"] += 1
        counts["locked"] += 1
    
    # Count unlocked rewards
    for reward_file in REWARDS_UNLOCKED.glob("*.json"):
        counts["total"] += 1
        counts["unlocked"] += 1
    
    return counts


def update_synergy():
    """
    Update synergy.json with current stats from all alter-egos and mission/reward counts.
    Calculates XP, synergy stats (mind/body/soul), and total synergy automatically.
    Uses synergy-rules.json for level progression and chapter details.
    """
    synergy_data = load_synergy()
    if not synergy_data:
        return False
    
    # Calculate synergy XP from all alter-egos
    total_xp = calculate_synergy_xp()
    synergy_data["fight_club"]["xp_details"]["current_xp"] = total_xp
    
    # Handle level-up for synergy using synergy-rules.json
    try:
        with open(SYNERGY_RULES_FILE, 'r') as f:
            synergy_rules = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"{Colors.WARNING}Warning: Could not load synergy rules{Colors.ENDC}")
        synergy_rules = None
    
    if synergy_rules:
        current_level = synergy_data["fight_club"]["level"]
        level_data = synergy_rules.get('levels', {}).get(str(current_level), {})
        xp_to_next = level_data.get('xp_to_next_level')
        
        # Level up if needed
        while xp_to_next and total_xp >= xp_to_next:
            total_xp -= xp_to_next
            current_level += 1
            
            new_level_data = synergy_rules.get('levels', {}).get(str(current_level), {})
            synergy_data["fight_club"]["level"] = current_level
            synergy_data["fight_club"]["chapter"] = new_level_data.get('chapter', 'UNKNOWN')
            synergy_data["fight_club"]["description"] = new_level_data.get('description', '')
            synergy_data["fight_club"]["xp_details"]["xp_to_next_level"] = new_level_data.get('xp_to_next_level')
            synergy_data["fight_club"]["xp_details"]["current_xp"] = total_xp
            
            print(f"{Colors.OKGREEN}🎉 SYNERGY LEVEL UP! Now at Level {current_level} - {new_level_data.get('chapter', '')}!{Colors.ENDC}")
            
            xp_to_next = new_level_data.get('xp_to_next_level')
    
    # Calculate synergy stats (mind, body, soul)
    synergy_stats = calculate_synergy_stats()
    synergy_data["fight_club"]["synergy"] = synergy_stats
    synergy_data["fight_club"]["total_synergy"] = round(sum(synergy_stats.values()), 2)
    
    # Update mission counts
    mission_counts = count_missions()
    synergy_data["fight_club"]["missions"] = mission_counts
    
    # Update reward counts
    reward_counts = count_rewards()
    synergy_data["fight_club"]["rewards"] = reward_counts
    
    # Save updated synergy
    if save_synergy(synergy_data):
        return True
    return False


def get_all_daily_progress_files() -> List[Tuple[Path, datetime.date]]:
    """Get all daily progress JSON files sorted by date."""
    files_with_dates = []
    
    if not DAILY_PROGRESS_DIR.exists():
        return files_with_dates
    
    for year_dir in DAILY_PROGRESS_DIR.glob("*"):
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.glob("*"):
            if not month_dir.is_dir():
                continue
            for progress_file in month_dir.glob("*.json"):
                try:
                    # Extract date from filename: DD-month-YYYY.json
                    filename = progress_file.stem
                    # Parse date from filename
                    date_obj = datetime.datetime.strptime(filename, "%d-%B-%Y").date()
                    files_with_dates.append((progress_file, date_obj))
                except (ValueError, AttributeError):
                    continue
    
    # Sort by date
    files_with_dates.sort(key=lambda x: x[1])
    return files_with_dates


def get_latest_daily_progress() -> Optional[Tuple[Path, Dict, datetime.date]]:
    """Get the most recent daily progress file."""
    files = get_all_daily_progress_files()
    if not files:
        return None
    
    latest_file, latest_date = files[-1]
    data = load_json(latest_file)
    if data:
        return (latest_file, data, latest_date)
    return None


def calculate_days_since_last_checkin() -> int:
    """Calculate number of days since last check-in."""
    latest = get_latest_daily_progress()
    if not latest:
        return 999  # No check-ins yet
    
    _, _, latest_date = latest
    today = datetime.date.today()
    days_diff = (today - latest_date).days
    return days_diff


def load_daily_progress_rules() -> Optional[Dict]:
    """Load daily progress rules from daily-progress-rules.json."""
    try:
        with open(DAILY_PROGRESS_RULES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"{Colors.FAIL}Error: Could not load daily progress rules{Colors.ENDC}")
        return None


def apply_missed_checkin_penalty():
    """Apply penalties to all alter-egos when check-in streak is broken for 3+ days."""
    days_missed = calculate_days_since_last_checkin()
    rules = load_daily_progress_rules()
    
    if not rules:
        return False
    
    penalty_config = rules.get('missed_checkin_penalty', {})
    threshold = penalty_config.get('threshold_days', 3)
    
    if days_missed < threshold:
        print_info(f"Days since last check-in: {days_missed} (threshold: {threshold})")
        return False
    
    print(f"{Colors.FAIL}⚠️  MISSED CHECK-IN PENALTY!{Colors.ENDC}")
    print(f"{Colors.FAIL}   Last check-in was {days_missed} days ago (threshold: {threshold} days){Colors.ENDC}\n")
    
    penalties = penalty_config.get('penalties', {})
    xp_penalty = penalties.get('xp', -5)
    health_penalty = penalties.get('health', -3)
    energy_penalty = penalties.get('energy', -3)
    abilities_percent = penalties.get('abilities_percent', -2)
    
    # Apply penalties to all alter-egos and record history
    for archetype in ["tyler", "mr-robot", "kei"]:
        ego_data = load_alter_ego(archetype)
        if not ego_data:
            continue
        
        # Store state before penalty
        state_before = {
            'level': ego_data['level'],
            'title': ego_data['title'],
            'xp': ego_data['xp_details']['current_xp'],
            'health': ego_data['health_details']['current_health'],
            'energy': ego_data['energy_details']['current_energy'],
            'abilities': ego_data['abilities'].copy()
        }
        
        # Apply XP penalty
        ego_data['xp_details']['current_xp'] = max(0, ego_data['xp_details']['current_xp'] + xp_penalty)
        
        # Apply health penalty
        ego_data['health_details']['current_health'] = max(0, ego_data['health_details']['current_health'] + health_penalty)
        
        # Apply energy penalty
        ego_data['energy_details']['current_energy'] = max(0, ego_data['energy_details']['current_energy'] + energy_penalty)
        
        # Apply abilities penalty (percentage reduction)
        abilities_delta = {}
        for ability in ego_data['abilities']:
            current_value = ego_data['abilities'][ability]
            reduction = max(1, int(current_value * abs(abilities_percent) / 100))
            ego_data['abilities'][ability] = max(0, current_value - reduction)
            abilities_delta[ability] = -reduction
        
        save_alter_ego(archetype, ego_data)
        print(f"{Colors.FAIL}   {ego_data['name']}: {xp_penalty} XP, {health_penalty} health, {energy_penalty} energy, ~{abs(abilities_percent)}% abilities{Colors.ENDC}")
        
        # Record history for this penalty
        history_entry = {
            'history_index': get_next_history_index(),
            'alter-ego': archetype,
            'event_type': 'missed_checkin_penalty',
            'days_missed': days_missed,
            'delta_changed': {
                'xp': xp_penalty,
                'health': health_penalty,
                'energy': energy_penalty,
                'abilities': abilities_delta
            },
            'state_after_delta_applied': {
                'level': ego_data['level'],
                'title': ego_data['title'],
                'xp': ego_data['xp_details']['current_xp'],
                'health': ego_data['health_details']['current_health'],
                'energy': ego_data['energy_details']['current_energy'],
                'abilities': ego_data['abilities'].copy()
            },
            'date': datetime.date.today().isoformat()
        }
        
        record_history(history_entry)
    
    # Update synergy
    update_synergy()
    
    print(f"\n{Colors.WARNING}Penalties applied to all alter-egos. Get back on track!{Colors.ENDC}\n")
    return True


def update_habit_streak_in_synergy(habit_name: str, success: bool) -> bool:
    """Update habit streak in synergy.json and return whether milestone was reached."""
    synergy_data = load_synergy()
    if not synergy_data:
        return False
    
    habit_data = synergy_data["fight_club"]["daily_progress"]["habits"].get(habit_name)
    if not habit_data:
        return False
    
    milestone_reached = False
    
    if success:
        # Increment streak and totals
        habit_data["streak"] += 1
        habit_data["total_success"] += 1
        
        # Update best streak
        if habit_data["streak"] > habit_data["best_streak"]:
            habit_data["best_streak"] = habit_data["streak"]
        
        # Check for milestone (will be handled by caller)
        milestone_reached = True
    else:
        # Reset streak on failure
        habit_data["streak"] = 0
        habit_data["total_failures"] += 1
    
    save_synergy(synergy_data)
    return milestone_reached and success


def apply_habit_rewards(habit_results: Dict[str, str]):
    """
    Apply XP rewards to all alter-egos based on successful habits.
    Updates synergy habits tracking.
    """
    rules = load_daily_progress_rules()
    if not rules:
        return False
    
    habit_rewards = rules.get('habit_success_reward', {}).get('habits', {})
    milestones = rules.get('streak_milestone_bonus', {}).get('milestones', {})
    
    total_xp_earned = 0
    milestone_bonuses = []
    
    print(f"\n{Colors.OKGREEN}📊 HABIT ANALYSIS:{Colors.ENDC}\n")
    
    for habit_name, result in habit_results.items():
        success = (result.lower() == "success")
        
        # Update streak in synergy
        update_habit_streak_in_synergy(habit_name, success)
        
        if success:
            xp_reward = habit_rewards.get(habit_name, {}).get('xp_per_success', 0)
            total_xp_earned += xp_reward
            
            # Get current streak to check for milestone
            synergy_data = load_synergy()
            if synergy_data:
                current_streak = synergy_data["fight_club"]["daily_progress"]["habits"][habit_name]["streak"]
                
                # Check if milestone reached
                if str(current_streak) in milestones:
                    milestone_bonus = milestones[str(current_streak)].get('xp_bonus', 0)
                    milestone_bonuses.append((habit_name, current_streak, milestone_bonus))
                    total_xp_earned += milestone_bonus
                
                print(f"{Colors.OKGREEN}   ✓ {habit_name}: +{xp_reward} XP (streak: {current_streak}){Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}   ✗ {habit_name}: streak reset{Colors.ENDC}")
    
    # Show milestone bonuses
    if milestone_bonuses:
        print(f"\n{Colors.OKCYAN}🎉 STREAK MILESTONES:{Colors.ENDC}")
        for habit, streak, bonus in milestone_bonuses:
            print(f"{Colors.OKCYAN}   {habit}: {streak} day streak! +{bonus} XP bonus{Colors.ENDC}")
    
    # Apply total XP to all alter-egos
    if total_xp_earned > 0:
        print(f"\n{Colors.OKGREEN}Total XP earned: {total_xp_earned}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Applying to all alter-egos...{Colors.ENDC}\n")
        
        for archetype in ["tyler", "mr-robot", "kei"]:
            ego_data = load_alter_ego(archetype)
            if ego_data:
                ego_data['xp_details']['current_xp'] += total_xp_earned
                
                # Handle level-up
                xp_rules = load_xp_rules()
                if xp_rules:
                    current_level = ego_data['level']
                    level_data = xp_rules.get('levels', {}).get(str(current_level), {})
                    xp_to_next = level_data.get('xp_to_next_level')
                    
                    while xp_to_next and ego_data['xp_details']['current_xp'] >= xp_to_next:
                        ego_data['xp_details']['current_xp'] -= xp_to_next
                        ego_data['level'] += 1
                        
                        new_level_data = xp_rules.get('levels', {}).get(str(ego_data['level']), {})
                        ego_data['title'] = new_level_data.get('title', ego_data['title'])
                        ego_data['xp_details']['xp_to_next_level'] = new_level_data.get('xp_to_next_level')
                        
                        print(f"{Colors.OKGREEN}🎉 {ego_data['name']} LEVEL UP! Now Level {ego_data['level']} - {ego_data['title']}!{Colors.ENDC}")
                        
                        xp_to_next = ego_data['xp_details']['xp_to_next_level']
                
                save_alter_ego(archetype, ego_data)
                print(f"{Colors.OKGREEN}   {ego_data['name']}: +{total_xp_earned} XP{Colors.ENDC}")
        
        # Record milestone bonuses in history (one entry per milestone per alter-ego)
        if milestone_bonuses:
            for habit, streak, bonus in milestone_bonuses:
                for archetype in ["tyler", "mr-robot", "kei"]:
                    ego_data = load_alter_ego(archetype)
                    if ego_data:
                        history_entry = {
                            'history_index': get_next_history_index(),
                            'alter-ego': archetype,
                            'event_type': 'streak_milestone',
                            'habit_name': habit,
                            'streak_days': streak,
                            'delta_changed': {
                                'xp': bonus
                            },
                            'state_after_delta_applied': {
                                'level': ego_data['level'],
                                'title': ego_data['title'],
                                'xp': ego_data['xp_details']['current_xp'],
                                'health': ego_data['health_details']['current_health'],
                                'energy': ego_data['energy_details']['current_energy'],
                                'abilities': ego_data['abilities'].copy()
                            },
                            'date': datetime.date.today().isoformat()
                        }
                        record_history(history_entry)
        
        # Update synergy
        update_synergy()
        print(f"\n{Colors.OKGREEN}✅ Synergy updated{Colors.ENDC}\n")
    
    return True


def process_daily_progress_file(filepath: Path):
    """Process a daily progress file and apply rewards/penalties."""
    data = load_json(filepath)
    if not data:
        return False
    
    # Extract habit results
    habit_results = data.get('alter-ego-stats', {})
    if not habit_results:
        print_warning("No habit data found in daily progress file")
        return False
    
    # Apply habit rewards
    apply_habit_rewards(habit_results)
    
    # Update daily check-in streak in synergy
    synergy_data = load_synergy()
    if synergy_data:
        synergy_data["fight_club"]["daily_progress"]["daily_progress_streak"] += 1
        synergy_data["fight_club"]["daily_progress"]["days_checked_in"] += 1
        save_synergy(synergy_data)
    
    return True


def process_latest_daily_progress():
    """Process the most recent daily progress file."""
    print_header("PROCESS DAILY PROGRESS")
    
    latest = get_latest_daily_progress()
    if not latest:
        print_error("No daily progress files found!")
        return
    
    filepath, data, date = latest
    
    print_info(f"Latest check-in: {date.strftime('%d %B %Y')}")
    print_info(f"File: {filepath.name}\n")
    
    # Show habit results
    habit_results = data.get('alter-ego-stats', {})
    if habit_results:
        print(f"{Colors.BOLD}Habits for {date.strftime('%d %B %Y')}:{Colors.ENDC}\n")
        for habit, result in habit_results.items():
            status_icon = "✓" if result.lower() == "success" else "✗"
            status_color = Colors.OKGREEN if result.lower() == "success" else Colors.FAIL
            print(f"{status_color}   {status_icon} {habit}: {result}{Colors.ENDC}")
        
        print()
        confirm = get_input("Process this daily progress? (yes/no)", "yes")
        
        if confirm.lower() in ["yes", "y"]:
            if process_daily_progress_file(filepath):
                print_success("✅ Daily progress processed successfully!")
            else:
                print_error("Failed to process daily progress")
        else:
            print_info("Processing cancelled")
    else:
        print_error("No habit data found in the file")


def add_daily_progress():
    """Create a new daily progress entry."""
    print_header("ADD DAILY PROGRESS ENTRY")
    
    # Get date
    date_input = get_input("Date (YYYY-MM-DD)", datetime.date.today().isoformat())
    try:
        entry_date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
    except ValueError:
        print_error("Invalid date format! Use YYYY-MM-DD")
        return
    
    # Check if entry already exists
    year = entry_date.year
    month = entry_date.strftime("%m-%B").lower()
    day_filename = entry_date.strftime("%d-%B-%Y").lower() + ".json"
    
    target_dir = DAILY_PROGRESS_DIR / str(year) / month
    target_file = target_dir / day_filename
    
    if target_file.exists():
        print_error(f"Daily progress entry for {entry_date} already exists!")
        print_info(f"Use 'Modify Daily Progress' to update it.")
        return
    
    # Mood tracker
    print(f"\n{Colors.BOLD}MOOD TRACKER:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}   Energy options: Energized, Motivated, Calm, Okay, Distracted, Drained, Irritated, Low, Numb, Exhausted{Colors.ENDC}")
    energy = get_input("Energy level", "Okay")
    print(f"{Colors.OKCYAN}   Emotion options: Ecstatic, Happy, Content, Neutral, Tired, Stressed, Sad, Angry, Anxious, Empty{Colors.ENDC}")
    emotion = get_input("Emotion", "Neutral")
    mood_notes = get_input("Mood notes (optional)", "")
    
    # Sleep tracker
    print(f"\n{Colors.BOLD}SLEEP TRACKER:{Colors.ENDC}")
    hours_slept = get_input("Hours slept", "7")
    sleep_quality = get_input("Sleep quality (excellent/good/fair/poor)", "good")
    sleep_notes = get_input("Sleep notes (optional)", "")
    
    # Habit tracking
    print(f"\n{Colors.BOLD}HABIT TRACKING:{Colors.ENDC}")
    print_info("Mark each habit as 'success' or 'failed'\n")
    
    habits = ["no-sugar", "workout", "meditation", "reading", "coding", "no-fap", "no-junk-food"]
    habit_results = {}
    
    for habit in habits:
        result = get_input(f"{habit}", "failed")
        habit_results[habit] = result.lower()
    
    # Create daily progress object
    daily_progress = {
        "date": entry_date.isoformat(),
        "mood-tracker": {
            "energy": energy,
            "emotion": emotion,
            "notes": mood_notes
        },
        "sleep-tracker": {
            "hours_slept": int(hours_slept) if hours_slept.isdigit() else 7,
            "sleep_quality": sleep_quality,
            "notes": sleep_notes
        },
        "alter-ego-stats": habit_results
    }
    
    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    if save_json(target_file, daily_progress):
        print_success(f"Daily progress entry created for {entry_date.strftime('%d %B %Y')}")
        print_info(f"File: {target_file}")
        
        # Ask if user wants to process it now
        print()
        process_now = get_input("Process this entry now (apply rewards/penalties)? (yes/no)", "yes")
        
        if process_now.lower() in ["yes", "y"]:
            # Check for missed check-in penalty first
            days_missed = calculate_days_since_last_checkin()
            if days_missed >= 3:
                print_warning(f"\n⚠️  Last check-in was {days_missed} days ago!")
                apply_penalty = get_input("Apply missed check-in penalty? (yes/no)", "yes")
                if apply_penalty.lower() in ["yes", "y"]:
                    apply_missed_checkin_penalty()
            
            # Process the new entry
            if process_daily_progress_file(target_file):
                print_success("\n✅ Daily progress processed successfully!")
        else:
            print_info("Entry saved. You can process it later from the menu.")
    else:
        print_error("Failed to create daily progress entry")


def view_daily_progress():
    """View existing daily progress entries."""
    print_header("VIEW DAILY PROGRESS ENTRIES")
    
    files = get_all_daily_progress_files()
    if not files:
        print_error("No daily progress entries found!")
        return
    
    # Show recent entries (last 10)
    recent_files = files[-10:]
    
    print(f"{Colors.BOLD}Recent Daily Progress Entries:{Colors.ENDC}\n")
    for i, (filepath, date) in enumerate(recent_files, 1):
        data = load_json(filepath)
        if data:
            habit_results = data.get('alter-ego-stats', {})
            success_count = sum(1 for result in habit_results.values() if result.lower() == "success")
            total_habits = len(habit_results)
            
            print(f"{Colors.OKCYAN}[{i}]{Colors.ENDC} {date.strftime('%d %B %Y')} - {success_count}/{total_habits} habits successful")
    
    print()
    choice = get_input(f"View details (1-{len(recent_files)}) or 'q' to quit", "q")
    
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(recent_files):
            filepath, date = recent_files[idx]
            data = load_json(filepath)
            if data:
                print(f"\n{Colors.HEADER}═══ {date.strftime('%d %B %Y')} ═══{Colors.ENDC}\n")
                
                # Mood
                mood = data.get('mood-tracker', {})
                print(f"{Colors.BOLD}Mood:{Colors.ENDC}")
                print(f"  Energy: {mood.get('energy', 'N/A')}")
                print(f"  Emotion: {mood.get('emotion', 'N/A')}")
                if mood.get('notes'):
                    print(f"  Notes: {mood.get('notes')}")
                
                # Sleep
                sleep = data.get('sleep-tracker', {})
                print(f"\n{Colors.BOLD}Sleep:{Colors.ENDC}")
                print(f"  Hours: {sleep.get('hours_slept', 'N/A')}")
                print(f"  Quality: {sleep.get('sleep_quality', 'N/A')}")
                if sleep.get('notes'):
                    print(f"  Notes: {sleep.get('notes')}")
                
                # Habits
                habits = data.get('alter-ego-stats', {})
                print(f"\n{Colors.BOLD}Habits:{Colors.ENDC}")
                for habit, result in habits.items():
                    status_icon = "✓" if result.lower() == "success" else "✗"
                    status_color = Colors.OKGREEN if result.lower() == "success" else Colors.FAIL
                    print(f"{status_color}  {status_icon} {habit}: {result}{Colors.ENDC}")
    except ValueError:
        print_error("Invalid choice")


def modify_daily_progress():
    """Modify an existing daily progress entry."""
    print_header("MODIFY DAILY PROGRESS ENTRY")
    
    files = get_all_daily_progress_files()
    if not files:
        print_error("No daily progress entries found!")
        return
    
    # Show recent entries (last 10)
    recent_files = files[-10:]
    
    print(f"{Colors.BOLD}Recent Daily Progress Entries:{Colors.ENDC}\n")
    for i, (filepath, date) in enumerate(recent_files, 1):
        print(f"{Colors.OKCYAN}[{i}]{Colors.ENDC} {date.strftime('%d %B %Y')}")
    
    print()
    choice = get_input(f"Select entry to modify (1-{len(recent_files)})", "1")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(recent_files):
            filepath, date = recent_files[idx]
            data = load_json(filepath)
            if not data:
                print_error("Failed to load entry")
                return
            
            print(f"\n{Colors.BOLD}Modifying: {date.strftime('%d %B %Y')}{Colors.ENDC}")
            print_info("Press Enter to keep current value\n")
            
            # Modify mood
            print(f"{Colors.BOLD}MOOD TRACKER:{Colors.ENDC}")
            mood = data.get('mood-tracker', {})
            new_energy = get_input("Energy level", mood.get('energy', ''))
            if new_energy:
                mood['energy'] = new_energy
            
            new_emotion = get_input("Emotion", mood.get('emotion', ''))
            if new_emotion:
                mood['emotion'] = new_emotion
            
            new_mood_notes = get_input("Mood notes", mood.get('notes', ''))
            if new_mood_notes:
                mood['notes'] = new_mood_notes
            
            # Modify sleep
            print(f"\n{Colors.BOLD}SLEEP TRACKER:{Colors.ENDC}")
            sleep = data.get('sleep-tracker', {})
            new_hours = get_input("Hours slept", str(sleep.get('hours_slept', '')))
            if new_hours and new_hours.isdigit():
                sleep['hours_slept'] = int(new_hours)
            
            new_quality = get_input("Sleep quality", sleep.get('sleep_quality', ''))
            if new_quality:
                sleep['sleep_quality'] = new_quality
            
            new_sleep_notes = get_input("Sleep notes", sleep.get('notes', ''))
            if new_sleep_notes:
                sleep['notes'] = new_sleep_notes
            
            # Modify habits
            print(f"\n{Colors.BOLD}HABIT TRACKING:{Colors.ENDC}")
            print_info("Update habits (success/failed) or press Enter to keep current\n")
            
            habits = data.get('alter-ego-stats', {})
            for habit in habits:
                current = habits[habit]
                new_status = get_input(f"{habit} (current: {current})", "")
                if new_status:
                    habits[habit] = new_status.lower()
            
            # Save changes
            if save_json(filepath, data):
                print_success(f"\nDaily progress entry updated for {date.strftime('%d %B %Y')}")
                
                # Ask if user wants to reprocess
                print()
                reprocess = get_input("Reprocess this entry (recalculate rewards)? (yes/no)", "no")
                
                if reprocess.lower() in ["yes", "y"]:
                    # Reset synergy habits first (optional - for clean recalculation)
                    if process_daily_progress_file(filepath):
                        print_success("✅ Entry reprocessed successfully!")
                    else:
                        print_error("Failed to reprocess entry")
            else:
                print_error("Failed to update entry")
    except ValueError:
        print_error("Invalid choice")


def delete_daily_progress():
    """Delete a daily progress entry."""
    print_header("DELETE DAILY PROGRESS ENTRY")
    
    files = get_all_daily_progress_files()
    if not files:
        print_error("No daily progress entries found!")
        return
    
    # Show recent entries (last 10)
    recent_files = files[-10:]
    
    print(f"{Colors.BOLD}Recent Daily Progress Entries:{Colors.ENDC}\n")
    for i, (filepath, date) in enumerate(recent_files, 1):
        print(f"{Colors.OKCYAN}[{i}]{Colors.ENDC} {date.strftime('%d %B %Y')}")
    
    print()
    choice = get_input(f"Select entry to delete (1-{len(recent_files)})", "1")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(recent_files):
            filepath, date = recent_files[idx]
            
            confirm = get_input(f"Are you sure you want to delete the entry for {date.strftime('%d %B %Y')}? (yes/no)", "no")
            
            if confirm.lower() in ["yes", "y"]:
                filepath.unlink()
                print_success(f"Daily progress entry deleted for {date.strftime('%d %B %Y')}")
                print_warning("Note: Synergy stats and alter-ego rewards are NOT reversed.")
                print_info("You may need to manually adjust stats if needed.")
            else:
                print_info("Deletion cancelled")
    except ValueError:
        print_error("Invalid choice")


def get_reward_files(folder: Path) -> List[Path]:
    """Get all reward JSON files in a folder."""
    if not folder.exists():
        return []
    return sorted([f for f in folder.glob("*.json")])


def list_rewards(folder: Path, status_label: str) -> List[Tuple[Path, Dict]]:
    """List all rewards in a folder."""
    rewards = []
    files = get_reward_files(folder)
    
    if not files:
        print_warning(f"No {status_label} rewards found")
        return rewards
    
    print(f"\n{Colors.BOLD}{status_label.upper()} REWARDS:{Colors.ENDC}")
    for idx, file in enumerate(files, 1):
        reward = load_json(file)
        if reward:
            reward_id = reward.get("reward_id", file.stem.split('-')[0])
            title = reward.get("title", "Untitled")
            reward_type = reward.get("reward_type", "unknown")
            missions = reward.get("associated_mission_ids", [])
            
            print(f"  {Colors.OKBLUE}{idx}. [{reward_id}]{Colors.ENDC} {title}")
            print(f"      Type: {reward_type} | Missions: {', '.join(missions) if missions else 'None'}")
            
            rewards.append((file, reward))
    
    return rewards


def create_reward(mission_code: str = None) -> Optional[Dict]:
    """Create a new reward and return reward data."""
    print(f"\n{Colors.HEADER}═══ CREATE REWARD ═══{Colors.ENDC}\n")
    
    # Generate reward ID
    reward_id = get_next_reward_id()
    
    # Reward details
    title = get_input("Reward title")
    if not title:
        print_error("Reward title is required!")
        return None
    
    description = get_input("Reward description")
    
    # Reward type
    print(f"\n{Colors.OKCYAN}   Reward type options: street, vanguard, legendary, apex, mythic{Colors.ENDC}")
    print_info("Reward Type:")
    type_choice = get_choice(["Street", "Vanguard", "Legendary", "Apex", "Mythic"], "Type")
    reward_type = ["street", "vanguard", "legendary", "apex", "mythic"][type_choice - 1]
    
    # Badge icon
    badge_icon = get_input("Badge icon path", "assets/rewards/default.png")
    
    # Associated missions
    associated_missions = []
    if mission_code:
        associated_missions.append(mission_code)
        print_info(f"Associated with mission: {mission_code}")
    
    # Create reward object
    reward = {
        "reward_id": reward_id,
        "title": title,
        "description": description,
        "associated_mission_ids": associated_missions,
        "reward_type": reward_type,
        "is_locked": True,
        "badge_icon": badge_icon
    }
    
    # Generate filename
    filename = f"{reward_id}-{title_to_filename(title)}.json"
    filepath = REWARDS_LOCKED / filename
    
    # Save reward
    if save_json(filepath, reward):
        print_success(f"Reward created: {title}")
        print_info(f"Reward ID: {reward_id}")
        print_info(f"File: {filename}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
        
        return {
            "reward_type": reward_type,
            "title": title,
            "reward_id": reward_id
        }
    else:
        print_error("Failed to create reward")
        return None

def add_new_mission():
    """Add a new mission for an alter ego."""
    print_header("ADD NEW MISSION")
    
    # Select alter ego
    print_info("Select alter ego for this mission:")
    ego_names = list(ALTER_EGOS.keys())
    ego_labels = [f"{ALTER_EGOS[ego]['name']} - {ALTER_EGOS[ego]['role']}" for ego in ego_names]
    ego_choice = get_choice(ego_labels, "Alter Ego")
    alter_ego = ego_names[ego_choice - 1]
    
    # Generate mission ID
    mission_code = get_next_mission_id(alter_ego)
    
    # Mission details
    title = get_input("Mission title")
    if not title:
        print_error("Mission title is required!")
        return
    
    description = get_input("Mission description")
    
    # Difficulty
    print(f"{Colors.OKCYAN}   Difficulty options: easy, medium, hard{Colors.ENDC}")
    difficulty_choice = get_choice(["easy", "medium", "hard"], "Difficulty")
    difficulty = ["easy", "medium", "hard"][difficulty_choice - 1]
    
    # Progress tracking
    total_progress = get_input("Total units to complete (e.g., days, tasks)", "1")
    
    # Dates
    start_date = get_input("Start date (YYYY-MM-DD)", datetime.date.today().isoformat())
    due_date = get_input("Due date (YYYY-MM-DD)")
    
    # Mission icon
    mission_icon = get_input("Mission icon path", "assets/badges/default.png")
    
    # Get stat changes for completion
    print(f"\n{Colors.BOLD}STAT CHANGES ON COMPLETION:{Colors.ENDC}")
    health_complete = int(get_input("Health change", "0"))
    energy_complete = int(get_input("Energy change", "0"))
    
    abilities_complete = {}
    print_info(f"\nAbility changes (for {ALTER_EGOS[alter_ego]['name']}):")
    for ability in ALTER_EGOS[alter_ego]["abilities"]:
        value = get_input(f"  {ability.capitalize()}", "0")
        abilities_complete[ability] = int(value)
    
    # Get stat changes for failure
    print(f"\n{Colors.BOLD}STAT CHANGES ON FAILURE:{Colors.ENDC}")
    health_failure = int(get_input("Health change", "0"))
    energy_failure = int(get_input("Energy change", "0"))
    
    abilities_failure = {}
    print_info(f"\nAbility changes (for {ALTER_EGOS[alter_ego]['name']}):")
    for ability in ALTER_EGOS[alter_ego]["abilities"]:
        value = get_input(f"  {ability.capitalize()}", "0")
        abilities_failure[ability] = int(value)
    
    # Ask about reward association
    reward_list = []
    has_reward = get_input("\nDoes this mission have a reward? (yes/no)", "no")
    
    if has_reward.lower() in ["yes", "y"]:
        print_info("\nReward Options:")
        print(f"{Colors.OKGREEN}[1]{Colors.ENDC} Create new reward")
        print(f"{Colors.OKGREEN}[2]{Colors.ENDC} Link to existing reward")
        print(f"{Colors.OKGREEN}[3]{Colors.ENDC} No reward")
        
        reward_choice = get_input("Choose option (1-3)", "3")
        
        if reward_choice == "1":
            # Create new reward
            reward_data = create_reward(mission_code)
            if reward_data:
                reward_list.append(reward_data)
        
        elif reward_choice == "2":
            # List existing rewards
            print_info("\nExisting Locked Rewards:")
            locked_rewards = list_rewards(REWARDS_LOCKED, "locked")
            
            if locked_rewards:
                reward_idx = get_choice([f"Reward {i}" for i in range(1, len(locked_rewards) + 1)], "Select reward")
                reward_file, reward_data = locked_rewards[reward_idx - 1]
                
                # Add mission to reward's associated missions
                if "associated_mission_ids" not in reward_data:
                    reward_data["associated_mission_ids"] = []
                
                if mission_code not in reward_data["associated_mission_ids"]:
                    reward_data["associated_mission_ids"].append(mission_code)
                    save_json(reward_file, reward_data)
                    print_success(f"Linked to reward: {reward_data['title']}")
                
                # Add reward to mission
                reward_list.append({
                    "reward_type": reward_data.get("reward_type", "common"),
                    "title": reward_data.get("title", ""),
                    "reward_id": reward_data.get("reward_id", "")
                })
    
    # Create mission object matching exact structure
    mission = {
        "archetype": alter_ego,
        "mission_code": mission_code,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "status": "not-started",
        "progress": {
            "current": 0,
            "total": int(total_progress)
        },
        "archetype_stat_change": {
            "on_complete": {
                "health": health_complete,
                "energy": energy_complete,
                "abilities": abilities_complete
            },
            "on_failure": {
                "health": health_failure,
                "energy": energy_failure,
                "abilities": abilities_failure
            }
        },
        "reward": reward_list,
        "mission_icon": mission_icon,
        "due_date": due_date,
        "start_date": start_date,
        "completion_date": None
    }
    
    # Generate filename: missionID-title-in-kebab-case.json
    filename = f"{mission_code}-{title_to_filename(title)}.json"
    mission_file = MISSIONS_NOT_COMPLETED / filename
    
    if save_json(mission_file, mission):
        print_success(f"Mission created: {title}")
        print_info(f"Mission Code: {mission_code}")
        print_info(f"Assigned to: {ALTER_EGOS[alter_ego]['name']}")
        print_info(f"File: {filename}")
        
        if reward_list:
            print_info(f"Rewards: {', '.join([r['title'] for r in reward_list])}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
    else:
        print_error("Failed to create mission")

def list_missions(folder: Path, status_label: str) -> List[Tuple[Path, Dict]]:
    """List all missions in a folder."""
    missions = []
    files = get_mission_files(folder)
    
    if not files:
        print_warning(f"No {status_label} missions found")
        return missions
    
    print(f"\n{Colors.BOLD}{status_label.upper()} MISSIONS:{Colors.ENDC}")
    for idx, file in enumerate(files, 1):
        mission = load_json(file)
        if mission:
            archetype = mission.get("archetype", "unknown")
            ego_name = ALTER_EGOS.get(archetype, {}).get("name", archetype)
            title = mission.get("title", "Untitled")
            mission_code = mission.get("mission_code", file.stem.split('-')[0])
            
            # Archetype-specific colors
            archetype_colors = {
                "kei": Colors.OKCYAN,      # Cyan for Kei (water)
                "mr-robot": Colors.OKGREEN, # Green for Mr-Robot (tech)
                "tyler": Colors.FAIL        # Red for Tyler (fire)
            }
            archetype_color = archetype_colors.get(archetype, Colors.OKBLUE)
            
            # Show progress if available
            progress = mission.get("progress", {})
            current = progress.get("current", 0)
            total = progress.get("total", 1)
            progress_pct = (current / total * 100) if total > 0 else 0
            
            status = mission.get("status", "unknown")
            
            # Status color coding
            status_colors = {
                "not-started": Colors.WARNING,
                "in-progress": Colors.OKCYAN,
                "completed": Colors.OKGREEN,
                "failed": Colors.FAIL
            }
            status_color = status_colors.get(status, Colors.ENDC)
            
            print(f"  {Colors.OKBLUE}{idx}.{Colors.ENDC} {archetype_color}[{mission_code}]{Colors.ENDC} {Colors.BOLD}{title}{Colors.ENDC}")
            print(f"      Archetype: {archetype_color}{ego_name}{Colors.ENDC} | Status: {status_color}{status}{Colors.ENDC} | Progress: {current}/{total} ({progress_pct:.0f}%)")
            
            if mission.get("due_date"):
                print(f"      Due: {mission['due_date']}")
            
            missions.append((file, mission))
    
    return missions

def mark_mission_completed():
    """Mark a mission as completed."""
    print_header("MARK MISSION AS COMPLETED")
    
    missions = list_missions(MISSIONS_NOT_COMPLETED, "not-completed")
    if not missions:
        return
    
    choice = get_choice([f"Mission {i}" for i in range(1, len(missions) + 1)], "Select mission to complete")
    mission_file, mission = missions[choice - 1]
    
    # Update mission
    mission["status"] = "completed"
    mission["progress"]["current"] = mission["progress"]["total"]
    mission["completion_date"] = datetime.date.today().isoformat()
    
    # Collect unlocked reward IDs
    unlocked_rewards = []
    
    # Unlock associated rewards
    if mission.get("reward"):
        for reward_info in mission["reward"]:
            reward_id = reward_info.get("reward_id")
            if reward_id:
                # Find and unlock the reward
                for reward_file in REWARDS_LOCKED.glob(f"{reward_id}-*.json"):
                    reward_data = load_json(reward_file)
                    if reward_data:
                        reward_data["is_locked"] = False
                        
                        # Move to unlocked folder
                        new_reward_file = REWARDS_UNLOCKED / reward_file.name
                        if save_json(new_reward_file, reward_data):
                            reward_file.unlink()
                            unlocked_rewards.append(reward_id)
                            print_success(f"🎁 Reward unlocked: {reward_data['title']}")
    
    # Apply stat changes to alter-ego
    xp_rules = load_xp_rules()
    ego_data = load_alter_ego(mission['archetype'])
    
    if ego_data and xp_rules:
        # Get stat changes from mission
        on_complete = mission["archetype_stat_change"]["on_complete"]
        
        # Store state before changes
        state_before = {
            'level': ego_data['level'],
            'title': ego_data['title'],
            'xp': ego_data['xp_details']['current_xp'],
            'health': ego_data['health_details']['current_health'],
            'energy': ego_data['energy_details']['current_energy'],
            'abilities': ego_data['abilities'].copy()
        }
        
        # Apply changes
        delta_applied = apply_stat_changes(ego_data, on_complete, xp_rules)
        
        # Save updated alter-ego
        if save_alter_ego(mission['archetype'], ego_data):
            print_success(f"✅ Updated {ego_data['name']} stats")
            
            # Record history
            history_entry = {
                'history_index': get_next_history_index(),
                'alter-ego': mission['archetype'],
                'mission_associated': mission_file.stem,
                'state': 'completed',
                'delta_changed': delta_applied,
                'state_after_delta_applied': {
                    'level': ego_data['level'],
                    'title': ego_data['title'],
                    'xp': ego_data['xp_details']['current_xp'],
                    'health': ego_data['health_details']['current_health'],
                    'energy': ego_data['energy_details']['current_energy'],
                    'abilities': ego_data['abilities'].copy()
                },
                'date': mission["completion_date"]
            }
            
            if unlocked_rewards:
                history_entry['reward_unlocked'] = unlocked_rewards
            
            record_history(history_entry)
            print_success(f"📝 History recorded (entry #{history_entry['history_index']})")
    
    # Move to completed folder
    new_file = MISSIONS_COMPLETED / mission_file.name
    if save_json(new_file, mission):
        mission_file.unlink()  # Delete from not-completed
        
        print_success(f"Mission completed: {mission['title']}")
        print_info(f"Moved to: {MISSIONS_COMPLETED}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
        
        # Show rewards
        on_complete = mission["archetype_stat_change"]["on_complete"]
        print(f"\n{Colors.OKGREEN}REWARDS EARNED:{Colors.ENDC}")
        if 'xp' in on_complete:
            print(f"  XP: {on_complete['xp']:+d}")
        print(f"  Health: {on_complete['health']:+d}")
        print(f"  Energy: {on_complete['energy']:+d}")
        
        print(f"\n{Colors.OKGREEN}  Abilities:{Colors.ENDC}")
        for ability, value in on_complete["abilities"].items():
            if value != 0:
                print(f"    • {ability.capitalize()}: {value:+d}")
    else:
        print_error("Failed to mark mission as completed")


def mark_mission_failed():
    """Mark a mission as failed."""
    print_header("MARK MISSION AS FAILED")
    
    missions = list_missions(MISSIONS_NOT_COMPLETED, "not-completed")
    if not missions:
        return
    
    choice = get_choice([f"Mission {i}" for i in range(1, len(missions) + 1)], "Select mission to mark as failed")
    mission_file, mission = missions[choice - 1]
    
    # Update mission
    mission["status"] = "failed"
    mission["completion_date"] = datetime.date.today().isoformat()
    
    # Keep rewards locked (failed mission doesn't unlock rewards)
    
    # Apply stat penalties to alter-ego
    xp_rules = load_xp_rules()
    ego_data = load_alter_ego(mission['archetype'])
    
    if ego_data and xp_rules:
        # Get stat changes from mission
        on_failure = mission["archetype_stat_change"]["on_failure"]
        
        # Store state before changes
        state_before = {
            'level': ego_data['level'],
            'title': ego_data['title'],
            'xp': ego_data['xp_details']['current_xp'],
            'health': ego_data['health_details']['current_health'],
            'energy': ego_data['energy_details']['current_energy'],
            'abilities': ego_data['abilities'].copy()
        }
        
        # Apply changes (penalties)
        delta_applied = apply_stat_changes(ego_data, on_failure, xp_rules)
        
        # Save updated alter-ego
        if save_alter_ego(mission['archetype'], ego_data):
            print_warning(f"⚠️  Updated {ego_data['name']} stats (penalties applied)")
            
            # Record history
            history_entry = {
                'history_index': get_next_history_index(),
                'alter-ego': mission['archetype'],
                'mission_associated': mission_file.stem,
                'state': 'failed',
                'delta_changed': delta_applied,
                'state_after_delta_applied': {
                    'level': ego_data['level'],
                    'title': ego_data['title'],
                    'xp': ego_data['xp_details']['current_xp'],
                    'health': ego_data['health_details']['current_health'],
                    'energy': ego_data['energy_details']['current_energy'],
                    'abilities': ego_data['abilities'].copy()
                },
                'date': mission["completion_date"]
            }
            
            record_history(history_entry)
            print_success(f"📝 History recorded (entry #{history_entry['history_index']})")
    
    # Move to completed folder (with failed status)
    new_file = MISSIONS_COMPLETED / mission_file.name
    if save_json(new_file, mission):
        mission_file.unlink()  # Delete from not-completed
        
        print_warning(f"Mission failed: {mission['title']}")
        print_info(f"Moved to: {MISSIONS_COMPLETED}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
        
        # Show penalties
        on_failure = mission["archetype_stat_change"]["on_failure"]
        print(f"\n{Colors.FAIL}PENALTIES APPLIED:{Colors.ENDC}")
        if 'xp' in on_failure:
            print(f"  XP: {on_failure['xp']:+d}")
        print(f"  Health: {on_failure['health']:+d}")
        print(f"  Energy: {on_failure['energy']:+d}")
        
        print(f"\n{Colors.FAIL}  Abilities:{Colors.ENDC}")
        for ability, value in on_failure["abilities"].items():
            if value != 0:
                print(f"    • {ability.capitalize()}: {value:+d}")
    else:
        print_error("Failed to mark mission as failed")


def delete_mission():
    """Delete a mission."""
    print_header("DELETE MISSION")
    
    print_info("Select folder:")
    folder_choice = get_choice(["Not Completed", "Completed"], "Folder")
    
    folders = [MISSIONS_NOT_COMPLETED, MISSIONS_COMPLETED]
    folder = folders[folder_choice - 1]
    status_labels = ["not-completed", "completed"]
    
    missions = list_missions(folder, status_labels[folder_choice - 1])
    if not missions:
        return
    
    choice = get_choice([f"Mission {i}" for i in range(1, len(missions) + 1)], "Select mission to delete")
    mission_file, mission = missions[choice - 1]
    
    confirm = get_input(f"Are you sure you want to delete '{mission['title']}'? (yes/no)", "no")
    if confirm.lower() in ["yes", "y"]:
        mission_file.unlink()
        print_success(f"Mission deleted: {mission['title']}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
    else:
        print_info("Deletion cancelled")

def modify_mission():
    """Modify an existing mission."""
    print_header("MODIFY MISSION")
    
    print_info("Select folder:")
    folder_choice = get_choice(["Not Completed", "Completed"], "Folder")
    
    folders = [MISSIONS_NOT_COMPLETED, MISSIONS_COMPLETED]
    folder = folders[folder_choice - 1]
    status_labels = ["not-completed", "completed"]
    
    missions = list_missions(folder, status_labels[folder_choice - 1])
    if not missions:
        return
    
    choice = get_choice([f"Mission {i}" for i in range(1, len(missions) + 1)], "Select mission to modify")
    mission_file, mission = missions[choice - 1]
    
    print(f"\n{Colors.BOLD}Modifying: {mission['title']}{Colors.ENDC}")
    print_info("Press Enter to keep current value")
    
    # Track if title changed for filename update
    old_title = mission.get("title", "")
    title_changed = False
    
    # Modify basic fields
    new_title = get_input("Title", mission.get("title", ""))
    if new_title and new_title != old_title:
        mission["title"] = new_title
        title_changed = True
    
    new_desc = get_input("Description", mission.get("description", ""))
    if new_desc:
        mission["description"] = new_desc
    
    print(f"{Colors.OKCYAN}   Difficulty options: easy, medium, hard{Colors.ENDC}")
    new_diff = get_input("Difficulty", mission.get("difficulty", "medium"))
    if new_diff:
        mission["difficulty"] = new_diff
    
    print(f"{Colors.OKCYAN}   Status options: not-started, in-progress, completed, failed{Colors.ENDC}")
    new_status = get_input("Status", mission.get("status", "not-started"))
    if new_status:
        mission["status"] = new_status
    
    # Modify progress
    current_progress = mission.get("progress", {}).get("current", 0)
    total_progress = mission.get("progress", {}).get("total", 1)
    
    new_current = get_input(f"Current progress", str(current_progress))
    if new_current:
        mission["progress"]["current"] = int(new_current)
    
    new_total = get_input(f"Total progress", str(total_progress))
    if new_total:
        mission["progress"]["total"] = int(new_total)
    
    # Modify dates
    new_due = get_input("Due date (YYYY-MM-DD)", mission.get("due_date", ""))
    if new_due:
        mission["due_date"] = new_due
    
    # Manage rewards
    print_info("\nManage Rewards?")
    manage_rewards = get_input("Modify rewards? (yes/no)", "no")
    
    if manage_rewards.lower() in ["yes", "y"]:
        current_rewards = mission.get("reward", [])
        
        if current_rewards:
            print(f"\n{Colors.OKCYAN}Current Rewards:{Colors.ENDC}")
            for idx, r in enumerate(current_rewards, 1):
                print(f"  {idx}. {r.get('title', 'Unknown')} ({r.get('reward_id', 'Unknown')})")
            
            print_info("\nReward Actions:")
            print(f"{Colors.OKGREEN}[1]{Colors.ENDC} Add new reward")
            print(f"{Colors.OKGREEN}[2]{Colors.ENDC} Remove a reward")
            print(f"{Colors.OKGREEN}[3]{Colors.ENDC} Keep current")
            
            reward_action = get_input("Choose option (1-3)", "3")
            
            if reward_action == "1":
                # Add reward
                print_info("\nAdd Reward:")
                print(f"{Colors.OKGREEN}[1]{Colors.ENDC} Create new reward")
                print(f"{Colors.OKGREEN}[2]{Colors.ENDC} Link existing reward")
                
                add_choice = get_input("Choose option (1-2)", "2")
                
                if add_choice == "1":
                    reward_data = create_reward(mission.get("mission_code"))
                    if reward_data:
                        mission["reward"].append(reward_data)
                
                elif add_choice == "2":
                    locked_rewards = list_rewards(REWARDS_LOCKED, "locked")
                    if locked_rewards:
                        reward_idx = get_choice([f"Reward {i}" for i in range(1, len(locked_rewards) + 1)], "Select reward")
                        reward_file, reward_data = locked_rewards[reward_idx - 1]
                        
                        # Update reward's associated missions
                        if "associated_mission_ids" not in reward_data:
                            reward_data["associated_mission_ids"] = []
                        
                        mission_code = mission.get("mission_code", "")
                        if mission_code and mission_code not in reward_data["associated_mission_ids"]:
                            reward_data["associated_mission_ids"].append(mission_code)
                            save_json(reward_file, reward_data)
                        
                        # Add to mission
                        mission["reward"].append({
                            "reward_type": reward_data.get("reward_type", "common"),
                            "title": reward_data.get("title", ""),
                            "reward_id": reward_data.get("reward_id", "")
                        })
                        print_success(f"Linked to reward: {reward_data['title']}")
            
            elif reward_action == "2":
                # Remove reward
                if len(current_rewards) > 0:
                    rem_idx = get_choice([f"{r.get('title', 'Unknown')}" for r in current_rewards], "Select reward to remove")
                    removed_reward = current_rewards.pop(rem_idx - 1)
                    
                    # Update reward file to remove mission association
                    reward_id = removed_reward.get("reward_id")
                    if reward_id:
                        for folder in [REWARDS_LOCKED, REWARDS_UNLOCKED]:
                            for reward_file in folder.glob(f"{reward_id}-*.json"):
                                reward_data = load_json(reward_file)
                                if reward_data:
                                    mission_code = mission.get("mission_code", "")
                                    if mission_code in reward_data.get("associated_mission_ids", []):
                                        reward_data["associated_mission_ids"].remove(mission_code)
                                        save_json(reward_file, reward_data)
                    
                    print_success(f"Removed reward: {removed_reward.get('title', 'Unknown')}")
        else:
            # No current rewards, ask to add
            add_reward = get_input("Add a reward? (yes/no)", "no")
            if add_reward.lower() in ["yes", "y"]:
                print_info("\nAdd Reward:")
                print(f"{Colors.OKGREEN}[1]{Colors.ENDC} Create new reward")
                print(f"{Colors.OKGREEN}[2]{Colors.ENDC} Link existing reward")
                
                add_choice = get_input("Choose option (1-2)", "2")
                
                if add_choice == "1":
                    reward_data = create_reward(mission.get("mission_code"))
                    if reward_data:
                        mission["reward"] = [reward_data]
                
                elif add_choice == "2":
                    locked_rewards = list_rewards(REWARDS_LOCKED, "locked")
                    if locked_rewards:
                        reward_idx = get_choice([f"Reward {i}" for i in range(1, len(locked_rewards) + 1)], "Select reward")
                        reward_file, reward_data = locked_rewards[reward_idx - 1]
                        
                        # Update reward's associated missions
                        if "associated_mission_ids" not in reward_data:
                            reward_data["associated_mission_ids"] = []
                        
                        mission_code = mission.get("mission_code", "")
                        if mission_code and mission_code not in reward_data["associated_mission_ids"]:
                            reward_data["associated_mission_ids"].append(mission_code)
                            save_json(reward_file, reward_data)
                        
                        # Add to mission
                        mission["reward"] = [{
                            "reward_type": reward_data.get("reward_type", "common"),
                            "title": reward_data.get("title", ""),
                            "reward_id": reward_data.get("reward_id", "")
                        }]
                        print_success(f"Linked to reward: {reward_data['title']}")
    
    # Ask about status change
    print_info("\nChange status?")
    status_choice = get_choice(
        ["Keep current status", "not-started", "in-progress", "completed", "failed"],
        "Status"
    )
    if status_choice > 1:
        statuses = ["not-started", "in-progress", "completed", "failed"]
        new_status = statuses[status_choice - 2]
        old_status = mission.get("status", "not-started")
        mission["status"] = new_status
        
        # If status changed to completed/failed, set completion date
        if new_status in ["completed", "failed"] and not mission.get("completion_date"):
            mission["completion_date"] = datetime.date.today().isoformat()
        
        # Move file if status folder needs to change
        if new_status in ["completed", "failed"] and folder == MISSIONS_NOT_COMPLETED:
            # Generate filename with new title if changed
            current_title = mission["title"]
            filename = f"{mission['mission_code']}-{title_to_filename(current_title)}.json"
            new_file = MISSIONS_COMPLETED / filename
            if save_json(new_file, mission):
                mission_file.unlink()
                print_success(f"Mission updated and moved to completed folder")
            return
        elif new_status in ["not-started", "in-progress"] and folder == MISSIONS_COMPLETED:
            # Move back to not-completed
            current_title = mission["title"]
            filename = f"{mission['mission_code']}-{title_to_filename(current_title)}.json"
            new_file = MISSIONS_NOT_COMPLETED / filename
            if save_json(new_file, mission):
                mission_file.unlink()
                print_success(f"Mission updated and moved to not-completed folder")
            return
    
    # Check if filename needs to be updated (title changed)
    if title_changed:
        new_filename = f"{mission['mission_code']}-{title_to_filename(mission['title'])}.json"
        new_filepath = folder / new_filename
        
        if save_json(new_filepath, mission):
            if new_filepath != mission_file:
                mission_file.unlink()  # Remove old file
            print_success(f"Mission updated: {mission['title']}")
            print_info(f"File renamed to: {new_filename}")
    else:
        # Save to same file
        if save_json(mission_file, mission):
            print_success(f"Mission updated: {mission['title']}")
            
            # Update synergy (missions stats might have changed)
            if update_synergy():
                print_success("🔗 Synergy updated")
        else:
            print_error("Failed to update mission")

def update_mission_progress():
    """Update progress for an ongoing mission."""
    print_header("UPDATE MISSION PROGRESS")
    
    missions = list_missions(MISSIONS_NOT_COMPLETED, "not-completed")
    if not missions:
        return
    
    choice = get_choice([f"Mission {i}" for i in range(1, len(missions) + 1)], "Select mission to update")
    mission_file, mission = missions[choice - 1]
    
    current = mission["progress"]["current"]
    total = mission["progress"]["total"]
    
    print(f"\n{Colors.OKCYAN}Mission: {mission['title']}{Colors.ENDC}")
    print(f"Current Progress: {current}/{total} ({current/total*100:.0f}%)")
    
    new_progress = get_input(f"Enter new progress value (0-{total})", str(current))
    if new_progress:
        new_val = int(new_progress)
        if 0 <= new_val <= total:
            mission["progress"]["current"] = new_val
            
            # Update status based on progress
            if new_val == 0:
                mission["status"] = "not-started"
            elif new_val < total:
                mission["status"] = "in-progress"
            elif new_val == total:
                print_warning("Progress complete! Use 'Mark Mission as Completed' to officially complete.")
                mission["status"] = "in-progress"
            
            if save_json(mission_file, mission):
                print_success(f"Progress updated: {new_val}/{total} ({new_val/total*100:.0f}%)")
            else:
                print_error("Failed to update progress")
        else:
            print_error(f"Progress must be between 0 and {total}")


def manage_rewards():
    """Manage rewards - view, create, modify, delete."""
    print_header("MANAGE REWARDS")
    
    options = [
        "View All Rewards",
        "Create New Reward",
        "Modify Reward",
        "Delete Reward",
        "Back to Main Menu"
    ]
    
    choice = get_choice(options, "Reward Management")
    
    if choice == 1:
        # View all rewards
        print_header("ALL REWARDS")
        list_rewards(REWARDS_LOCKED, "locked")
        list_rewards(REWARDS_UNLOCKED, "unlocked")
    
    elif choice == 2:
        # Create new reward
        create_reward()
    
    elif choice == 3:
        # Modify reward
        modify_reward()
    
    elif choice == 4:
        # Delete reward
        delete_reward()


def modify_reward():
    """Modify an existing reward."""
    print_header("MODIFY REWARD")
    
    print_info("Select folder:")
    folder_choice = get_choice(["Locked", "Unlocked"], "Folder")
    
    folders = [REWARDS_LOCKED, REWARDS_UNLOCKED]
    folder = folders[folder_choice - 1]
    status_labels = ["locked", "unlocked"]
    
    rewards = list_rewards(folder, status_labels[folder_choice - 1])
    if not rewards:
        return
    
    choice = get_choice([f"Reward {i}" for i in range(1, len(rewards) + 1)], "Select reward to modify")
    reward_file, reward = rewards[choice - 1]
    
    print(f"\n{Colors.BOLD}Modifying: {reward['title']}{Colors.ENDC}")
    print_info("Press Enter to keep current value")
    
    # Track if title changed
    old_title = reward.get("title", "")
    title_changed = False
    
    # Modify fields
    new_title = get_input("Title", reward.get("title", ""))
    if new_title and new_title != old_title:
        reward["title"] = new_title
        title_changed = True
    
    new_desc = get_input("Description", reward.get("description", ""))
    if new_desc:
        reward["description"] = new_desc
    
    # Reward type
    current_type = reward.get("reward_type", "common")
    print(f"\n{Colors.OKCYAN}   Reward type options: street, vanguard, legendary, apex, mythic{Colors.ENDC}")
    print_info(f"Current type: {current_type}")
    change_type = get_input("Change reward type? (yes/no)", "no")
    
    if change_type.lower() in ["yes", "y"]:
        type_choice = get_choice(["Street", "Vanguard", "Legendary", "Apex", "Mythic"], "Type")
        reward["reward_type"] = ["street", "vanguard", "legendary", "apex", "mythic"][type_choice - 1]
    
    # Badge icon
    new_icon = get_input("Badge icon path", reward.get("badge_icon", ""))
    if new_icon:
        reward["badge_icon"] = new_icon
    
    # Manage associated missions
    print_info("\nManage Associated Missions?")
    manage_missions = get_input("Modify associated missions? (yes/no)", "no")
    
    if manage_missions.lower() in ["yes", "y"]:
        current_missions = reward.get("associated_mission_ids", [])
        
        if current_missions:
            print(f"\n{Colors.OKCYAN}Current Missions: {', '.join(current_missions)}{Colors.ENDC}")
            print_info("\nMission Actions:")
            print(f"{Colors.OKGREEN}[1]{Colors.ENDC} Add mission")
            print(f"{Colors.OKGREEN}[2]{Colors.ENDC} Remove mission")
            print(f"{Colors.OKGREEN}[3]{Colors.ENDC} Keep current")
            
            mission_action = get_input("Choose option (1-3)", "3")
            
            if mission_action == "1":
                mission_id = get_input("Enter mission code to add (e.g., K01, M02)")
                if mission_id and mission_id not in current_missions:
                    reward["associated_mission_ids"].append(mission_id.upper())
                    print_success(f"Added mission: {mission_id.upper()}")
            
            elif mission_action == "2":
                if len(current_missions) > 0:
                    rem_idx = get_choice(current_missions, "Select mission to remove")
                    removed = current_missions.pop(rem_idx - 1)
                    print_success(f"Removed mission: {removed}")
        else:
            add_mission = get_input("Add a mission association? (yes/no)", "no")
            if add_mission.lower() in ["yes", "y"]:
                mission_id = get_input("Enter mission code (e.g., K01, M02)")
                if mission_id:
                    reward["associated_mission_ids"] = [mission_id.upper()]
                    print_success(f"Added mission: {mission_id.upper()}")
    
    # Handle filename change if title changed
    if title_changed:
        new_filename = f"{reward['reward_id']}-{title_to_filename(reward['title'])}.json"
        new_filepath = folder / new_filename
        
        if save_json(new_filepath, reward):
            if new_filepath != reward_file:
                reward_file.unlink()
            print_success(f"Reward updated: {reward['title']}")
            print_info(f"File renamed to: {new_filename}")
            
            # Update synergy
            if update_synergy():
                print_success("🔗 Synergy updated")
    else:
        if save_json(reward_file, reward):
            print_success(f"Reward updated: {reward['title']}")
            
            # Update synergy
            if update_synergy():
                print_success("🔗 Synergy updated")
        else:
            print_error("Failed to update reward")


def delete_reward():
    """Delete a reward."""
    print_header("DELETE REWARD")
    
    print_info("Select folder:")
    folder_choice = get_choice(["Locked", "Unlocked"], "Folder")
    
    folders = [REWARDS_LOCKED, REWARDS_UNLOCKED]
    folder = folders[folder_choice - 1]
    status_labels = ["locked", "unlocked"]
    
    rewards = list_rewards(folder, status_labels[folder_choice - 1])
    if not rewards:
        return
    
    choice = get_choice([f"Reward {i}" for i in range(1, len(rewards) + 1)], "Select reward to delete")
    reward_file, reward = rewards[choice - 1]
    
    print(f"\n{Colors.FAIL}Reward: {reward['title']}{Colors.ENDC}")
    
    # Show associated missions
    if reward.get("associated_mission_ids"):
        print_warning(f"This reward is associated with missions: {', '.join(reward['associated_mission_ids'])}")
        print_warning("Deleting will remove reward references from these missions.")
    
    confirm = get_input(f"Are you sure you want to delete '{reward['title']}'? (yes/no)", "no")
    if confirm.lower() in ["yes", "y"]:
        # Remove reward from associated missions
        reward_id = reward.get("reward_id")
        for mission_id in reward.get("associated_mission_ids", []):
            # Find and update mission files
            for mission_folder in [MISSIONS_NOT_COMPLETED, MISSIONS_COMPLETED]:
                for mission_file in mission_folder.glob(f"{mission_id}-*.json"):
                    mission_data = load_json(mission_file)
                    if mission_data:
                        # Remove this reward from mission's reward list
                        mission_data["reward"] = [
                            r for r in mission_data.get("reward", [])
                            if r.get("reward_id") != reward_id
                        ]
                        save_json(mission_file, mission_data)
        
        # Delete reward file
        reward_file.unlink()
        print_success(f"Reward deleted: {reward['title']}")
        
        # Update synergy
        if update_synergy():
            print_success("🔗 Synergy updated")
    else:
        print_info("Deletion cancelled")


def main_menu():
    """Display main menu and handle user choice."""
    while True:
        print_header("FIGHT CLUB - ALTER EGO MANAGEMENT")
        
        options = [
            "📝 Add Daily Progress Entry",
            "👁️  View Daily Progress Entries",
            "✏️  Modify Daily Progress Entry",
            "🗑️  Delete Daily Progress Entry",
            "🎯 Create New Mission",
            "✅ Mark Mission as Completed",
            "❌ Mark Mission as Failed",
            "📈 Update Mission Progress",
            "✏️  Modify Mission",
            "🗑️  Delete Mission",
            "📊 View All Missions",
            "🎁 Manage Rewards",
            "🚪 Exit"
        ]
        
        choice = get_choice(options, "What would you like to do?")
        
        if choice == 1:
            add_daily_progress()
        elif choice == 2:
            view_daily_progress()
        elif choice == 3:
            modify_daily_progress()
        elif choice == 4:
            delete_daily_progress()
        elif choice == 5:
            add_new_mission()
        elif choice == 6:
            mark_mission_completed()
        elif choice == 7:
            mark_mission_failed()
        elif choice == 8:
            update_mission_progress()
        elif choice == 9:
            modify_mission()
        elif choice == 10:
            delete_mission()
        elif choice == 11:
            print_header("ALL MISSIONS")
            list_missions(MISSIONS_NOT_COMPLETED, "not-completed")
            list_missions(MISSIONS_COMPLETED, "completed")
        elif choice == 12:
            manage_rewards()
        elif choice == 13:
            print(f"\n{Colors.FAIL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
            print(f"{Colors.FAIL}  First rule of Fight Club:{Colors.ENDC}")
            print(f"{Colors.FAIL}    You do not talk about Fight Club.{Colors.ENDC}")
            print(f"{Colors.FAIL}  Second rule of Fight Club:{Colors.ENDC}")
            print(f"{Colors.FAIL}    You DO NOT talk about Fight Club.{Colors.ENDC}")
            print(f"{Colors.FAIL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")
            print_info("Stay strong! 💪")
            sys.exit(0)
        
        input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")
        input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)
