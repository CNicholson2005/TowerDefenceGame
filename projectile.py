"""
Projectile class - Handles projectiles fired by towers
"""
import math


class Projectile:
    """Represents a projectile fired by a tower"""
    
    def __init__(self, x, y, target, damage, speed, tower_type='cannon', splash_radius=0):
        """
        Initialize a projectile
        
        Args:
            x, y: Starting position
            target: Enemy object this projectile is targeting
            damage: Damage to deal on hit
            speed: Projectile speed in pixels/second
            tower_type: Type of tower that fired this
            splash_radius: Radius for splash damage (0 = no splash)
        """
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.tower_type = tower_type
        self.splash_radius = splash_radius
        self.active = True
        
    def update(self, dt):
        """
        Update projectile position
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            bool: True if projectile should be removed (hit or target died)
        """
        if not self.active:
            return True
        
        # If target died, mark inactive but return False to keep checking
        if not self.target.alive:
            self.active = False
            return True
        
        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if hit target
        if distance < 10:  # Hit radius
            return True  # Keep active=True so damage can be applied
        
        # Move towards target
        if distance > 0:
            move_distance = self.speed * dt
            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance
        
        return False
