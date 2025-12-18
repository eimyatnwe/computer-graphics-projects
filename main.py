import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame.font
import pygame.mixer

# Game constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Game states
GAME_STATE_INTRO = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

# Colors (RGB values for wireframe)
WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)
CYAN = (0.0, 1.0, 1.0)
ORANGE = (1.0, 0.5, 0.0)
PURPLE = (1.0, 0.0, 1.0)

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        mag = self.magnitude()
        if (mag > 0):
            return Vector3(self.x/mag, self.y/mag, self.z/mag)
        return Vector3(0, 0, 0)

class GameObject:
    def __init__(self, position, color=WHITE):
        self.position = position
        self.rotation = Vector3(0, 0, 0)
        self.scale = Vector3(1, 1, 1)
        self.color = color
        self.active = True
        self.radius = 1.0  # For collision detection
    
    def update(self, dt):
        pass
    
    def render(self):
        pass

class Tank(GameObject):
    def __init__(self, position, color=GREEN, is_enemy=False):
        super().__init__(position, color)
        self.speed = 5.0 if not is_enemy else 3.0
        self.rotation_speed = 90.0  # degrees per second
        self.health = 1
        self.radius = 1.5  # Reduced from 2.0
        self.last_shot_time = 0
        self.shot_cooldown = 0.5 if not is_enemy else 1.0  # seconds between shots
        self.is_enemy = is_enemy
        self.ai_timer = 0
        self.ai_direction_timer = 0
        self.ai_move_direction = random.uniform(0, 360)
    
    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= self.shot_cooldown
    
    def shoot(self, current_time):
        if self.can_shoot(current_time):
            self.last_shot_time = current_time
            
            # Calculate shooting direction based on tank rotation
            direction = Vector3(
                math.sin(math.radians(self.rotation.y)),
                0,
                math.cos(math.radians(self.rotation.y))
            )
            
            # Start laser from tank barrel position
            laser_start = Vector3(
                self.position.x + direction.x * 2,
                self.position.y + 0.5,
                self.position.z + direction.z * 2
            )
            
            laser_color = CYAN if not self.is_enemy else RED
            owner = "enemy" if self.is_enemy else "player"
            return Laser(laser_start, direction, laser_color, owner)
        return None
    
    def update(self, dt):
        if self.is_enemy:
            # More aggressive AI behavior
            self.ai_timer += dt
            self.ai_direction_timer += dt
            
            # Change direction more frequently
            if self.ai_direction_timer >= random.uniform(1.5, 2.5):  # Reduced from 2.0-3.5
                self.ai_move_direction = random.uniform(0, 360)
                self.ai_direction_timer = 0
            
            # Move faster and more aggressively
            move_x = math.sin(math.radians(self.ai_move_direction)) * self.speed * dt * 0.7  # Increased from 0.5
            move_z = math.cos(math.radians(self.ai_move_direction)) * self.speed * dt * 0.7
            self.position.x += move_x
            self.position.z += move_z
            
            # More active rotation
            self.rotation.y += (random.uniform(-1, 1) * 45) * dt  # Increased from 30
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation.y, 0, 1, 0)
        glScalef(0.7, 0.7, 0.7)
        
        # Enable better material properties
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Render tank shadow first (projected onto ground)
        self.render_shadow()
        
        # Set base tank material properties
        if self.is_enemy:
            # Red enemy tank - metallic look
            base_color = [0.7, 0.1, 0.1]
            highlight_color = [0.9, 0.3, 0.3]
            dark_color = [0.4, 0.05, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.1, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        else:
            # Green player tank - military look
            base_color = [0.1, 0.6, 0.1]
            highlight_color = [0.3, 0.8, 0.3]
            dark_color = [0.05, 0.3, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.2, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.1, 0.7, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 32.0)
        
        # 1. Draw tank hull/body with depth
        glColor3f(*base_color)
        self.draw_tank_hull(1.6, 0.5, 2.4)
        
        # 2. Draw tank tracks (darker)
        glColor3f(*dark_color)
        self.draw_tank_tracks()
        
        # 3. Draw turret (elevated, different color)
        glPushMatrix()
        glTranslatef(0, 0.4, -0.2)  # Slightly back
        glColor3f(*highlight_color)
        self.draw_tank_turret(0.8, 0.4, 0.8)
        
        # 4. Draw cannon barrel (metallic)
        glTranslatef(0, 0.15, 0.6)
        glColor3f(0.3, 0.3, 0.3)  # Dark metallic
        self.draw_tank_barrel()
        
        # 5. Add tank details
        glPopMatrix()
        self.draw_tank_details(base_color, dark_color)
        
        glPopMatrix()

    def render_shadow(self):
        """Render a simple projected shadow on the ground"""
        glPushMatrix()
        
        # Disable lighting for shadow
        glDisable(GL_LIGHTING)
        
        # Set shadow color (semi-transparent black)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.3)
        
        # Project shadow matrix (simple planar projection)
        light_pos = [10, 20, 10]  # Light position
        ground_y = -0.1  # Ground level
        
        # Flatten onto ground plane
        glTranslatef(0, ground_y, 0)
        glScalef(1.0, 0.0, 1.0)  # Flatten Y axis
        
        # Draw simplified tank shape for shadow
        glBegin(GL_QUADS)
        # Shadow hull
        glVertex3f(-1.2, 0, -1.0)
        glVertex3f(1.2, 0, -1.0)
        glVertex3f(1.2, 0, 1.0)
        glVertex3f(-1.2, 0, 1.0)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def draw_tank_hull(self, width, height, depth):
        """Draw main tank body with beveled edges"""
        w, h, d = width/2, height/2, depth/2
        
        glBegin(GL_QUADS)
        
        # Front face (slanted for realistic tank look)
        glNormal3f(0, 0.2, 0.8)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, d*0.8)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        # Top face (angled)
        glNormal3f(0, 0.9, 0.1)
        glVertex3f(-w*0.8, h, -d)
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, -d)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        
        # Right face (angled)
        glNormal3f(0.8, 0.2, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w*0.8, h, -d)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(w, -h, d)
        
        # Left face (angled)
        glNormal3f(-0.8, 0.2, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, -d)
        
        glEnd()

    def draw_tank_tracks(self):
        """Draw tank tracks on both sides"""
        track_width = 0.2
        track_height = 0.3
        hull_width = 1.6
        
        for side in [-1, 1]:  # Left and right tracks
            glPushMatrix()
            glTranslatef(side * (hull_width/2 + track_width/2), -0.1, 0)
            
            # Track body
            glBegin(GL_QUADS)
            
            # Outer face
            glNormal3f(side, 0, 0)
            glVertex3f(side * track_width/2, -track_height, -1.0)
            glVertex3f(side * track_width/2, track_height, -1.0)
            glVertex3f(side * track_width/2, track_height, 1.0)
            glVertex3f(side * track_width/2, -track_height, 1.0)
            
            # Top
            glNormal3f(0, 1, 0)
            glVertex3f(-track_width/2, track_height, -1.0)
            glVertex3f(-track_width/2, track_height, 1.0)
            glVertex3f(track_width/2, track_height, 1.0)
            glVertex3f(track_width/2, track_height, -1.0)
            
            # Bottom
            glNormal3f(0, -1, 0)
            glVertex3f(-track_width/2, -track_height, -1.0)
            glVertex3f(track_width/2, -track_height, -1.0)
            glVertex3f(track_width/2, -track_height, 1.0)
            glVertex3f(-track_width/2, -track_height, 1.0)
            
            glEnd()
            
            # Track details (wheels/road wheels)
            self.draw_track_wheels()
            
            glPopMatrix()

    def draw_track_wheels(self):
        """Draw road wheels on the track"""
        wheel_radius = 0.15
        wheel_positions = [-0.8, -0.3, 0.2, 0.7]
        
        for pos_z in wheel_positions:
            glPushMatrix()
            glTranslatef(0, 0, pos_z)
            
            # Simple wheel (circle)
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(1, 0, 0)
            glVertex3f(0, 0, 0)  # Center
            
            segments = 8
            for i in range(segments + 1):
                angle = (i / segments) * 2 * math.pi
                y = wheel_radius * math.cos(angle)
                z = wheel_radius * math.sin(angle)
                glVertex3f(0, y, z)
            
            glEnd()
            glPopMatrix()

    def draw_tank_turret(self, width, height, depth):
        """Draw tank turret with rounded edges"""
        w, h, d = width/2, height/2, depth/2
        
        # Main turret body (hexagonal for realism)
        glBegin(GL_QUADS)
        
        # Front face (angled)
        glNormal3f(0, 0.1, 0.9)
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(w*0.7, -h, d)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        # Top face (rounded)
        glNormal3f(0, 1, 0)
        glVertex3f(-w*0.8, h, -d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(w*0.8, h, -d*0.8)
        
        # Angled sides
        glNormal3f(0.7, 0.3, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w*0.8, h, -d*0.8)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(w*0.7, -h, d)
        
        glNormal3f(-0.7, 0.3, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(-w*0.8, h, -d*0.8)
        
        glEnd()

    def draw_tank_barrel(self):
        """Draw detailed tank cannon barrel"""
        barrel_length = 1.4
        barrel_radius = 0.08
        segments = 12
        
        # Main barrel cylinder
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = barrel_radius * math.cos(angle)
            y = barrel_radius * math.sin(angle)
            
            glNormal3f(math.cos(angle), math.sin(angle), 0)
            glVertex3f(x, y, 0)
            glVertex3f(x, y, barrel_length)
        glEnd()
        
        # Barrel end cap
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, barrel_length)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = barrel_radius * math.cos(angle)
            y = barrel_radius * math.sin(angle)
            glVertex3f(x, y, barrel_length)
        glEnd()
        
        # Muzzle brake (additional detail)
        glTranslatef(0, 0, barrel_length - 0.1)
        glScalef(1.2, 1.2, 0.1)
        
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = barrel_radius * math.cos(angle)
            y = barrel_radius * math.sin(angle)
            
            glNormal3f(math.cos(angle), math.sin(angle), 0)
            glVertex3f(x, y, 0)
            glVertex3f(x, y, 1)
        glEnd()

    def draw_tank_details(self, base_color, dark_color):
        """Add extra details like antenna, hatches, etc."""
        # Commander hatch
        glPushMatrix()
        glTranslatef(-0.2, 0.8, -0.3)
        glColor3f(*dark_color)
        glScalef(0.3, 0.05, 0.3)
        self.draw_filled_cube(1, 1, 1)
        glPopMatrix()
        
        # Antenna
        glPushMatrix()
        glTranslatef(0.3, 0.9, -0.5)
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.8, 0)
        glEnd()
        glPopMatrix()
        
        # Side armor panels
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.9, 0, 0)
            glColor3f(base_color[0] * 0.8, base_color[1] * 0.8, base_color[2] * 0.8)
            glScalef(0.05, 0.3, 1.5)
            self.draw_filled_cube(1, 1, 1)
            glPopMatrix()

    def draw_filled_cube(self, width, height, depth):
        """Draw a filled cube with proper normals for lighting"""
        w, h, d = width/2, height/2, depth/2
        
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        
        glEnd()

class Mountain(GameObject):
    def __init__(self, position, color=WHITE):
        super().__init__(position, color)
        self.radius = 2.0  # Reduced from 3.0
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Set mountain material (rocky/snowy)
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 16.0)
        glColor3f(0.9, 0.9, 0.9)  # Light gray/white
        
        # Draw filled pyramid with proper normals
        base = 2.0
        peak_height = 2.8
        
        glBegin(GL_TRIANGLES)
        
        # Front face (calculate proper normal)
        v1 = [-base, 0, base]
        v2 = [base, 0, base]
        v3 = [0, peak_height, 0]
        # Normal calculation for proper lighting
        normal = self.calculate_normal(v1, v2, v3)
        glNormal3f(*normal)
        glVertex3f(*v1)
        glVertex3f(*v2)
        glVertex3f(*v3)
        
        # Right face
        v1 = [base, 0, base]
        v2 = [base, 0, -base]
        v3 = [0, peak_height, 0]
        normal = self.calculate_normal(v1, v2, v3)
        glNormal3f(*normal)
        glVertex3f(*v1)
        glVertex3f(*v2)
        glVertex3f(*v3)
        
        # Back face
        v1 = [base, 0, -base]
        v2 = [-base, 0, -base]
        v3 = [0, peak_height, 0]
        normal = self.calculate_normal(v1, v2, v3)
        glNormal3f(*normal)
        glVertex3f(*v1)
        glVertex3f(*v2)
        glVertex3f(*v3)
        
        # Left face
        v1 = [-base, 0, -base]
        v2 = [-base, 0, base]
        v3 = [0, peak_height, 0]
        normal = self.calculate_normal(v1, v2, v3)
        glNormal3f(*normal)
        glVertex3f(*v1)
        glVertex3f(*v2)
        glVertex3f(*v3)
        
        glEnd()
        
        # Draw base with proper normal
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-base, 0, -base)
        glVertex3f(base, 0, -base)
        glVertex3f(base, 0, base)
        glVertex3f(-base, 0, base)
        glEnd()
        
        glPopMatrix()
    
    def calculate_normal(self, v1, v2, v3):
        # Calculate cross product for normal
        u = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
        v = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
        
        normal = [
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0]
        ]
        
        # Normalize
        length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        if length > 0:
            normal = [normal[0]/length, normal[1]/length, normal[2]/length]
        
        return normal

class LifeSphere(GameObject):
    def __init__(self, position, color=YELLOW):
        super().__init__(position, color)
        self.radius = 0.35  # Reduced from 0.5
        self.bob_time = 0
        self.original_y = position.y
    
    def update(self, dt):
        self.bob_time += dt * 2
        self.position.y = self.original_y + math.sin(self.bob_time) * 0.2  # Reduced bobbing from 0.3
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Set glowing yellow material
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.4, 0.4, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 0.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        glColor3f(1.0, 1.0, 0.2)  # Bright yellow
        
        # Draw filled sphere using triangles with proper normals
        radius = 0.35
        stacks = 8
        slices = 8
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            glBegin(GL_TRIANGLE_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                # Proper normals for sphere lighting
                glNormal3f(x * zr0, z0, y * zr0)
                glVertex3f(x * zr0, z0, y * zr0)
                glNormal3f(x * zr1, z1, y * zr1)
                glVertex3f(x * zr1, z1, y * zr1)
            glEnd()
        
        glPopMatrix()

class Laser(GameObject):
    def __init__(self, position, direction, color=CYAN, owner="player"):
        super().__init__(position, color)
        self.direction = direction
        self.speed = 20.0
        self.radius = 0.15  # Reduced from 0.2
        self.lifetime = 3.0  # seconds
        self.owner = owner
    
    def update(self, dt):
        # Move laser forward
        self.position.x += self.direction.x * self.speed * dt
        self.position.y += self.direction.y * self.speed * dt
        self.position.z += self.direction.z * self.speed * dt
        
        # Reduce lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Set glowing laser material
        if self.owner == "player":
            # Cyan laser
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.4, 0.4, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 1.0, 1.0, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 1.0, 1.0, 1.0])
            glColor3f(0.2, 1.0, 1.0)
        else:
            # Red laser
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.4, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.2, 0.2, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 0.5, 0.5, 1.0])
            glColor3f(1.0, 0.2, 0.2)
        
        glMaterialf(GL_FRONT, GL_SHININESS, 128.0)  # Very shiny
        
        # Draw filled laser beam as a stretched cube with proper normals
        glScalef(0.1, 0.1, 0.7)
        
        glBegin(GL_QUADS)
        
        # All faces with proper normals for lighting
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, 1)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, 1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, -1, -1)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-1, 1, -1)
        glVertex3f(-1, 1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(1, 1, -1)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, -1, 1)
        glVertex3f(-1, -1, 1)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 1)
        glVertex3f(1, -1, 1)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, -1, 1)
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, 1, -1)
        
        glEnd()
        glPopMatrix()

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)  # Initialize sound
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Arctic Tank 3D")
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize sound effects
        self.init_sounds()
        
        # Initialize OpenGL with better lighting
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)  # Add second light
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)  # Automatically normalize normals
        glEnable(GL_BLEND)
        
        # Set background color (dark blue arctic sky)
        glClearColor(0.05, 0.05, 0.2, 1.0)
        
        # Configure material properties
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up main light (sun-like, from above and front)
        glLightfv(GL_LIGHT0, GL_POSITION, [15, 25, 10, 1])  # Positioned light
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.15, 1])   # Soft blue ambient
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1])   # Bright white diffuse
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.7, 1])  # Moderate specular
        
        # Set up secondary light (fill light, from side)
        glLightfv(GL_LIGHT1, GL_POSITION, [-10, 15, -8, 1])  # From the other side
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.05, 0.05, 0.1, 1])   # Very soft ambient
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.3, 0.4, 1])   # Soft fill light
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.1, 0.1, 0.2, 1])  # Low specular
        
        # Set global ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.02, 0.02, 0.05, 1])
        
        # Enable smooth shading
        glShadeModel(GL_SMOOTH)
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (WINDOW_WIDTH/WINDOW_HEIGHT), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GAME_STATE_INTRO
        self.player_lives = 3
        self.score = 0
        
        # Enemy spawning - more aggressive
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 3.0  # Reduced from 5.0 seconds
        self.max_enemies = 5  # Increased from 3
        
        # Initialize game objects
        self.init_game_objects()
        
        self.camera_pos = Vector3(0, 5, 10)
        self.camera_target = Vector3(0, 0, 0)
        
        # Intro animation
        self.intro_rotation = 0

    def init_sounds(self):
        """Initialize sound effects and background music"""
        try:
            # Create sound effects programmatically (since we don't have audio files)
            
            # Laser shooting sound (high frequency beep)
            self.laser_sound = self.create_laser_sound()
            
            # Hit/damage sound (lower frequency noise)
            self.hit_sound = self.create_hit_sound()
            
            # Life lost sound (dramatic falling tone)
            self.life_lost_sound = self.create_life_lost_sound()
            
            # Enemy destroyed sound (explosion-like)
            self.enemy_destroyed_sound = self.create_enemy_destroyed_sound()
            
            # Life sphere collected sound (positive chime)
            self.life_sphere_sound = self.create_life_sphere_sound()
            
            # Background ambient sound (wind/arctic atmosphere)
            self.create_background_sound()
            
            print("Sound system initialized successfully!")
            
        except pygame.error as e:
            print(f"Sound initialization failed: {e}")
            # Create dummy sounds that do nothing if sound fails
            self.laser_sound = None
            self.hit_sound = None
            self.life_lost_sound = None
            self.enemy_destroyed_sound = None
            self.life_sphere_sound = None

    def create_laser_sound(self):
        """Create a laser shooting sound effect"""
        import numpy as np
        
        # Create a short high-frequency beep
        duration = 0.2  # seconds
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Combine multiple frequencies for a laser-like sound
        frequency1 = 800  # Base frequency
        frequency2 = 1200  # Harmonic
        
        # Create the waveform with frequency modulation
        wave = (np.sin(2 * np.pi * frequency1 * t) * 0.3 + 
                np.sin(2 * np.pi * frequency2 * t) * 0.2) * np.exp(-t * 8)  # Exponential decay
        
        # Convert to the format pygame expects
        wave = (wave * 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
        stereo_wave[:, 0] = wave  # Left channel
        stereo_wave[:, 1] = wave  # Right channel
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def create_hit_sound(self):
        """Create a hit/damage sound effect"""
        import numpy as np
        
        duration = 0.3
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a harsh, noisy sound for hits
        frequency = 200  # Low frequency
        noise = np.random.normal(0, 0.1, len(t))  # White noise
        wave = (np.sin(2 * np.pi * frequency * t) * 0.4 + noise * 0.6) * np.exp(-t * 5)
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
        stereo_wave[:, 0] = wave
        stereo_wave[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def create_life_lost_sound(self):
        """Create a dramatic life lost sound"""
        import numpy as np
        
        duration = 1.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Falling tone effect
        start_freq = 400
        end_freq = 100
        frequency = start_freq * np.exp(-t * 2)  # Exponentially falling frequency
        
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 1.5)  # With decay
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
        stereo_wave[:, 0] = wave
        stereo_wave[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def create_enemy_destroyed_sound(self):
        """Create an explosion-like sound for enemy destruction"""
        import numpy as np
        
        duration = 0.5
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Explosive sound with multiple frequency components
        freq1 = 150
        freq2 = 300
        freq3 = 450
        noise = np.random.normal(0, 0.3, len(t))
        
        wave = (np.sin(2 * np.pi * freq1 * t) * 0.3 +
                np.sin(2 * np.pi * freq2 * t) * 0.2 +
                np.sin(2 * np.pi * freq3 * t) * 0.1 +
                noise * 0.4) * np.exp(-t * 4)
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
        stereo_wave[:, 0] = wave
        stereo_wave[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def create_life_sphere_sound(self):
        """Create a positive chime sound for collecting life spheres"""
        import numpy as np
        
        duration = 0.4
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Pleasant ascending chime
        freq1 = 523  # C5
        freq2 = 659  # E5
        freq3 = 784  # G5
        
        # Create a chord that fades in and out
        envelope = np.sin(np.pi * t / duration)  # Bell-like envelope
        wave = (np.sin(2 * np.pi * freq1 * t) * 0.4 +
                np.sin(2 * np.pi * freq2 * t) * 0.3 +
                np.sin(2 * np.pi * freq3 * t) * 0.3) * envelope
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
        stereo_wave[:, 0] = wave
        stereo_wave[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def create_background_sound(self):
        """Create ambient background sound (wind/arctic atmosphere)"""
        import numpy as np
        
        try:
            # Create a longer ambient wind sound
            duration = 5.0  # 5 seconds, will loop
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create wind-like sound with filtered white noise
            noise = np.random.normal(0, 0.15, len(t))
            
            # Apply low-pass filter effect (simple approximation)
            filtered_noise = np.convolve(noise, np.ones(50)/50, mode='same')
            
            # Add some subtle low-frequency rumbling
            rumble = np.sin(2 * np.pi * 30 * t) * 0.05 + np.sin(2 * np.pi * 45 * t) * 0.03
            
            wave = filtered_noise + rumble
            wave = (wave * 16383).astype(np.int16)  # Lower volume for background
            
            stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
            stereo_wave[:, 0] = wave
            stereo_wave[:, 1] = wave
            
            self.background_sound = pygame.sndarray.make_sound(stereo_wave)
            
            # Start playing background sound in loop
            self.background_sound.play(-1)  # -1 means loop indefinitely
            self.background_sound.set_volume(0.3)  # Set to 30% volume
            
        except Exception as e:
            print(f"Background sound creation failed: {e}")
            self.background_sound = None

    def play_sound(self, sound, volume=1.0):
        """Safely play a sound effect"""
        if sound:
            try:
                sound.set_volume(volume)
                sound.play()
            except pygame.error:
                pass  # Silently ignore sound errors

    def init_game_objects(self):
        self.player_tank = Tank(Vector3(0, 0, 0), GREEN)
        self.enemy_tanks = []
        
        # Add many more mountains scattered across a larger area
        self.mountains = [
            # Close mountains around spawn
            Mountain(Vector3(5, 0, 5), WHITE),
            Mountain(Vector3(-8, 0, 12), WHITE),
            Mountain(Vector3(15, 0, -5), WHITE),
            Mountain(Vector3(-15, 0, -8), WHITE),
            Mountain(Vector3(20, 0, 15), WHITE),
            
            # Far North
            Mountain(Vector3(10, 0, 25), WHITE),
            Mountain(Vector3(-5, 0, 30), WHITE),
            Mountain(Vector3(25, 0, 35), WHITE),
            Mountain(Vector3(-20, 0, 28), WHITE),
            Mountain(Vector3(0, 0, 40), WHITE),
            Mountain(Vector3(18, 0, 42), WHITE),
            Mountain(Vector3(-12, 0, 45), WHITE),
            
            # Far South
            Mountain(Vector3(8, 0, -25), WHITE),
            Mountain(Vector3(-15, 0, -30), WHITE),
            Mountain(Vector3(22, 0, -35), WHITE),
            Mountain(Vector3(-25, 0, -28), WHITE),
            Mountain(Vector3(5, 0, -40), WHITE),
            Mountain(Vector3(-8, 0, -42), WHITE),
            Mountain(Vector3(30, 0, -25), WHITE),
            
            # Far East
            Mountain(Vector3(35, 0, 10), WHITE),
            Mountain(Vector3(40, 0, -5), WHITE),
            Mountain(Vector3(45, 0, 20), WHITE),
            Mountain(Vector3(38, 0, 0), WHITE),
            Mountain(Vector3(42, 0, 15), WHITE),
            Mountain(Vector3(50, 0, 8), WHITE),
            
            # Far West
            Mountain(Vector3(-35, 0, 10), WHITE),
            Mountain(Vector3(-40, 0, -5), WHITE),
            Mountain(Vector3(-45, 0, 20), WHITE),
            Mountain(Vector3(-38, 0, 0), WHITE),
            Mountain(Vector3(-42, 0, 15), WHITE),
            Mountain(Vector3(-50, 0, 8), WHITE),
            
            # More scattered mountains
            Mountain(Vector3(12, 0, -15), WHITE),
            Mountain(Vector3(-18, 0, 22), WHITE),
            Mountain(Vector3(28, 0, -8), WHITE),
            Mountain(Vector3(-22, 0, -18), WHITE),
            Mountain(Vector3(15, 0, 30), WHITE),
            Mountain(Vector3(-28, 0, -25), WHITE),
            Mountain(Vector3(35, 0, -15), WHITE),
            Mountain(Vector3(-32, 0, 25), WHITE)
        ]
        
        # More life spheres scattered around
        self.life_spheres = [
            LifeSphere(Vector3(-3, 1, 8), YELLOW),
            LifeSphere(Vector3(12, 1, -8), YELLOW),
            LifeSphere(Vector3(-10, 1, 15), YELLOW),
            LifeSphere(Vector3(25, 1, 20), YELLOW),
            LifeSphere(Vector3(-20, 1, 25), YELLOW),
            LifeSphere(Vector3(18, 1, -20), YELLOW),
            LifeSphere(Vector3(-15, 1, -25), YELLOW),
            LifeSphere(Vector3(30, 1, 10), YELLOW),
            LifeSphere(Vector3(-25, 1, -15), YELLOW),
            LifeSphere(Vector3(8, 1, 35), YELLOW)
        ]
        self.lasers = []
        
    def spawn_enemy(self):
        if len(self.enemy_tanks) < self.max_enemies:
            # Spawn enemy at random position around the player (not just at map edges)
            player_pos = self.player_tank.position
            
            # Choose random spawn method
            spawn_method = random.choice(['circle', 'forward', 'sides'])
            
            if spawn_method == 'circle':
                # Spawn in a circle around player
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(15, 30)
                spawn_x = player_pos.x + math.cos(angle) * distance
                spawn_z = player_pos.z + math.sin(angle) * distance
            
            elif spawn_method == 'forward':
                # Spawn ahead of player's movement direction
                player_direction = math.radians(self.player_tank.rotation.y)
                forward_distance = random.uniform(20, 40)
                side_offset = random.uniform(-15, 15)
                
                spawn_x = player_pos.x + math.sin(player_direction) * forward_distance + side_offset
                spawn_z = player_pos.z + math.cos(player_direction) * forward_distance + side_offset
            
            else:  # sides
                # Spawn to the sides of player
                side = random.choice([-1, 1])
                side_distance = random.uniform(20, 35)
                forward_offset = random.uniform(-10, 20)
                
                player_direction = math.radians(self.player_tank.rotation.y)
                # Calculate perpendicular direction
                perp_direction = player_direction + (math.pi/2 * side)
                
                spawn_x = player_pos.x + math.sin(perp_direction) * side_distance + math.sin(player_direction) * forward_offset
                spawn_z = player_pos.z + math.cos(perp_direction) * side_distance + math.cos(player_direction) * forward_offset
            
            # Make sure enemy doesn't spawn inside a mountain
            safe_spawn = True
            for mountain in self.mountains:
                if self.distance(Vector3(spawn_x, 0, spawn_z), mountain.position) < (mountain.radius + 3):
                    safe_spawn = False
                    break
            
            if safe_spawn:
                new_enemy = Tank(Vector3(spawn_x, 0, spawn_z), RED, is_enemy=True)
                self.enemy_tanks.append(new_enemy)
                print(f"Enemy spawned at ({spawn_x:.1f}, 0, {spawn_z:.1f})")
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            
            if self.game_state == GAME_STATE_INTRO:
                self.update_intro(dt)
                self.render_intro()
            elif self.game_state == GAME_STATE_PLAYING:
                self.handle_input(dt)
                self.update_game(dt)
                self.render_game()
            elif self.game_state == GAME_STATE_GAME_OVER:
                self.render_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == GAME_STATE_INTRO:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.game_state = GAME_STATE_PLAYING
                        # Start background sound when game begins
                        if hasattr(self, 'background_sound') and self.background_sound:
                            self.background_sound.play(-1)
                            self.background_sound.set_volume(0.3)
                elif self.game_state == GAME_STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        # Restart game
                        self.game_state = GAME_STATE_PLAYING
                        self.player_lives = 3
                        self.score = 0
                        self.init_game_objects()
                        # Restart background sound
                        if hasattr(self, 'background_sound') and self.background_sound:
                            self.background_sound.play(-1)
                            self.background_sound.set_volume(0.3)
    
    def update_intro(self, dt):
        self.intro_rotation += dt * 30  # Rotate 30 degrees per second
    
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            # Move forward
            forward_x = math.sin(math.radians(self.player_tank.rotation.y))
            forward_z = math.cos(math.radians(self.player_tank.rotation.y))
            self.player_tank.position.x += forward_x * self.player_tank.speed * dt
            self.player_tank.position.z += forward_z * self.player_tank.speed * dt
        
        if keys[pygame.K_s]:
            # Move backward
            forward_x = math.sin(math.radians(self.player_tank.rotation.y))
            forward_z = math.cos(math.radians(self.player_tank.rotation.y))
            self.player_tank.position.x -= forward_x * self.player_tank.speed * dt
            self.player_tank.position.z -= forward_z * self.player_tank.speed * dt
        
        if keys[pygame.K_a]:
            self.player_tank.rotation.y += self.player_tank.rotation_speed * dt
        
        if keys[pygame.K_d]:
            self.player_tank.rotation.y -= self.player_tank.rotation_speed * dt
        
        # Shooting with sound effect
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks() / 1000.0
            laser = self.player_tank.shoot(current_time)
            if laser:
                self.lasers.append(laser)
                # Play laser shooting sound
                self.play_sound(self.laser_sound, 0.5)
        
        # Update camera to follow tank
        self.update_camera()
    
    def update_camera(self):
        # Position camera closer since objects are smaller
        offset_distance = 6  # Reduced from 8
        offset_height = 2.5  # Reduced from 3
        
        camera_x = self.player_tank.position.x - math.sin(math.radians(self.player_tank.rotation.y)) * offset_distance
        camera_z = self.player_tank.position.z - math.cos(math.radians(self.player_tank.rotation.y)) * offset_distance
        
        self.camera_pos = Vector3(camera_x, self.player_tank.position.y + offset_height, camera_z)
        self.camera_target = Vector3(self.player_tank.position.x, self.player_tank.position.y, self.player_tank.position.z)
    
    def update_game(self, dt):
        # Enemy spawning - more frequent
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            # Gradually increase spawn rate (faster)
            self.enemy_spawn_interval = max(2.0, self.enemy_spawn_interval - 0.05)  # Faster decrease
        
        # Ensure there's always action nearby
        self.ensure_enemies_nearby()
        
        # Update all game objects
        self.player_tank.update(dt)
        
        for enemy in self.enemy_tanks:
            enemy.update(dt)
            # Enemy shooting with sound
            current_time = pygame.time.get_ticks() / 1000.0
            if random.random() < 0.01:  # 1% chance per frame to shoot
                laser = enemy.shoot(current_time)
                if laser:
                    self.lasers.append(laser)
                    # Play enemy laser sound (different volume/pitch)
                    self.play_sound(self.laser_sound, 0.3)  # Quieter for enemy
        
        for sphere in self.life_spheres:
            sphere.update(dt)
        
        # Update lasers
        for laser in self.lasers[:]:
            laser.update(dt)
            if not laser.active:
                self.lasers.remove(laser)
        
        # Collision detection
        self.check_collisions()
        
        # Check game over
        if self.player_lives <= 0:
            self.game_state = GAME_STATE_GAME_OVER
            # Stop background sound when game over
            if hasattr(self, 'background_sound') and self.background_sound:
                self.background_sound.stop()
    
    def ensure_enemies_nearby(self):
        if len(self.enemy_tanks) < 2:  # Always keep at least 2 enemies
            self.spawn_enemy()
            
        # If player is far from all enemies, spawn one closer
        player_pos = self.player_tank.position
        closest_enemy_distance = float('inf')
        
        for enemy in self.enemy_tanks:
            dist = self.distance(player_pos, enemy.position)
            closest_enemy_distance = min(closest_enemy_distance, dist)
        
        if closest_enemy_distance > 25:  # If furthest from all enemies
            # Force spawn an enemy closer
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(12, 20)  # Closer spawn
            spawn_x = player_pos.x + math.cos(angle) * distance
            spawn_z = player_pos.z + math.sin(angle) * distance
            
            new_enemy = Tank(Vector3(spawn_x, 0, spawn_z), RED, is_enemy=True)
            self.enemy_tanks.append(new_enemy)
            print(f"Close enemy spawned at ({spawn_x:.1f}, 0, {spawn_z:.1f})")
    
    def check_collisions(self):
        # Check life sphere collection
        for sphere in self.life_spheres[:]:
            if self.distance(self.player_tank.position, sphere.position) < (self.player_tank.radius + sphere.radius):
                self.life_spheres.remove(sphere)
                self.player_lives += 1
                self.score += 5
                print(f"Life sphere collected! Lives: {self.player_lives}")
                # Play life sphere collection sound
                self.play_sound(self.life_sphere_sound, 0.7)
        
        # Check laser-enemy collisions
        for laser in self.lasers[:]:
            if laser.owner == "player":
                for enemy in self.enemy_tanks[:]:
                    if self.distance(laser.position, enemy.position) < (laser.radius + enemy.radius):
                        # Hit enemy
                        self.lasers.remove(laser)
                        self.enemy_tanks.remove(enemy)
                        self.score += 10
                        print(f"Enemy destroyed! Score: {self.score}")
                        # Play enemy destroyed sound
                        self.play_sound(self.enemy_destroyed_sound, 0.6)
                        break
        
        # Check laser-player collisions
        for laser in self.lasers[:]:
            if laser.owner == "enemy":
                if self.distance(laser.position, self.player_tank.position) < (laser.radius + self.player_tank.radius):
                    # Player hit
                    self.lasers.remove(laser)
                    self.player_lives -= 1
                    print(f"Player hit by laser! Lives remaining: {self.player_lives}")
                    # Play hit sound and life lost sound if this was fatal
                    self.play_sound(self.hit_sound, 0.8)
                    if self.player_lives <= 0:
                        self.play_sound(self.life_lost_sound, 0.9)
        
        # Check laser-mountain collisions (lasers blocked by mountains)
        for laser in self.lasers[:]:
            for mountain in self.mountains:
                if self.distance(laser.position, mountain.position) < (laser.radius + mountain.radius):
                    self.lasers.remove(laser)
                    print("Laser blocked by mountain!")
                    # Play a softer hit sound for laser hitting mountain
                    self.play_sound(self.hit_sound, 0.3)
                    break
        
        # Check player-mountain collisions
        for mountain in self.mountains:
            if self.distance(self.player_tank.position, mountain.position) < (self.player_tank.radius + mountain.radius):
                # Player loses a life when hitting mountain
                self.player_lives -= 1
                print(f"Player hit mountain! Lives remaining: {self.player_lives}")
                # Play hit sound and life lost sound if this was fatal
                self.play_sound(self.hit_sound, 0.8)
                if self.player_lives <= 0:
                    self.play_sound(self.life_lost_sound, 0.9)
                
                # Push back player
                direction = Vector3(
                    self.player_tank.position.x - mountain.position.x,
                    0,
                    self.player_tank.position.z - mountain.position.z
                )
                distance = direction.magnitude()
                if distance > 0:
                    # Normalize direction
                    direction.x /= distance
                    direction.z /= distance
                    # Calculate push distance to separate player from mountain
                    push_distance = (self.player_tank.radius + mountain.radius) - distance + 0.5
                    # Push player away from mountain
                    self.player_tank.position.x += direction.x * push_distance
                    self.player_tank.position.z += direction.z * push_distance
                
                break  # Only process one mountain collision per frame
    
    def distance(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)
    
    def render_intro(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Disable lighting for 2D UI
        glDisable(GL_LIGHTING)
        
        # Switch to 2D rendering for intro
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)  # Note: flipped Y axis for pygame text
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Animated background
        self.draw_animated_background_simple()
        
        # Render text using pygame fonts
        self.render_text_to_opengl("ARCTIC TANK", WINDOW_WIDTH//2 - 150, 100, self.title_font, CYAN)
        self.render_text_to_opengl("3D WIREFRAME", WINDOW_WIDTH//2 - 120, 180, self.large_font, WHITE)
        
        # Controls section
        y_pos = 280
        self.render_text_to_opengl("CONTROLS:", 100, y_pos, self.medium_font, YELLOW)
        y_pos += 50
        
        controls = [
            "W - Move Forward",
            "S - Move Backward", 
            "A - Turn Left",
            "D - Turn Right",
            "SPACE - Shoot"
        ]
        
        for control in controls:
            self.render_text_to_opengl(control, 120, y_pos, self.small_font, GREEN)
            y_pos += 30
        
        # Objectives section
        y_pos += 30
        self.render_text_to_opengl("OBJECTIVES:", 100, y_pos, self.medium_font, YELLOW)
        y_pos += 50
        
        objectives = [
            "• Destroy enemy tanks (+10 pts)",
            "• Collect life spheres (+1 life, +5 pts)",
            "• Avoid mountains (lose life)",
            "• Survive as long as possible!"
        ]
        
        for objective in objectives:
            self.render_text_to_opengl(objective, 120, y_pos, self.small_font, WHITE)
            y_pos += 30
        
        # Start instruction (blinking)
        start_color = ORANGE
        if int(pygame.time.get_ticks() / 500) % 2:
            start_color = RED
        
        self.render_text_to_opengl("Press ENTER or SPACE to start", WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 100, self.medium_font, start_color)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)  # Re-enable lighting
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def render_text_to_opengl(self, text, x, y, font, color):
        # Create text surface
        text_surface = font.render(text, True, (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Enable blending for text
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Save current state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glRasterPos2f(x, y)
        
        # Draw the text
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        # Restore state
        glPopAttrib()
        glDisable(GL_BLEND)
    
    def draw_animated_background_simple(self):
        glColor3f(*BLUE)
        time = pygame.time.get_ticks() / 1000.0
        
        # Moving lines
        for i in range(5):
            y = (time * 50 + i * 100) % WINDOW_HEIGHT
            glBegin(GL_LINES)
            glVertex2f(0, y)
            glVertex2f(WINDOW_WIDTH, y)
            glEnd()
        
        # Simple rotating squares
        for i in range(3):
            x = 150 + i * 300
            y = 400
            size = 30
            angle = time * 45 + i * 120
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glRotatef(angle, 0, 0, 1)
            glBegin(GL_LINE_LOOP)
            glVertex2f(-size, -size)
            glVertex2f(size, -size)
            glVertex2f(size, size)
            glVertex2f(-size, size)
            glEnd()
            glPopMatrix()
    
    def render_game(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Enable fog for atmospheric depth
        glEnable(GL_FOG)
        glFogf(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
        glFogfv(GL_FOG_COLOR, [0.05, 0.05, 0.2, 1.0])
        
        # Set camera
        gluLookAt(self.camera_pos.x, self.camera_pos.y, self.camera_pos.z,
                  self.camera_target.x, self.camera_target.y, self.camera_target.z,
                  0, 1, 0)
        
        # Render all objects
        self.player_tank.render()
        
        for enemy in self.enemy_tanks:
            enemy.render()
        
        for mountain in self.mountains:
            mountain.render()
        
        for sphere in self.life_spheres:
            sphere.render()
        
        # Render lasers
        for laser in self.lasers:
            laser.render()
        
        glDisable(GL_FOG)
        self.render_hud()
    
    def render_game_over(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Switch to 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Game Over screen
        self.render_text_to_opengl("GAME OVER", WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 50, self.title_font, RED)
        self.render_text_to_opengl(f"Final Score: {self.score}", WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 20, self.medium_font, WHITE)
        self.render_text_to_opengl("Press R to restart", WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 70, self.medium_font, YELLOW)
        
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def render_hud(self):
        # Disable lighting for HUD
        glDisable(GL_LIGHTING)
        
        # Switch to 2D rendering for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)  # Flipped Y for pygame text
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Lives indicator (filled heart shapes with special effects for low health)
        current_time = pygame.time.get_ticks() / 1000.0
        
        for i in range(self.player_lives):
            x = 20 + i * 40  # Increased spacing for larger hearts
            y = 25
            
            if self.player_lives <= 1:
                # Pulse when only 1 life left (critical health)
                self.draw_pulsing_heart(x, y, 15, current_time)
            else:
                # Normal heart
                self.draw_filled_heart(x, y, 15)
        
        # Score and enemy count using real text
        self.render_text_to_opengl(f"Score: {self.score}", WINDOW_WIDTH - 200, 30, self.small_font, YELLOW)
        self.render_text_to_opengl(f"Enemies: {len(self.enemy_tanks)}", WINDOW_WIDTH - 200, 60, self.small_font, RED)
        
        # Add lives text indicator
        if self.player_lives > 0:
            self.render_text_to_opengl(f"Lives: {self.player_lives}", 20, 70, self.small_font, WHITE)
        else:
            # Flash "NO LIVES" in red when dead
            if int(current_time * 4) % 2:  # Flash 4 times per second
                self.render_text_to_opengl("NO LIVES!", 20, 70, self.small_font, RED)
        
        # Crosshair
        glColor3f(*GREEN)
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        glBegin(GL_LINES)
        glVertex2f(center_x - 10, center_y)
        glVertex2f(center_x + 10, center_y)
        glVertex2f(center_x, center_y - 10)
        glVertex2f(center_x, center_y + 10)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)  # Re-enable lighting
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_filled_heart(self, x, y, size):
        """Draw a filled heart shape using triangles and circles"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Heart color (bright red with slight transparency)
        glColor4f(1.0, 0.2, 0.2, 0.9)  # Bright red with slight transparency
        
        # Heart is made of two circles and a triangle
        # The heart shape is created by:
        # 1. Two circles at the top (left and right lobes)
        # 2. A triangle at the bottom (pointy part)
        
        # Left lobe (circle)
        circle_radius = size * 0.4
        left_center_x = x + size * 0.3
        left_center_y = y + size * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(left_center_x, left_center_y)  # Center of circle
        segments = 20
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            circle_x = left_center_x + circle_radius * math.cos(angle)
            circle_y = left_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        # Right lobe (circle)
        right_center_x = x + size * 0.7
        right_center_y = y + size * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(right_center_x, right_center_y)  # Center of circle
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            circle_x = right_center_x + circle_radius * math.cos(angle)
            circle_y = right_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        # Bottom triangle (pointy part of heart)
        glBegin(GL_TRIANGLES)
        # Main triangle body
        glVertex2f(x + size * 0.1, y + size * 0.5)   # Left point
        glVertex2f(x + size * 0.9, y + size * 0.5)   # Right point
        glVertex2f(x + size * 0.5, y + size * 1.2)   # Bottom point
        glEnd()
        
        # Fill in the connection between circles and triangle
        glBegin(GL_QUADS)
        # Left connection
        glVertex2f(x + size * 0.1, y + size * 0.3)
        glVertex2f(x + size * 0.5, y + size * 0.3)
        glVertex2f(x + size * 0.5, y + size * 0.6)
        glVertex2f(x + size * 0.1, y + size * 0.6)
        
        # Right connection
        glVertex2f(x + size * 0.5, y + size * 0.3)
        glVertex2f(x + size * 0.9, y + size * 0.3)
        glVertex2f(x + size * 0.9, y + size * 0.6)
        glVertex2f(x + size * 0.5, y + size * 0.6)
        glEnd()
        
        # Add a subtle highlight/shine effect
        glColor4f(1.0, 0.6, 0.6, 0.7)  # Lighter red for highlight
        
        # Small highlight on left lobe
        highlight_radius = circle_radius * 0.3
        highlight_x = left_center_x - circle_radius * 0.3
        highlight_y = left_center_y - circle_radius * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(highlight_x, highlight_y)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            hx = highlight_x + highlight_radius * math.cos(angle)
            hy = highlight_y + highlight_radius * math.sin(angle)
            glVertex2f(hx, hy)
        glEnd()
        
        # Small highlight on right lobe
        highlight_x = right_center_x - circle_radius * 0.3
        highlight_y = right_center_y - circle_radius * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(highlight_x, highlight_y)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            hx = highlight_x + highlight_radius * math.cos(angle)
            hy = highlight_y + highlight_radius * math.sin(angle)
            glVertex2f(hx, hy)
        glEnd()
        
        # Optional: Add a subtle border/outline
        glColor4f(0.8, 0.1, 0.1, 1.0)  # Darker red for border
        glLineWidth(2.0)
        
        # Left lobe outline
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            circle_x = left_center_x + circle_radius * math.cos(angle)
            circle_y = left_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        # Right lobe outline
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            circle_x = right_center_x + circle_radius * math.cos(angle)
            circle_y = right_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        # Triangle outline
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + size * 0.1, y + size * 0.5)   # Left point
        glVertex2f(x + size * 0.9, y + size * 0.5)   # Right point
        glVertex2f(x + size * 0.5, y + size * 1.2)   # Bottom point
        glEnd()
        
        glLineWidth(1.0)  # Reset line width
        glDisable(GL_BLEND)

    def draw_pulsing_heart(self, x, y, base_size, pulse_time):
        """Draw a heart that pulses when lives are low"""
        # Pulse effect - size varies with time
        pulse_factor = 1.0 + 0.2 * math.sin(pulse_time * 8)  # Pulse 8 times per second
        size = base_size * pulse_factor
        
        # Color gets more intense when pulsing
        intensity = 0.8 + 0.2 * math.sin(pulse_time * 8)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # More intense red when pulsing
        glColor4f(intensity, 0.1, 0.1, 0.9)
        
        # Use the same heart drawing code but with variable size
        self.draw_filled_heart(x, y, size)

if __name__ == "__main__":
    game = Game()
    game.run()