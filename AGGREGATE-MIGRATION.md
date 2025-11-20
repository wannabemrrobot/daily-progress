# Aggregate JSON Migration Guide

## Overview
This document describes the migration from individual JSON files to an aggregate system for improved frontend performance.

## Problem Statement
The original architecture required loading 30+ individual JSON files (19 missions + 18 rewards), causing:
- Excessive HTTP requests
- UI lag and poor performance
- Slow page load times

## Solution
Implemented a dual-file system:
- **Individual files**: Source of truth for backend Python script operations
- **Aggregate files**: Performance layer for frontend consumption

## Architecture

### Aggregate Files Generated

#### Missions (4 files)
1. `missions/active.json` - In-progress missions sorted by due date
2. `missions/completed.json` - Completed missions sorted by completion date (desc)
3. `missions/failed.json` - Failed missions sorted by due date
4. `missions/not-started.json` - Not-started missions sorted by due date

#### Rewards (2 files)
1. `rewards/locked-aggregate.json` - All locked rewards
2. `rewards/unlocked-aggregate.json` - All unlocked rewards

### Aggregate File Structure

```json
{
  "count": 5,
  "generated_at": "2025-01-28T10:30:00.000000",
  "missions": [
    {
      "archetype": "knight",
      "mission_code": "K01",
      "title": "Mission Title",
      "description": "Mission description",
      "difficulty": "medium",
      "status": "in-progress",
      "progress": {
        "current": 3,
        "total": 10
      },
      "due_date": "2025-02-15",
      "start_date": "2025-01-20",
      "mission_icon": "path/to/icon.svg",
      "archetype_stat_change": {},
      "reward": []
    }
  ]
}
```

## Backend Changes (fight-club.py)

### New Functions
1. **`generate_missions_aggregates()`**: Reads all missions, categorizes by status, generates 4 aggregate files
2. **`generate_rewards_aggregates()`**: Reads all rewards, categorizes by lock status, generates 2 aggregate files
3. **`regenerate_all_aggregates()`**: Wrapper function to regenerate all aggregates

### Updated Functions (9 total)
All mission/reward modification operations now regenerate aggregates:
1. `create_reward()` - After creating new reward
2. `add_new_mission()` - After creating new mission
3. `mark_mission_completed()` - After marking completed
4. `mark_mission_failed()` - After marking failed
5. `delete_mission()` - After deleting mission
6. `modify_mission()` - After modifying mission (4 exit points)
7. `update_mission_progress()` - After updating progress
8. `modify_reward()` - After modifying reward (2 exit points)
9. `delete_reward()` - After deleting reward

### New Menu Option
Added "📦 Regenerate Aggregates" menu option (option 13) to manually regenerate all aggregates from individual files.

## Frontend Changes (missions.service.ts)

### New Constants
```typescript
private readonly MISSIONS_ACTIVE_AGGREGATE = `${this.MISSIONS_BASE_PATH}/active.json`;
private readonly MISSIONS_COMPLETED_AGGREGATE = `${this.MISSIONS_BASE_PATH}/completed.json`;
private readonly MISSIONS_FAILED_AGGREGATE = `${this.MISSIONS_BASE_PATH}/failed.json`;
private readonly MISSIONS_NOT_STARTED_AGGREGATE = `${this.MISSIONS_BASE_PATH}/not-started.json`;
private readonly REWARDS_LOCKED_AGGREGATE = `${this.REWARDS_BASE_PATH}/locked-aggregate.json`;
private readonly REWARDS_UNLOCKED_AGGREGATE = `${this.REWARDS_BASE_PATH}/unlocked-aggregate.json`;
```

### Updated Functions

#### `loadMissions(folder, limit)`
- Now loads from aggregate files instead of individual files
- Maps `not-completed` folder → active.json + not-started.json + failed.json
- Maps `completed` folder → completed.json
- Fallback to legacy individual file loading on error

#### `loadAllRewards(limit)`
- Now loads from locked-aggregate.json and unlocked-aggregate.json
- Fallback to legacy individual file loading on error

### New Private Functions
1. **`loadMissionsAggregate(aggregatePath)`**: Loads single aggregate file
2. **`loadRewardsAggregate(aggregatePath)`**: Loads rewards aggregate file
3. **`loadMissionsLegacy(folder, limit)`**: Fallback to individual file loading
4. **`loadAllRewardsLegacy(limit)`**: Fallback to individual reward file loading

## Data Integrity

### Consistency Guarantees
- Every mission/reward modification triggers aggregate regeneration
- Aggregates are always in sync with individual files
- Individual files remain the single source of truth

### Validation Points
1. **Creation**: New missions/rewards immediately reflected in aggregates
2. **Modification**: Status changes update appropriate aggregate files
3. **Deletion**: Removed items disappear from aggregates
4. **Progress Updates**: Mission progress changes trigger regeneration

## Testing Checklist

### Backend Testing
- [ ] Create new mission → verify in active.json
- [ ] Mark mission completed → verify moves to completed.json
- [ ] Mark mission failed → verify in failed.json
- [ ] Update mission progress → verify in active.json
- [ ] Modify mission → verify changes in appropriate aggregate
- [ ] Delete mission → verify removal from aggregates
- [ ] Create reward → verify in locked-aggregate.json
- [ ] Modify reward → verify changes in aggregate
- [ ] Delete reward → verify removal from aggregate
- [ ] Use menu option 13 → verify all aggregates regenerate

### Frontend Testing
- [ ] Dashboard loads missions from aggregates
- [ ] All mission statuses display correctly
- [ ] Mission counts match actual data
- [ ] Rewards display correctly
- [ ] Fallback works if aggregates missing
- [ ] No excessive HTTP requests (check browser network tab)
- [ ] Performance improvement visible (faster page load)

## Deployment Steps

1. **Generate Initial Aggregates**
   ```bash
   cd daily-progress/scripts
   python fight-club.py
   # Select option 13: "📦 Regenerate Aggregates"
   ```

2. **Commit Aggregate Files**
   ```bash
   git add gamification/missions/*.json
   git add gamification/rewards/*-aggregate.json
   git commit -m "Add aggregate JSON files for performance optimization"
   ```

3. **Deploy Frontend Changes**
   ```bash
   cd blog-frontend
   ng build --prod
   # Deploy to hosting
   ```

4. **Verify**
   - Check browser network tab (should see 6 aggregate requests instead of 37 individual requests)
   - Verify mission/reward data displays correctly
   - Test creating/modifying missions through Python script
   - Confirm aggregates update automatically

## Maintenance

### When Individual Files Are Modified Manually
If you manually edit individual mission/reward JSON files:
1. Run the Python script
2. Select option 13: "📦 Regenerate Aggregates"
3. Commit the updated aggregate files

### Monitoring
- Aggregates should always be in sync with individual files
- If UI shows stale data, regenerate aggregates
- Check `generated_at` timestamp in aggregate files to verify freshness

## Rollback Plan

If issues arise:
1. Frontend automatically falls back to individual file loading on error
2. Remove aggregate file paths from frontend if needed
3. Individual files remain unchanged and functional

## Performance Improvements

### Before Migration
- 37 HTTP requests (19 missions + 18 rewards)
- ~2-3 seconds load time
- Multiple sequential file loads

### After Migration
- 6 HTTP requests (4 mission aggregates + 2 reward aggregates)
- ~500ms load time (estimated 80% reduction)
- Single parallel load per category

## File Locations

### Backend
- Script: `daily-progress/scripts/fight-club.py`
- Individual missions: `daily-progress/gamification/missions/not-completed/` and `missions/completed/`
- Individual rewards: `daily-progress/gamification/rewards/locked/` and `rewards/unlocked/`
- Aggregate missions: `daily-progress/gamification/missions/*.json` (4 files)
- Aggregate rewards: `daily-progress/gamification/rewards/*-aggregate.json` (2 files)

### Frontend
- Service: `blog-frontend/src/app/service/missions.service.ts`
- Component: `blog-frontend/src/app/components/fightclub/fightclub.component.ts`

## Notes

- Aggregates are automatically regenerated by Python script on any mission/reward operation
- Frontend has fallback to individual files if aggregates are missing
- Individual files remain the source of truth - never modify aggregates directly
- Use menu option 13 for manual regeneration if needed
- Aggregates include metadata (count, generated_at timestamp)
