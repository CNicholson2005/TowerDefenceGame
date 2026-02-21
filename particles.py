"""
Particle system for visual effects
"""
import random
import math


class Particle:
    """Single particle for effects like explosions"""
    
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=1.0, size=5):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity_x
        self.vy = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True
    
    def update(self, dt):
        """Update particle position and lifetime"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Gravity effect
        self.vy -= 100 * dt
        
        # Fade out
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
    
    def get_alpha(self):
        """Get transparency based on remaining lifetime"""
        return self.lifetime / self.max_lifetime


class MuzzleFlash:
    """Brief flash when tower shoots"""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 0.1  # Very brief
        self.alive = True
    
    def update(self, dt):
        """Update flash"""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False


def create_explosion(x, y, color, num_particles=15):
    """Create explosion particle effect"""
    particles = []
    
    for _ in range(num_particles):
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Vary the color slightly
        r = min(1.0, color[0] + random.uniform(-0.2, 0.2))
        g = min(1.0, color[1] + random.uniform(-0.2, 0.2))
        b = min(1.0, color[2] + random.uniform(-0.2, 0.2))
        particle_color = (r, g, b)
        
        lifetime = random.uniform(0.3, 0.7)
        size = random.uniform(3, 8)
        
        particle = Particle(x, y, particle_color, vx, vy, lifetime, size)
        particles.append(particle)
    
    return particles


def create_hit_effect(x, y, num_particles=5):
    """Create small impact effect when projectile hits"""
    particles = []
    
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(30, 80)
        
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Yellow/orange impact
        color = (1.0, random.uniform(0.5, 1.0), 0)
        lifetime = random.uniform(0.1, 0.3)
        size = random.uniform(2, 4)
        
        particle = Particle(x, y, color, vx, vy, lifetime, size)
        particles.append(particle)
    
    return particles
