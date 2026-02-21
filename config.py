"""
Tower Defense Game - Configuration File
All game balance values and settings in one place for easy tuning
"""

# Screen Settings
DESIGN_WIDTH = 1170  # iPhone 13 Pro width
DESIGN_HEIGHT = 2532  # iPhone 13 Pro height
DESKTOP_WIDTH = 1920  # For testing on PC
DESKTOP_HEIGHT = 1080  # For testing on PC

# Grid Settings
GRID_SIZE = 50  # Size of each grid cell in pixels
GRID_COLS = 30  # Number of columns
GRID_ROWS = 18  # Number of rows

# Game Settings
STARTING_HEALTH = 20
STARTING_CURRENCY = 650  # Increased from 500 - can now afford 6 cannons or mix of towers
BASE_ENEMY_REWARD = 25

# Tower Stats
TOWERS = {
    'cannon': {
        'name': 'Cannon',
        'cost': 100,
        'damage': 25,  # Increased from 20
        'fire_rate': 1.0,  # Shots per second
        'range': 150,
        'projectile_speed': 300,
        'color': (0.3, 0.3, 0.8, 1),  # Blue
        'upgrade_cost': 75,
        'upgrade_damage': 12,
        'upgrade_fire_rate': 0.2,
    },
    'machine_gun': {
        'name': 'Machine Gun',
        'cost': 120,  # Reduced from 150
        'damage': 10,  # Increased from 8
        'fire_rate': 4.0,
        'range': 120,  # Increased from 100
        'projectile_speed': 400,
        'color': (0.8, 0.3, 0.3, 1),  # Red
        'upgrade_cost': 100,
        'upgrade_damage': 5,
        'upgrade_fire_rate': 0.5,
    },
    'splash': {
        'name': 'Mortar',
        'cost': 180,  # Reduced from 200
        'damage': 35,  # Increased from 30
        'fire_rate': 0.6,  # Increased from 0.5
        'range': 180,
        'projectile_speed': 200,
        'splash_radius': 80,
        'color': (0.8, 0.5, 0.2, 1),  # Orange
        'upgrade_cost': 150,
        'upgrade_damage': 18,
        'upgrade_fire_rate': 0.1,
    },
    'freeze': {
        'name': 'Freeze Tower',
        'cost': 150,  # Reduced from 175
        'damage': 8,  # Increased from 5
        'fire_rate': 2.0,
        'range': 130,  # Increased from 120
        'projectile_speed': 350,
        'slow_duration': 2.5,  # Increased from 2.0
        'slow_amount': 0.6,  # Increased from 0.5 (60% slow)
        'color': (0.3, 0.8, 0.8, 1),  # Cyan
        'upgrade_cost': 125,
        'upgrade_damage': 4,
        'upgrade_fire_rate': 0.3,
    }
}

# Enemy Stats
ENEMIES = {
    'basic': {
        'name': 'Basic',
        'health': 100,
        'speed': 80,  # Pixels per second
        'reward': 25,
        'color': (0.8, 0.2, 0.2, 1),  # Red
    },
    'fast': {
        'name': 'Fast',
        'health': 60,
        'speed': 150,
        'reward': 30,
        'color': (0.9, 0.9, 0.2, 1),  # Yellow
    },
    'tank': {
        'name': 'Tank',
        'health': 300,
        'speed': 40,
        'reward': 50,
        'color': (0.4, 0.4, 0.4, 1),  # Gray
    },
    'regen': {
        'name': 'Regen',
        'health': 150,
        'speed': 70,
        'reward': 40,
        'regen_rate': 5,  # HP per second
        'color': (0.2, 0.8, 0.2, 1),  # Green
    },
    'boss': {
        'name': 'Boss',
        'health': 2000,
        'speed': 30,
        'reward': 500,
        'color': (0.6, 0.1, 0.6, 1),  # Purple
    }
}

# Wave Settings
WAVE_SPAWN_INTERVAL = 1.0  # Seconds between enemy spawns
WAVE_REST_TIME = 5.0  # Seconds between waves
BOSS_WAVE_INTERVAL = 20  # Boss every X waves

# Path Definition (normalized coordinates 0-1, will be scaled to grid)
# This creates a winding path from left to right across the widescreen
PATH_WAYPOINTS = [
    (0.05, 0.1),   # Start left side
    (0.3, 0.1),    # Move right
    (0.3, 0.5),    # Down
    (0.6, 0.5),    # Right
    (0.6, 0.8),    # Down
    (0.85, 0.8),   # Right
    (0.85, 0.4),   # Up
    (0.95, 0.4),   # End right side
]

# UI Colors
UI_BACKGROUND = (0.15, 0.15, 0.15, 1)
UI_TEXT = (1, 1, 1, 1)
GRID_LINE_COLOR = (0.3, 0.3, 0.3, 1)
PATH_COLOR = (0.4, 0.3, 0.2, 1)
SELECTED_TOWER_COLOR = (1, 1, 0, 0.3)
