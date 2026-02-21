# 🏗️ Code Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        MAIN.PY                              │
│                  TowerDefenseGame Class                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Game State:                                        │    │
│  │  - health, currency, wave                          │    │
│  │  - enemies[], towers[], projectiles[]              │    │
│  │                                                     │    │
│  │  Game Loop (60 FPS):                               │    │
│  │  1. Spawn enemies                                  │    │
│  │  2. Update all enemies                             │    │
│  │  3. Update all towers (find targets, shoot)        │    │
│  │  4. Update all projectiles (move, hit)             │    │
│  │  5. Handle collisions & damage                     │    │
│  │  6. Update UI                                      │    │
│  │  7. Draw everything                                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses
                            ▼
    ┌──────────────┬────────────────┬──────────────┬──────────────┐
    │              │                │              │              │
    ▼              ▼                ▼              ▼              ▼
┌─────────┐  ┌─────────┐      ┌─────────┐   ┌──────────┐   ┌─────────┐
│ Enemy   │  │ Tower   │      │Project. │   │ Config   │   │ Kivy    │
│ Class   │  │ Class   │      │ Class   │   │ Module   │   │Framework│
├─────────┤  ├─────────┤      ├─────────┤   ├──────────┤   ├─────────┤
│- pos    │  │- pos    │      │- pos    │   │ TOWERS   │   │Graphics │
│- health │  │- damage │      │- target │   │ ENEMIES  │   │Clock    │
│- speed  │  │- range  │      │- speed  │   │ GRID     │   │Events   │
│- path   │  │- target │      │- damage │   │ PATH     │   │Window   │
│         │  │         │      │         │   │ WAVES    │   │         │
│update() │  │update() │      │update() │   │          │   │         │
│move()   │  │shoot()  │      │hit()    │   │          │   │         │
│damage() │  │upgrade()│      │         │   │          │   │         │
└─────────┘  └─────────┘      └─────────┘   └──────────┘   └─────────┘
```

## Class Relationships

### Enemy Class (`enemy.py`)
**Purpose**: Represents an enemy moving along the path

**Key Methods**:
- `__init__()`: Create enemy with stats from config
- `update(dt)`: Move along path, handle effects
- `take_damage(amount)`: Apply damage, check if dead
- `apply_slow(duration, amount)`: Slow effect from freeze towers

**State**:
- Position (x, y)
- Health (current, max)
- Path progress (path_index)
- Status effects (slow_timer, slow_amount)

### Tower Class (`tower.py`)
**Purpose**: Represents a tower that shoots enemies

**Key Methods**:
- `__init__()`: Create tower with stats from config
- `update(dt, enemies)`: Find target, shoot if ready
- `find_target(enemies)`: Select best enemy in range
- `shoot()`: Create projectile toward target
- `upgrade()`: Increase damage and fire rate

**State**:
- Position (grid coordinates)
- Combat stats (damage, range, fire_rate)
- Upgrade level
- Current target
- Fire cooldown timer

### Projectile Class (`projectile.py`)
**Purpose**: Represents a shot fired by a tower

**Key Methods**:
- `__init__()`: Create projectile with target
- `update(dt)`: Move toward target, check collision

**State**:
- Position (x, y)
- Target enemy
- Damage amount
- Speed

## Data Flow

### 1. Enemy Spawn
```
Wave System → Generate Enemy List → Spawn Timer → Create Enemy Object → Add to enemies[]
```

### 2. Tower Shooting
```
Tower.update() → find_target() → Check range → shoot() → Create Projectile → Add to projectiles[]
```

### 3. Damage Application
```
Projectile hits → Check collision → Apply damage → Enemy.take_damage() → 
  → If dead: Remove + Give currency
  → Else: Update health
```

### 4. Wave Progression
```
Start Wave → Spawn All Enemies → All Enemies Dead/Escaped → 
  → Give Bonus → Wave Complete → Player Starts Next Wave
```

## File Organization

```
tower_defense/
│
├── main.py              # 🎮 Game loop, UI, coordination (400 lines)
│   └── TowerDefenseGame class
│       ├── Game state management
│       ├── Wave system
│       ├── UI setup
│       ├── Event handling (clicks, hover)
│       └── Rendering
│
├── tower.py             # 🗼 Tower logic (150 lines)
│   └── Tower class
│       ├── Targeting algorithm
│       ├── Shooting mechanics
│       └── Upgrade system
│
├── enemy.py             # 👾 Enemy logic (120 lines)
│   └── Enemy class
│       ├── Path following
│       ├── Status effects
│       └── Health management
│
├── projectile.py        # 💥 Projectile logic (50 lines)
│   └── Projectile class
│       ├── Movement
│       └── Collision detection
│
└── config.py            # ⚙️ All game balance (150 lines)
    ├── TOWERS dict
    ├── ENEMIES dict
    ├── PATH_WAYPOINTS
    └── Game constants
```

## Key Design Patterns

### 1. **Composition Over Inheritance**
- Game has lists of enemies, towers, projectiles
- Each class is independent and composable

### 2. **Configuration-Driven Design**
- All balance values in `config.py`
- Easy to add new tower/enemy types without code changes
- Just add dictionary entry!

### 3. **Game Loop Pattern**
```python
def update(dt):
    # 1. Input
    handle_user_input()
    
    # 2. Update
    update_game_objects(dt)
    
    # 3. Render
    draw_everything()
```

### 4. **Object Pooling** (Can be added)
- Currently creates/destroys objects
- Could pool projectiles for performance

## Performance Considerations

### Current Performance
- 60 FPS target
- Handles ~50 enemies + 20 towers + 50 projectiles smoothly

### Optimization Opportunities
1. **Spatial partitioning**: Grid-based enemy lookup for tower targeting
2. **Object pooling**: Reuse projectile objects
3. **Dirty rectangles**: Only redraw changed areas
4. **LOD**: Simplify distant objects

## Extending the Game

### Adding a New Tower Type

1. **Add to config.py**:
```python
TOWERS['laser'] = {
    'name': 'Laser',
    'cost': 300,
    'damage': 15,
    'fire_rate': 10.0,  # Continuous beam
    'range': 200,
    # Special properties
    'beam_type': True,
}
```

2. **Add special behavior in tower.py** (if needed):
```python
def update(self, dt, enemies):
    if self.stats.get('beam_type'):
        # Continuous damage to target
        if self.target and self.target.alive:
            self.target.take_damage(self.damage * dt)
    else:
        # Normal projectile shooting
        # ... existing code
```

### Adding a New Enemy Type

1. **Add to config.py**:
```python
ENEMIES['flying'] = {
    'name': 'Flying',
    'health': 80,
    'speed': 100,
    'reward': 35,
    'flying': True,  # Special property
}
```

2. **Add special behavior in enemy.py** (if needed):
```python
def update(self, dt):
    if self.stats.get('flying'):
        # Use different path or fly directly
        self.fly_to_end(dt)
    else:
        # Normal path following
        # ... existing code
```

## Testing Strategy

### Manual Testing Checklist
- [ ] Towers place correctly on grid
- [ ] Can't place on path
- [ ] Towers shoot enemies in range
- [ ] Projectiles hit targets
- [ ] Damage applies correctly
- [ ] Currency increases on kill
- [ ] Health decreases when enemies escape
- [ ] Waves increase in difficulty
- [ ] Boss spawns every 20 waves
- [ ] Upgrades work correctly

### Future: Unit Tests
```python
def test_tower_targeting():
    # Create tower and enemies
    # Verify correct target selection
    
def test_projectile_collision():
    # Create projectile and enemy
    # Verify collision detection
```

## Next Development Steps

**Week 2**:
- Add remaining tower types
- Add more enemy varieties
- Improve visual feedback

**Week 3**:
- Add pixel art assets
- Sound effects
- Multiple maps

**Week 4**:
- Polish UI/UX
- Add animations
- Main menu

**Week 5-6**:
- iOS packaging
- Performance optimization
- App store preparation

---

This architecture is designed to be:
✅ **Easy to understand** - Clear separation of concerns
✅ **Easy to extend** - Just add config entries
✅ **Easy to maintain** - Well-commented, modular code
✅ **Portfolio-ready** - Demonstrates software engineering principles
