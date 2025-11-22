#!/usr/bin/env python3
"""
Quick script to add status and earned_by fields to all badges in config
"""
import json

badges_file = '../gamification/configs/badges.json'

with open(badges_file, 'r') as f:
    data = json.load(f)

# Add status and earned_by to each badge
for badge in data['badges']:
    if 'status' not in badge:
        badge['status'] = 'locked'
    if 'earned_by' not in badge:
        badge['earned_by'] = []

# Write back
with open(badges_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Updated {len(data['badges'])} badges with status and earned_by fields")
