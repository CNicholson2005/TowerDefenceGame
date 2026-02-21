# 🚀 Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Python
If you don't have Python installed:
- **Windows/Mac**: Download from [python.org](https://www.python.org/downloads/)
- **Check installation**: Open terminal and type `python --version`

### 2. Install Kivy
Open your terminal/command prompt and run:
```bash
pip install kivy
```

### 3. Run the Game
```bash
cd tower_defense
python main.py
```

That's it! The game should launch in a window.

## 🎮 First Steps

1. Click **"Start Wave"** button at the bottom
2. Click on any empty grid cell to place a **Cannon** tower ($100)
3. Watch your tower shoot enemies as they move along the brown path
4. Click tower type buttons to select different towers
5. Click on placed towers to upgrade them

## 🐛 Troubleshooting

### "kivy" not found
```bash
# Try with pip3 instead
pip3 install kivy

# Or use python -m pip
python -m pip install kivy
```

### Game window is too small/large
Edit `config.py` and adjust:
```python
DESKTOP_WIDTH = 800   # Change this
DESKTOP_HEIGHT = 1200 # Change this
```

### Performance issues
Try reducing FPS in `main.py`:
```python
Clock.schedule_interval(self.update, 1/30.0)  # 30 FPS instead of 60
```

## 📖 Next Steps

1. **Play a few waves** to understand the mechanics
2. **Experiment with different tower combinations**
3. **Try to beat wave 20** to see your first boss!
4. **Read the full README.md** for detailed info
5. **Modify config.py** to balance the game your way

## 💡 Tips for Your First Game

- Place towers at corners where enemies move slowly
- Mix tower types - don't just spam one type
- Upgrade your best-positioned towers first
- Save some money for emergencies
- Fast enemies are worth more money per hit point

## 🎯 Development Roadmap

**This Week**: Core mechanics done ✅
**Week 2-3**: Add more content (towers, enemies, maps)
**Week 4**: Polish and visual improvements
**Week 5-6**: iOS deployment

## 📝 Making Changes

Want to modify the game? Start here:

### Change Tower Stats
Edit `config.py` → `TOWERS` dictionary

### Change Enemy Stats  
Edit `config.py` → `ENEMIES` dictionary

### Change the Path
Edit `config.py` → `PATH_WAYPOINTS` list

### Add New Features
- New tower type: Add to `config.py`, implement special behavior in `tower.py`
- New enemy type: Add to `config.py`, implement special behavior in `enemy.py`

## 🆘 Need Help?

Check the main README.md for:
- Detailed feature documentation
- Code architecture explanation
- How to add new content
- iOS deployment instructions (coming soon)

Have fun! 🎮
