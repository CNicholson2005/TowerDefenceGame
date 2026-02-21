"""
Main Game Logic - Handles game state, waves, and coordination
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import math

from config import *
from enemy import Enemy
from tower import Tower
from projectile import Projectile
from particles import Particle, MuzzleFlash, create_explosion, create_hit_effect


class GameCanvas(Widget):
    """Widget that handles the game rendering"""
    def on_touch_down(self, touch):
        # Don't consume any touches - let them pass through to game logic
        return False
    
    def on_touch_move(self, touch):
        return False
    
    def on_touch_up(self, touch):
        return False


class TowerDefenseGame(FloatLayout):
    """Main game widget that handles all game logic"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Game state
        self.health = STARTING_HEALTH
        self.currency = STARTING_CURRENCY
        self.wave = 0
        self.game_over = False
        self.paused = False
        
        # Game objects
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.particles = []  # For visual effects
        
        # Game speed
        self.game_speed = 1.0  # 1x, 2x, or 3x
        
        # Visual effects
        self.muzzle_flashes = []  # Tower shooting effects
        
        # Wave management
        self.wave_timer = 0
        self.spawn_timer = 0
        self.enemies_to_spawn = []
        self.wave_active = False
        
        # UI state
        self.selected_tower_type = 'cannon'
        self.selected_tower = None
        self.hovered_cell = None
        
        # Calculate grid offset to center it
        self.grid_pixel_width = GRID_COLS * GRID_SIZE
        self.grid_pixel_height = GRID_ROWS * GRID_SIZE
        
        # Path setup
        self.path_points = self.calculate_path()
        self.path_cells = self.get_path_cells()
        
        # Start game loop
        Clock.schedule_interval(self.update, 1/60.0)
        
        # Setup UI
        self.setup_ui()
        
        # Bind mouse/touch events
        Window.bind(mouse_pos=self.on_mouse_move)
        
        # Bind keyboard for fullscreen toggle
        Window.bind(on_key_down=self.on_key_down)
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard shortcuts"""
        # F11 or F to toggle fullscreen
        if key == 292 or (key == 102 and 'ctrl' in modifier):  # F11 or Ctrl+F
            Window.fullscreen = 'auto' if not Window.fullscreen else False
            print(f"[DEBUG] Fullscreen toggled: {Window.fullscreen}")
        # ESC to exit fullscreen
        elif key == 27 and Window.fullscreen:  # ESC
            Window.fullscreen = False
        # Space to start wave (convenience)
        elif key == 32 and not self.wave_active:  # Space
            self.start_wave()
    
    def calculate_path(self):
        """Convert normalized path waypoints to pixel coordinates"""
        path = []
        for norm_x, norm_y in PATH_WAYPOINTS:
            x = norm_x * self.grid_pixel_width
            y = norm_y * self.grid_pixel_height
            path.append((x, y))
        return path
    
    def get_path_cells(self):
        """Get all grid cells that the path passes through"""
        cells = set()
        
        # Add cells for each segment of the path
        for i in range(len(self.path_points) - 1):
            x1, y1 = self.path_points[i]
            x2, y2 = self.path_points[i + 1]
            
            # Add cells along the line
            steps = int(max(abs(x2 - x1), abs(y2 - y1)) / (GRID_SIZE / 2))
            for step in range(steps + 1):
                t = step / max(steps, 1)
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                
                grid_x = int(x / GRID_SIZE)
                grid_y = int(y / GRID_SIZE)
                
                if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                    cells.add((grid_x, grid_y))
        
        return cells
    
    def setup_ui(self):
        """Setup UI elements - simple side panel, no collapsing"""
        # Game canvas for drawing
        self.game_canvas = GameCanvas()
        self.add_widget(self.game_canvas)
        
        # Top info bar (use padding to avoid side panel)
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=50,
            pos_hint={'top': 1},
            padding=[10, 10, 320, 10],  # Large right padding to avoid side panel
            spacing=0
        )
        
        # Wave info (LEFT)
        self.wave_label = Label(
            text=f"WAVE: {self.wave}",
            size_hint=(0.33, 1),
            color=(0.5, 0.8, 1, 1),
            font_size='16sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        self.wave_label.bind(size=self.wave_label.setter('text_size'))
        top_bar.add_widget(self.wave_label)
        
        # Health info (CENTER)
        self.health_label = Label(
            text=f"LIVES: {self.health}",
            size_hint=(0.33, 1),
            color=(1, 0.3, 0.3, 1),
            font_size='16sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.health_label.bind(size=self.health_label.setter('text_size'))
        top_bar.add_widget(self.health_label)
        
        # Currency info (RIGHT)
        self.currency_label = Label(
            text=f"GOLD: ${self.currency}",
            size_hint=(0.34, 1),
            color=(1, 0.84, 0, 1),
            font_size='16sp',
            bold=True,
            halign='right',
            valign='middle'
        )
        self.currency_label.bind(size=self.currency_label.setter('text_size'))
        top_bar.add_widget(self.currency_label)
        
        self.add_widget(top_bar)
        
        # Simple right side panel - everything visible, no collapsing
        self.side_panel = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=300,
            pos_hint={'right': 1, 'top': 1},
            padding=[10, 60, 10, 10],  # Extra top padding to avoid top bar
            spacing=8
        )
        
        # Add background
        from kivy.graphics import Color, Rectangle
        with self.side_panel.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.side_panel_bg = Rectangle(pos=self.side_panel.pos, size=self.side_panel.size)
        
        def update_bg(instance, value):
            self.side_panel_bg.pos = instance.pos
            self.side_panel_bg.size = instance.size
        
        self.side_panel.bind(pos=update_bg, size=update_bg)
        
        # Game speed section
        speed_label = Label(
            text="GAME SPEED",
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        self.side_panel.add_widget(speed_label)
        
        speed_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=5)
        
        self.speed_1x_btn = Button(text="1x", background_color=(0.3, 0.8, 0.3, 1), font_size='14sp', bold=True)
        self.speed_1x_btn.bind(on_press=lambda x: self.set_game_speed(1.0))
        speed_box.add_widget(self.speed_1x_btn)
        
        self.speed_2x_btn = Button(text="2x", background_color=(0.5, 0.5, 0.5, 1), font_size='14sp', bold=True)
        self.speed_2x_btn.bind(on_press=lambda x: self.set_game_speed(2.0))
        speed_box.add_widget(self.speed_2x_btn)
        
        self.speed_3x_btn = Button(text="3x", background_color=(0.5, 0.5, 0.5, 1), font_size='14sp', bold=True)
        self.speed_3x_btn.bind(on_press=lambda x: self.set_game_speed(3.0))
        speed_box.add_widget(self.speed_3x_btn)
        
        self.side_panel.add_widget(speed_box)
        
        # Spacer to push towers down a bit
        self.side_panel.add_widget(Widget(size_hint=(1, 0.3)))
        
        # Divider
        self.side_panel.add_widget(Label(text="____________", size_hint=(1, None), height=20, color=(0.5, 0.5, 0.5, 1)))
        
        # Tower selection section
        tower_label = Label(
            text="SELECT TOWER",
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        self.side_panel.add_widget(tower_label)
        
        # Selected tower info
        self.tower_info_label = Label(
            text=f"Selected: {TOWERS[self.selected_tower_type]['name']}",
            size_hint=(1, None),
            height=25,
            color=(0.8, 0.8, 0.8, 1),
            font_size='12sp'
        )
        self.side_panel.add_widget(self.tower_info_label)
        
        # Tower buttons - all visible
        self.tower_type_buttons = {}
        
        for tower_type, stats in TOWERS.items():
            btn = Button(
                text=f"{stats['name']} - ${stats['cost']}",
                size_hint=(1, None),
                height=50,
                background_color=stats['color'],
                font_size='13sp',
                bold=True
            )
            btn.tower_type = tower_type
            btn.bind(on_press=self.on_tower_button_press)
            self.side_panel.add_widget(btn)
            self.tower_type_buttons[tower_type] = btn
        
        # Spacer to push tower actions to bottom half
        self.side_panel.add_widget(Widget(size_hint=(1, 0.5)))
        
        # Divider
        self.side_panel.add_widget(Label(text="____________", size_hint=(1, None), height=20, color=(0.5, 0.5, 0.5, 1)))
        
        # Selected tower actions
        actions_label = Label(
            text="TOWER ACTIONS",
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        self.side_panel.add_widget(actions_label)
        
        self.selected_info_label = Label(
            text="Click a tower to select",
            size_hint=(1, None),
            height=25,
            color=(0.7, 0.7, 0.7, 1),
            font_size='12sp'
        )
        self.side_panel.add_widget(self.selected_info_label)
        
        self.sell_btn = Button(
            text="SELL TOWER",
            size_hint=(1, None),
            height=45,
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            font_size='14sp',
            bold=True
        )
        self.sell_btn.bind(on_press=self.on_sell_press)
        self.side_panel.add_widget(self.sell_btn)
        
        self.upgrade_btn = Button(
            text="UPGRADE",
            size_hint=(1, None),
            height=45,
            background_color=(0.8, 0.6, 0.2, 1),
            disabled=True,
            font_size='14sp',
            bold=True
        )
        self.upgrade_btn.bind(on_press=self.on_upgrade_press)
        self.side_panel.add_widget(self.upgrade_btn)
        
        # Spacer to push start wave to bottom
        self.side_panel.add_widget(Widget(size_hint=(1, 0.3)))
        
        # Divider
        self.side_panel.add_widget(Label(text="____________", size_hint=(1, None), height=20, color=(0.5, 0.5, 0.5, 1)))
        
        # Start wave button
        self.start_wave_btn = Button(
            text="START WAVE 1",
            size_hint=(1, None),
            height=60,
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='16sp',
            bold=True
        )
        self.start_wave_btn.bind(on_press=self.on_start_wave_press)
        self.side_panel.add_widget(self.start_wave_btn)
        
        self.add_widget(self.side_panel)
    
    def on_tower_button_press(self, button):
        """Handle tower type button press"""
        tower_type = button.tower_type
        self.select_tower_type(tower_type)
    
    def on_start_wave_press(self, button):
        """Handle start wave button press"""
        self.start_wave()
    
    def on_sell_press(self, button):
        """Handle sell button press"""
        self.sell_tower()
    
    def on_upgrade_press(self, button):
        """Handle upgrade button press"""
        self.upgrade_tower()
    
    def set_game_speed(self, speed):
        """Change game speed"""
        self.game_speed = speed
        
        # Update button colors to show active speed
        self.speed_1x_btn.background_color = (0.3, 0.8, 0.3, 1) if speed == 1.0 else (0.5, 0.5, 0.5, 1)
        self.speed_2x_btn.background_color = (0.3, 0.8, 0.3, 1) if speed == 2.0 else (0.5, 0.5, 0.5, 1)
        self.speed_3x_btn.background_color = (0.3, 0.8, 0.3, 1) if speed == 3.0 else (0.5, 0.5, 0.5, 1)
        
        print(f"[DEBUG] Game speed set to {speed}x")
    
    def get_tower_info_text(self):
        """Get info text for selected tower type"""
        stats = TOWERS[self.selected_tower_type]
        return f"Damage: {stats['damage']} | Range: {stats['range']} | Fire Rate: {stats['fire_rate']}/s"
    
    def select_tower_type(self, tower_type):
        """Select which tower type to place"""
        print(f"[DEBUG] Selected tower type: {tower_type}")
        self.selected_tower_type = tower_type
        self.selected_tower = None
        self.tower_info_label.text = f"Selected: {TOWERS[tower_type]['name']}"
        self.sell_btn.disabled = True
        self.upgrade_btn.disabled = True
    
    def sell_tower(self):
        """Sell the selected tower"""
        if self.selected_tower:
            # Refund 70% of total cost
            refund = int(self.selected_tower.get_total_cost() * 0.7)
            self.currency += refund
            self.towers.remove(self.selected_tower)
            self.selected_tower = None
            self.sell_btn.disabled = True
            self.upgrade_btn.disabled = True
            print(f"[DEBUG] Tower sold for ${refund}")
    
    def upgrade_tower(self):
        """Upgrade the selected tower"""
        if self.selected_tower:
            cost = self.selected_tower.get_upgrade_cost()
            if cost > 0 and self.currency >= cost:
                self.currency -= self.selected_tower.upgrade()
                self.update_tower_buttons()
    
    def update_tower_buttons(self):
        """Update button states based on selected tower"""
        if self.selected_tower:
            # Update info label
            tower_name = TOWERS[self.selected_tower.type]['name']
            self.selected_info_label.text = f"{tower_name} (Level {self.selected_tower.level})"
            
            # Calculate sell value
            refund = int(self.selected_tower.get_total_cost() * 0.7)
            self.sell_btn.disabled = False
            self.sell_btn.text = f"SELL (${refund})"
            
            upgrade_cost = self.selected_tower.get_upgrade_cost()
            if upgrade_cost > 0:
                self.upgrade_btn.disabled = False
                self.upgrade_btn.text = f"UPGRADE (${upgrade_cost})"
            else:
                self.upgrade_btn.disabled = True
                self.upgrade_btn.text = "MAX LEVEL"
        else:
            self.selected_info_label.text = "Click a tower to view info"
            self.sell_btn.disabled = True
            self.sell_btn.text = "SELL TOWER"
            self.upgrade_btn.disabled = True
            self.upgrade_btn.text = "UPGRADE"
    
    def start_wave(self):
        """Start the next wave"""
        print(f"[DEBUG] Start wave called. Active: {self.wave_active}, Game Over: {self.game_over}")
        if self.wave_active or self.game_over:
            return
        
        self.wave += 1
        self.wave_active = True
        self.spawn_timer = 0
        
        print(f"[DEBUG] Starting wave {self.wave}")
        
        # Update button
        self.start_wave_btn.text = f"WAVE {self.wave} ACTIVE"
        self.start_wave_btn.disabled = True
        
        # Generate enemies for this wave
        self.enemies_to_spawn = self.generate_wave_enemies()
        print(f"[DEBUG] Generated {len(self.enemies_to_spawn)} enemies for wave")
    
    def generate_wave_enemies(self):
        """Generate list of enemies for current wave"""
        enemies = []
        
        # Boss wave every BOSS_WAVE_INTERVAL waves
        if self.wave % BOSS_WAVE_INTERVAL == 0:
            enemies.append('boss')
            return enemies
        
        # Regular waves - more gradual difficulty scaling
        # Start with fewer enemies, scale slower
        if self.wave == 1:
            base_count = 3  # Very easy first wave
        elif self.wave <= 3:
            base_count = 4 + self.wave  # Waves 2-3: 6-7 enemies
        elif self.wave <= 5:
            base_count = 6 + self.wave  # Waves 4-5: 10-11 enemies
        else:
            base_count = 8 + (self.wave - 5) * 2  # After wave 5: +2 per wave
        
        print(f"[DEBUG] Wave {self.wave}: Spawning {base_count} enemies")
        
        # Mix of enemy types based on wave
        for i in range(base_count):
            if self.wave <= 2:
                # Only basic enemies in first 2 waves
                enemies.append('basic')
            elif self.wave <= 5:
                # Introduce fast enemies
                enemies.append('basic' if i % 2 == 0 else 'fast')
            elif self.wave <= 10:
                # Add tank enemies
                enemy_type = ['basic', 'basic', 'fast', 'tank'][i % 4]
                enemies.append(enemy_type)
            elif self.wave <= 15:
                # Add regen enemies
                enemy_type = ['basic', 'fast', 'tank', 'regen'][i % 4]
                enemies.append(enemy_type)
            else:
                # Full variety
                enemy_type = ['basic', 'fast', 'fast', 'tank', 'regen'][i % 5]
                enemies.append(enemy_type)
        
        return enemies
    
    def update(self, dt):
        """Main game loop"""
        if self.game_over or self.paused:
            return
        
        # Apply game speed multiplier
        dt = dt * self.game_speed
        
        # Update UI labels
        self.wave_label.text = f"WAVE: {self.wave}"
        self.health_label.text = f"LIVES: {self.health}"
        self.currency_label.text = f"GOLD: ${self.currency}"
        
        # Spawn enemies
        if self.wave_active and self.enemies_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= WAVE_SPAWN_INTERVAL:
                enemy_type = self.enemies_to_spawn.pop(0)
                enemy = Enemy(enemy_type, self.path_points, self.wave)
                self.enemies.append(enemy)
                self.spawn_timer = 0
                print(f"[DEBUG] Spawned {enemy_type} at ({enemy.x}, {enemy.y}), path has {len(self.path_points)} points")
        
        # Check if wave is complete
        if self.wave_active and not self.enemies_to_spawn and not self.enemies:
            self.wave_active = False
            # Bonus: 50 base + 10 per wave completed
            wave_bonus = 50 + (self.wave * 10)
            self.currency += wave_bonus
            self.start_wave_btn.disabled = False
            self.start_wave_btn.text = f"START WAVE {self.wave + 1} (+${wave_bonus})"
            print(f"[DEBUG] Wave {self.wave} complete! Bonus: ${wave_bonus}")
        
        # Update enemies
        for enemy in self.enemies[:]:
            old_x, old_y = enemy.x, enemy.y
            enemy.update(dt)
            
            # Debug first enemy position
            if self.enemies and enemy == self.enemies[0] and self.wave == 1:
                if old_x != enemy.x or old_y != enemy.y:
                    print(f"[DEBUG] Enemy moved from ({old_x:.1f}, {old_y:.1f}) to ({enemy.x:.1f}, {enemy.y:.1f}), speed={enemy.current_speed}, path_index={enemy.path_index}")
            
            if enemy.reached_end:
                self.health -= 1
                self.enemies.remove(enemy)
                if self.health <= 0:
                    self.game_over = True
            elif not enemy.alive:
                # Create death explosion
                explosion_particles = create_explosion(enemy.x, enemy.y, enemy.stats['color'], num_particles=20)
                self.particles.extend(explosion_particles)
                
                self.currency += enemy.get_reward()
                self.enemies.remove(enemy)
        
        # Update towers and collect new projectiles
        for tower in self.towers:
            projectile = tower.update(dt, self.enemies)
            if projectile:
                self.projectiles.append(projectile)
                # Add muzzle flash effect
                flash = MuzzleFlash(tower.x, tower.y, tower.stats['color'])
                self.muzzle_flashes.append(flash)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            hit = projectile.update(dt)
            if hit:
                # Projectile hit target or target died
                if projectile.target.alive:
                    # Create hit effect
                    hit_particles = create_hit_effect(projectile.x, projectile.y, num_particles=8)
                    self.particles.extend(hit_particles)
                    
                    print(f"[DEBUG] Projectile hit! Damage: {projectile.damage}, Enemy health before: {projectile.target.health:.1f}")
                    # Deal damage
                    if projectile.splash_radius > 0:
                        # Splash damage
                        self.apply_splash_damage(projectile)
                    else:
                        # Single target
                        died = projectile.target.take_damage(projectile.damage)
                        print(f"[DEBUG] Enemy health after: {projectile.target.health:.1f}, died: {died}")
                        
                        # Apply slow if freeze tower
                        if projectile.tower_type == 'freeze':
                            tower = next((t for t in self.towers if t.type == 'freeze'), None)
                            if tower:
                                projectile.target.apply_slow(tower.slow_duration, tower.slow_amount)
                
                # Remove projectile
                self.projectiles.remove(projectile)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # Update muzzle flashes
        for flash in self.muzzle_flashes[:]:
            flash.update(dt)
            if not flash.alive:
                self.muzzle_flashes.remove(flash)
        
        # Redraw
        self.draw()
    
    def apply_splash_damage(self, projectile):
        """Apply splash damage to enemies in radius"""
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            dx = enemy.x - projectile.x
            dy = enemy.y - projectile.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= projectile.splash_radius:
                enemy.take_damage(projectile.damage)
    
    def on_mouse_move(self, window, pos):
        """Handle mouse movement for hover effects"""
        # Ignore if over side panel
        if pos[0] > (self.width - 300):
            self.hovered_cell = None
            return
            
        # Convert to grid coordinates (accounting for top bar offset)
        grid_x = int(pos[0] / GRID_SIZE)
        grid_y = int((pos[1] - 50) / GRID_SIZE)
        
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            self.hovered_cell = (grid_x, grid_y)
        else:
            self.hovered_cell = None
    
    def on_touch_down(self, touch):
        """Handle mouse clicks / touches"""
        # Debug: print touch coordinates
        print(f"[TOUCH DEBUG] Touch at ({touch.x:.1f}, {touch.y:.1f}), Window size: ({self.width}, {self.height})")
        
        # First, let child widgets (buttons, UI elements) handle the touch
        # This ensures buttons work before we try to handle grid clicks
        if super(TowerDefenseGame, self).on_touch_down(touch):
            print(f"[TOUCH DEBUG] Touch handled by child widget")
            return True
        
        # If no child handled it, check if it's in the game area
        # Ignore UI areas (top bar and side panel)
        if touch.y < 50 or touch.x > (self.width - 300):
            # Click is on UI area but no widget handled it - ignore
            print(f"[TOUCH DEBUG] Touch in UI area but not handled")
            return False
        
        print(f"[DEBUG] Touch at ({touch.x}, {touch.y})")
        
        # Convert to grid coordinates
        grid_x = int(touch.x / GRID_SIZE)
        grid_y = int((touch.y - 50) / GRID_SIZE)  # Offset by top bar
        
        print(f"[DEBUG] Grid coordinates: ({grid_x}, {grid_y})")
        
        # Check if clicked on existing tower
        clicked_tower = None
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                clicked_tower = tower
                break
        
        if clicked_tower:
            # Select tower for upgrade
            print(f"[DEBUG] Selected existing tower at ({grid_x}, {grid_y})")
            self.selected_tower = clicked_tower
            self.update_tower_buttons()
            return True
        
        # Try to place new tower
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            # Check if cell is valid for placement
            if (grid_x, grid_y) in self.path_cells:
                print(f"[DEBUG] Cannot place - cell is on path")
                return True  # Can't place on path
            
            # Check if already a tower here
            if any(t.grid_x == grid_x and t.grid_y == grid_y for t in self.towers):
                print(f"[DEBUG] Cannot place - tower already exists")
                return True
            
            # Check if can afford
            tower_cost = TOWERS[self.selected_tower_type]['cost']
            if self.currency >= tower_cost:
                # Place tower
                print(f"[DEBUG] Placing {self.selected_tower_type} tower at ({grid_x}, {grid_y})")
                tower = Tower(self.selected_tower_type, grid_x, grid_y, GRID_SIZE)
                self.towers.append(tower)
                self.currency -= tower_cost
                self.selected_tower = tower
            else:
                print(f"[DEBUG] Cannot afford tower - need ${tower_cost}, have ${self.currency}")
        
        return True
    
    def draw(self):
        """Draw everything"""
        self.game_canvas.canvas.clear()
        
        # Offset for top bar and side panel
        y_offset = 50
        side_panel_width = 300
        
        with self.game_canvas.canvas:
            # Background (don't draw under side panel)
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=(0, y_offset), size=(self.width - side_panel_width, self.height - y_offset))
            
            # Draw grid
            Color(*GRID_LINE_COLOR)
            for x in range(GRID_COLS + 1):
                Line(points=[x * GRID_SIZE, y_offset, x * GRID_SIZE, self.grid_pixel_height + y_offset], width=1)
            for y in range(GRID_ROWS + 1):
                Line(points=[0, y * GRID_SIZE + y_offset, self.grid_pixel_width, y * GRID_SIZE + y_offset], width=1)
            
            # Draw path
            Color(*PATH_COLOR)
            for i in range(len(self.path_points) - 1):
                x1, y1 = self.path_points[i]
                x2, y2 = self.path_points[i + 1]
                Line(points=[x1, y1 + y_offset, x2, y2 + y_offset], width=30)
            
            # Draw hover highlight
            if self.hovered_cell and self.hovered_cell not in self.path_cells:
                grid_x, grid_y = self.hovered_cell
                Color(0.3, 0.3, 0.3, 0.5)
                Rectangle(pos=(grid_x * GRID_SIZE, grid_y * GRID_SIZE + y_offset), size=(GRID_SIZE, GRID_SIZE))
            
            # Draw muzzle flashes (behind towers)
            for flash in self.muzzle_flashes:
                alpha = flash.lifetime / 0.1  # Flash is 0.1s
                Color(flash.color[0], flash.color[1], flash.color[2], alpha)
                Ellipse(pos=(flash.x - 20, flash.y - 20 + y_offset), size=(40, 40))
            
            # Draw towers
            for tower in self.towers:
                Color(*tower.stats['color'])
                size = GRID_SIZE * 0.6
                Rectangle(
                    pos=(tower.x - size/2, tower.y - size/2 + y_offset),
                    size=(size, size)
                )
                
                # Draw level stars
                if tower.level > 1:
                    Color(1, 1, 0, 1)  # Gold stars
                    star_y = tower.y + size/2 + 5 + y_offset
                    for i in range(tower.level - 1):  # Level 2 = 1 star, Level 3 = 2 stars
                        star_x = tower.x - 10 + (i * 10)
                        Ellipse(pos=(star_x - 3, star_y - 3), size=(6, 6))
                
                # Draw range if selected
                if tower == self.selected_tower:
                    Color(1, 1, 1, 0.15)
                    Ellipse(
                        pos=(tower.x - tower.range, tower.y - tower.range + y_offset),
                        size=(tower.range * 2, tower.range * 2)
                    )
            
            # Draw enemies
            for enemy in self.enemies:
                Color(*enemy.stats['color'])
                Ellipse(pos=(enemy.x - 15, enemy.y - 15 + y_offset), size=(30, 30))
                
                # Health bar background
                bar_width = 30
                bar_height = 4
                Color(0.3, 0, 0, 1)
                Rectangle(pos=(enemy.x - bar_width/2, enemy.y + 20 + y_offset), size=(bar_width, bar_height))
                
                # Health bar foreground
                health_pct = enemy.get_health_percentage()
                if health_pct > 0.6:
                    Color(0, 0.8, 0, 1)  # Green
                elif health_pct > 0.3:
                    Color(1, 0.8, 0, 1)  # Yellow
                else:
                    Color(1, 0, 0, 1)  # Red
                Rectangle(
                    pos=(enemy.x - bar_width/2, enemy.y + 20 + y_offset),
                    size=(bar_width * health_pct, bar_height)
                )
            
            # Draw projectiles with trail effect
            for projectile in self.projectiles:
                # Bright yellow center
                Color(1, 1, 0.2, 1)
                Ellipse(pos=(projectile.x - 5, projectile.y - 5 + y_offset), size=(10, 10))
                
                # Outer glow
                Color(1, 1, 0, 0.3)
                Ellipse(pos=(projectile.x - 8, projectile.y - 8 + y_offset), size=(16, 16))
            
            # Draw particles
            for particle in self.particles:
                alpha = particle.get_alpha()
                Color(particle.color[0], particle.color[1], particle.color[2], alpha)
                Ellipse(
                    pos=(particle.x - particle.size/2, particle.y - particle.size/2 + y_offset),
                    size=(particle.size, particle.size)
                )


class TowerDefenseApp(App):
    """Main application"""
    
    def build(self):
        # Set window size to 1920x1080
        Window.size = (DESKTOP_WIDTH, DESKTOP_HEIGHT)
        
        # Center the window on screen
        from kivy.core.window import Window as CoreWindow
        try:
            # Try to get screen size and center window
            from kivy.utils import platform
            if platform != 'android' and platform != 'ios':
                # Calculate center position
                # Note: This works best if called before window is shown
                pass
        except:
            pass
        
        return TowerDefenseGame()


if __name__ == '__main__':
    # Let the OS handle window positioning naturally (will center on most systems)
    TowerDefenseApp().run()
