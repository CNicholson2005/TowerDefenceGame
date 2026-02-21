"""
Tower class - Handles tower behavior, targeting, and shooting
"""
import math
from config import TOWERS
from projectile import Projectile


class Tower:
    """Represents a tower that can be placed on the grid"""
    
    def __init__(self, tower_type, grid_x, grid_y, cell_size):
        """
        Initialize a tower
        
        Args:
            tower_type: String key from TOWERS config
            grid_x, grid_y: Grid coordinates
            cell_size: Size of grid cells in pixels
        """
        self.type = tower_type
        self.stats = TOWERS[tower_type].copy()
        
        # Position (center of grid cell)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * cell_size + cell_size // 2
        self.y = grid_y * cell_size + cell_size // 2
        
        # Combat stats
        self.damage = self.stats['damage']
        self.fire_rate = self.stats['fire_rate']
        self.range = self.stats['range']
        self.projectile_speed = self.stats['projectile_speed']
        
        # Shooting
        self.fire_timer = 0
        self.target = None
        
        # Upgrades
        self.level = 1
        
        # Special properties
        self.splash_radius = self.stats.get('splash_radius', 0)
        self.slow_duration = self.stats.get('slow_duration', 0)
        self.slow_amount = self.stats.get('slow_amount', 0)
        
    def update(self, dt, enemies):
        """
        Update tower targeting and shooting
        
        Args:
            dt: Delta time in seconds
            enemies: List of Enemy objects
            
        Returns:
            Projectile or None: New projectile if tower shot
        """
        # Update fire timer
        self.fire_timer -= dt
        
        # Find target if we don't have one or current target is dead or out of range
        if self.target is None or not self.target.alive or self.get_distance_to(self.target) > self.range:
            self.target = self.find_target(enemies)
        
        # Shoot if ready and target is in range
        if self.target and self.fire_timer <= 0:
            # Double-check target is in range (enemy could have moved)
            if self.get_distance_to(self.target) <= self.range:
                self.fire_timer = 1.0 / self.fire_rate
                return self.shoot()
            else:
                # Target moved out of range
                self.target = None
        
        return None
    
    def find_target(self, enemies):
        """
        Find the best target among enemies
        
        Args:
            enemies: List of Enemy objects
            
        Returns:
            Enemy or None: Best target in range
        """
        # Strategy: Target enemy furthest along the path
        best_target = None
        best_progress = -1
        
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            # Check if in range
            distance = self.get_distance_to(enemy)
            if distance <= self.range:
                # Prefer enemies further along the path
                if enemy.path_index > best_progress:
                    best_progress = enemy.path_index
                    best_target = enemy
        
        return best_target
    
    def shoot(self):
        """
        Create a projectile towards current target
        
        Returns:
            Projectile: New projectile object
        """
        return Projectile(
            self.x, self.y,
            self.target,
            self.damage,
            self.projectile_speed,
            self.type,
            self.splash_radius
        )
    
    def get_distance_to(self, enemy):
        """Calculate distance to an enemy"""
        dx = enemy.x - self.x
        dy = enemy.y - self.y
        return math.sqrt(dx**2 + dy**2)
    
    def upgrade(self):
        """
        Upgrade the tower
        
        Returns:
            int: Cost of upgrade, or 0 if max level
        """
        if self.level >= 3:  # Max 3 levels
            return 0
        
        cost = self.stats['upgrade_cost'] * self.level
        
        # Apply upgrades
        self.damage += self.stats['upgrade_damage']
        self.fire_rate += self.stats['upgrade_fire_rate']
        self.level += 1
        
        return cost
    
    def get_upgrade_cost(self):
        """Returns cost to upgrade, or 0 if max level"""
        if self.level >= 3:
            return 0
        return self.stats['upgrade_cost'] * self.level
    
    def get_total_cost(self):
        """Returns total currency invested in this tower"""
        total = self.stats['cost']
        for i in range(1, self.level):
            total += self.stats['upgrade_cost'] * i
        return total
