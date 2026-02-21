"""
Enemy class - Handles enemy behavior, movement, and stats
"""
import math
from config import ENEMIES


class Enemy:
    """Represents an enemy that moves along the path"""
    
    def __init__(self, enemy_type, path_points, start_wave=1):
        """
        Initialize an enemy
        
        Args:
            enemy_type: String key from ENEMIES config
            path_points: List of (x, y) coordinates for the path
            start_wave: Wave number (affects scaling)
        """
        self.type = enemy_type
        self.stats = ENEMIES[enemy_type].copy()
        
        # Scale health based on wave
        self.max_health = self.stats['health'] * (1 + (start_wave - 1) * 0.15)
        self.health = self.max_health
        
        # Movement
        self.path = path_points
        self.path_index = 1  # Start moving toward second waypoint (first is starting position)
        self.x = path_points[0][0]
        self.y = path_points[0][1]
        self.speed = self.stats['speed']
        self.current_speed = self.speed  # Can be modified by slow effects
        
        # Status effects
        self.slow_timer = 0
        self.slow_amount = 0
        
        # State
        self.alive = True
        self.reached_end = False
        
        # Regen for regen type enemies
        self.regen_rate = self.stats.get('regen_rate', 0)
        
    def update(self, dt):
        """
        Update enemy position and status
        
        Args:
            dt: Delta time in seconds
        """
        if not self.alive:
            return
            
        # Handle slow effect
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.current_speed = self.speed * (1 - self.slow_amount)
        else:
            self.current_speed = self.speed
            self.slow_amount = 0
            
        # Handle regeneration
        if self.regen_rate > 0 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + self.regen_rate * dt)
        
        # Move towards next waypoint
        if self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            
            # Calculate distance to target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            # Move towards target
            if distance > 0:
                # Normalize direction and move
                move_distance = self.current_speed * dt
                
                if distance <= move_distance:
                    # Reached waypoint
                    self.x = target_x
                    self.y = target_y
                    self.path_index += 1
                else:
                    # Move towards waypoint
                    self.x += (dx / distance) * move_distance
                    self.y += (dy / distance) * move_distance
        else:
            # Reached end of path
            self.reached_end = True
            self.alive = False
    
    def take_damage(self, damage):
        """
        Apply damage to enemy
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            bool: True if enemy died from this damage
        """
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
    
    def apply_slow(self, duration, amount):
        """
        Apply slow effect to enemy
        
        Args:
            duration: How long the slow lasts (seconds)
            amount: Slow percentage (0.5 = 50% slow)
        """
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_amount = max(self.slow_amount, amount)
    
    def get_health_percentage(self):
        """Returns current health as percentage of max health"""
        return self.health / self.max_health if self.max_health > 0 else 0
    
    def get_reward(self):
        """Returns currency reward for killing this enemy"""
        return self.stats['reward']
