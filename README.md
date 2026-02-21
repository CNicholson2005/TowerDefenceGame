# Tower Defense Game

A mobile tower defense game built with Python and Kivy, designed for iPhone 13 Pro but works on desktop for development. This game is still in development as I have many more features to add and improve on exisiting features.

## 🎮 Features

### Current Implementation (Week 1)
- ✅ Core game loop with 60 FPS
- ✅ Grid-based tower placement system
- ✅ Enemy pathfinding along predefined routes
- ✅ 4 Tower types: Cannon, Machine Gun, Mortar (splash), Freeze
- ✅ 5 Enemy types: Basic, Fast, Tank, Regen, Boss
- ✅ Wave system with increasing difficulty
- ✅ Boss waves every 20 waves
- ✅ Currency and health system
- ✅ Tower upgrade system (up to level 3)
- ✅ Projectile physics
- ✅ Splash damage for mortars
- ✅ Slow/freeze effects
- ✅ Health regeneration for regen enemies

### Planned Features (Coming Weeks)
- 🔲 Pixel art graphics
- 🔲 Sound effects and music
- 🔲 Additional tower types
- 🔲 More enemy varieties
- 🔲 Multiple maps
- 🔲 Save/load system
- 🔲 Achievements
- 🔲 iOS deployment

## 📋 Requirements

- Python 3.8+
- Kivy 2.3.0+

## 🚀 Installation

### Desktop (For Development)

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/)

2. **Install Kivy**
   ```bash
   pip install kivy
   ```

3. **Run the game**
   ```bash
   cd tower_defense
   python main.py
   ```

### iOS Deployment (Future)

Will use `kivy-ios` toolchain:
```bash
# Install kivy-ios
pip install kivy-ios

# Create Xcode project
toolchain create TowerDefense /path/to/tower_defense

# Build and deploy to iPhone
```

## 🎯 How to Play

1. **Start a Wave**: Click "Start Wave" button
2. **Place Towers**: Click on any grid cell (not on the path) to place your selected tower
3. **Upgrade Towers**: Click on an existing tower to select it, then click upgrade button
4. **Defend**: Stop enemies from reaching the end of the path
5. **Earn Currency**: Kill enemies and complete waves to earn money for more towers

### Tower Types

| Tower | Cost | Damage | Fire Rate | Range | Special |
|-------|------|--------|-----------|-------|---------|
| **Cannon** | $100 | 20 | 1.0/s | 150 | Balanced all-rounder |
| **Machine Gun** | $150 | 8 | 4.0/s | 100 | Fast firing, good for swarms |
| **Mortar** | $200 | 30 | 0.5/s | 180 | Splash damage in 80px radius |
| **Freeze** | $175 | 5 | 2.0/s | 120 | Slows enemies by 50% for 2s |

### Enemy Types

| Enemy | Health | Speed | Reward | Special |
|-------|--------|-------|--------|---------|
| **Basic** | 100 | 80 | $25 | Standard enemy |
| **Fast** | 60 | 150 | $30 | Quick but fragile |
| **Tank** | 300 | 40 | $50 | Slow but very tanky |
| **Regen** | 150 | 70 | $40 | Regenerates 5 HP/s |
| **Boss** | 2000 | 30 | $500 | Appears every 20 waves |

### Tips

- **Mix tower types**: Use machine guns for fast enemies, cannons for general purpose, mortars for groups
- **Upgrade strategically**: A level 3 tower is often better than 3 level 1 towers
- **Use freeze towers**: Slow down fast enemies and bosses
- **Plan ahead**: Place towers early in the path to maximize damage time

## 📁 Project Structure

```
tower_defense/
├── main.py          # Main game loop and UI
├── config.py        # All game balance and settings
├── enemy.py         # Enemy class and behavior
├── tower.py         # Tower class and targeting
├── projectile.py    # Projectile physics
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## ⚙️ Configuration

All game balance values are in `config.py`. You can easily adjust:
- Tower stats (damage, fire rate, cost, range)
- Enemy stats (health, speed, rewards)
- Wave difficulty scaling
- Grid size and layout
- Path waypoints
- UI colors

## 🛠️ Development

### Code Architecture

The game follows clean OOP principles:

1. **Separation of Concerns**: Each class handles one responsibility
   - `Enemy`: Movement, health, status effects
   - `Tower`: Targeting, shooting, upgrades
   - `Projectile`: Movement, collision
   - `TowerDefenseGame`: Game state, coordination

2. **Configuration-Driven**: All balance values in one file for easy tuning

3. **Extensible Design**: Easy to add new tower/enemy types:
   ```python
   # In config.py
   TOWERS['laser'] = {
       'name': 'Laser',
       'cost': 250,
       'damage': 15,
       # ... more stats
   }
   ```

### Adding New Features

**Add a new tower type:**
1. Add stats to `TOWERS` dict in `config.py`
2. Add special behavior in `Tower.update()` if needed
3. That's it! The rest is automatic

**Add a new enemy type:**
1. Add stats to `ENEMIES` dict in `config.py`
2. Add special behavior in `Enemy.update()` if needed
3. Update wave generation in `generate_wave_enemies()`

## 📱 Mobile Optimization

The game is designed to scale between desktop and mobile:
- Responsive grid system
- Touch-friendly UI buttons
- Configurable resolution (desktop vs iPhone)
- Performance optimized (60 FPS target)

## 🎓 Portfolio Highlights

This project demonstrates:
- ✅ **Object-Oriented Design**: Clean class hierarchy
- ✅ **Game Development**: Physics, AI, game loop
- ✅ **Mobile Development**: Kivy framework for iOS
- ✅ **Python Best Practices**: Type hints, documentation, modularity
- ✅ **Project Management**: Iterative development, version control ready
- ✅ **Problem Solving**: Pathfinding, collision detection, targeting algorithms

## 📝 License

This project is open source and available for portfolio use.

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome!

## 📧 Contact

Created for placement portfolio - Conor Nicholson
