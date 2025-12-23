import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame.font

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
        self.radius = 1.0  
    
    def update(self, dt):
        pass
    
    def render(self):
        pass

class Tank(GameObject):
    def __init__(self, position, color=GREEN, is_enemy=False):
        super().__init__(position, color)
        self.speed = 5.0 if not is_enemy else 3.0
        self.rotation_speed = 90.0  
        self.health = 1
        self.radius = 1.5 
        self.last_shot_time = 0
        self.shot_cooldown = 0.5 if not is_enemy else 1.0  
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
        
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set base tank material properties
        if self.is_enemy:
            # Red enemy tank
            base_color = [0.7, 0.1, 0.1]
            highlight_color = [0.9, 0.3, 0.3]
            dark_color = [0.4, 0.05, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.1, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        
        # tank hull
        glColor3f(*base_color)
        self.draw_tank_hull(1.6, 0.5, 2.4)
        
        # tank tracks 
        glColor3f(*dark_color)
        self.draw_tank_tracks()
        
        # turret 
        glPushMatrix()
        glTranslatef(0, 0.4, -0.2) 
        glColor3f(*highlight_color)
        self.draw_tank_turret(0.8, 0.4, 0.8)
        
        # cannon barrel 
        glTranslatef(0, 0.15, 0.6)
        glColor3f(0.3, 0.3, 0.3)  
        self.draw_tank_barrel()
        
        # tank details
        glPopMatrix()
        self.draw_tank_details(base_color, dark_color)
        
        glPopMatrix()

    def draw_tank_hull(self, width, height, depth):
        w, h, d = width/2, height/2, depth/2
        
        # Front face 
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, d*0.8)
        glEnd()
        
        # Back face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        glEnd()
        
        # Top face (angled)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w*0.8, h, -d)
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, -d)
        glEnd()
        
        # Bottom face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        glEnd()
        
        # Connect front to back
        glBegin(GL_LINES)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, -h, -d)
        
        glVertex3f(w, -h, d)
        glVertex3f(w, -h, -d)
        
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, -d)
        
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, -d)
        glEnd()

    def draw_tank_tracks(self):
        """Draw tank tracks on both sides - WIREFRAME"""
        track_width = 0.2
        track_height = 0.3
        hull_width = 1.6
        
        for side in [-1, 1]:  
            glPushMatrix()
            glTranslatef(side * (hull_width/2 + track_width/2), -0.1, 0)
            
            # Track body
            # Front face
            glBegin(GL_LINE_LOOP)
            glVertex3f(-track_width/2, -track_height, 1.0)
            glVertex3f(track_width/2, -track_height, 1.0)
            glVertex3f(track_width/2, track_height, 1.0)
            glVertex3f(-track_width/2, track_height, 1.0)
            glEnd()
            
            # Back face
            glBegin(GL_LINE_LOOP)
            glVertex3f(-track_width/2, -track_height, -1.0)
            glVertex3f(track_width/2, -track_height, -1.0)
            glVertex3f(track_width/2, track_height, -1.0)
            glVertex3f(-track_width/2, track_height, -1.0)
            glEnd()
            
            # Connect front to back
            glBegin(GL_LINES)
            glVertex3f(-track_width/2, -track_height, 1.0)
            glVertex3f(-track_width/2, -track_height, -1.0)
            
            glVertex3f(track_width/2, -track_height, 1.0)
            glVertex3f(track_width/2, -track_height, -1.0)
            
            glVertex3f(track_width/2, track_height, 1.0)
            glVertex3f(track_width/2, track_height, -1.0)
            
            glVertex3f(-track_width/2, track_height, 1.0)
            glVertex3f(-track_width/2, track_height, -1.0)
            glEnd()
            
            # Track details 
            self.draw_track_wheels()
            
            glPopMatrix()

    def draw_track_wheels(self):
        wheel_radius = 0.15
        wheel_positions = [-0.8, -0.3, 0.2, 0.7]
        
        for pos_z in wheel_positions:
            glPushMatrix()
            glTranslatef(0, 0, pos_z)
            
            # Simple wheel 
            glBegin(GL_LINE_LOOP)
            segments = 8
            for i in range(segments):
                angle = (i / segments) * 2 * math.pi
                y = wheel_radius * math.cos(angle)
                z = wheel_radius * math.sin(angle)
                glVertex3f(0, y, z)
            glEnd()
            
            glBegin(GL_LINES)
            for i in range(4):
                angle = (i / 4) * 2 * math.pi
                y = wheel_radius * math.cos(angle)
                z = wheel_radius * math.sin(angle)
                glVertex3f(0, 0, 0)
                glVertex3f(0, y, z)
            glEnd()
            
            glPopMatrix()

    def draw_tank_turret(self, width, height, depth):
        w, h, d = width/2, height/2, depth/2
        
        # Front face (angled)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(w*0.7, -h, d)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        glEnd()
        
        # Back face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        glEnd()
        
        # Top face (rounded)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w*0.8, h, -d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(w*0.8, h, -d*0.8)
        glEnd()
        
        # Connect front to back edges
        glBegin(GL_LINES)
        # Left side
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(-w, -h, -d)
        
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(-w*0.8, h, -d*0.8)
        
        # Right side
        glVertex3f(w*0.7, -h, d)
        glVertex3f(w, -h, -d)
        
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(w*0.8, h, -d*0.8)
        glEnd()

    def draw_tank_barrel(self):
        barrel_length = 1.4
        barrel_radius = 0.08
        segments = 8
        
        # Main barrel cylinder 
        for z_pos in [0, barrel_length * 0.33, barrel_length * 0.67, barrel_length]:
            glBegin(GL_LINE_LOOP)
            for i in range(segments):
                angle = (i / segments) * 2 * math.pi
                x = barrel_radius * math.cos(angle)
                y = barrel_radius * math.sin(angle)
                glVertex3f(x, y, z_pos)
            glEnd()
        
        # Connect rings with lines along the barrel
        glBegin(GL_LINES)
        for i in range(4): 
            angle = (i / 4) * 2 * math.pi
            x = barrel_radius * math.cos(angle)
            y = barrel_radius * math.sin(angle)
            glVertex3f(x, y, 0)
            glVertex3f(x, y, barrel_length)
        glEnd()
        
        # Muzzle brake 
        glPushMatrix()
        glTranslatef(0, 0, barrel_length - 0.1)
        brake_radius = barrel_radius * 1.2
        
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = brake_radius * math.cos(angle)
            y = brake_radius * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = brake_radius * math.cos(angle)
            y = brake_radius * math.sin(angle)
            glVertex3f(x, y, 0.1)
        glEnd()
        
        glPopMatrix()

    def draw_tank_details(self, base_color, dark_color):
        # Commander hatch
        glPushMatrix()
        glTranslatef(-0.2, 0.8, -0.3)
        glColor3f(*dark_color)
        glScalef(0.3, 0.05, 0.3)
        self.draw_wireframe_cube(1, 1, 1)
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
            self.draw_wireframe_cube(1, 1, 1)
            glPopMatrix()

    def draw_wireframe_cube(self, width, height, depth):
        w, h, d = width/2, height/2, depth/2
        
        # Front face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        glEnd()
        
        # Back face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(-w, h, -d)
        glEnd()
        
        # Connect front to back
        glBegin(GL_LINES)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, -h, -d)
        
        glVertex3f(w, -h, d)
        glVertex3f(w, -h, -d)
        
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()

class Mountain(GameObject):
    def __init__(self, position, color=WHITE):
        super().__init__(position, color)
        self.radius = 1.2  
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # white/light gray color for wireframe mountains
        glColor3f(0.9, 0.9, 0.9) 
        
        # wireframe pyramid
        base = 2.0
        peak_height = 2.8
        
        # base 
        glBegin(GL_LINE_LOOP)
        glVertex3f(-base, 0, -base)
        glVertex3f(base, 0, -base)
        glVertex3f(base, 0, base)
        glVertex3f(-base, 0, base)
        glEnd()
        
        # Draw edges from base corners to peak
        glBegin(GL_LINES)
        # Front left to peak
        glVertex3f(-base, 0, base)
        glVertex3f(0, peak_height, 0)
        
        # Front right to peak
        glVertex3f(base, 0, base)
        glVertex3f(0, peak_height, 0)
        
        # Back right to peak
        glVertex3f(base, 0, -base)
        glVertex3f(0, peak_height, 0)
        
        # Back left to peak
        glVertex3f(-base, 0, -base)
        glVertex3f(0, peak_height, 0)
        glEnd()
        
        glPopMatrix()

class LifeSphere(GameObject):
    def __init__(self, position, color=YELLOW):
        super().__init__(position, color)
        self.radius = 0.35  
        self.bob_time = 0
        self.original_y = position.y
    
    def update(self, dt):
        self.bob_time += dt * 2
        self.position.y = self.original_y + math.sin(self.bob_time) * 0.2  
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
      
        glColor3f(1.0, 1.0, 0.2)  # Bright yellow
        
        #wireframe sphere using latitude and longitude lines
        radius = 0.35
        stacks = 8
        slices = 8
        
        # horizontal circles
        for i in range(stacks + 1):
            lat = math.pi * (-0.5 + float(i) / stacks)
            z = radius * math.sin(lat)
            zr = radius * math.cos(lat)
            
            glBegin(GL_LINE_LOOP)
            for j in range(slices):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng) * zr
                y = math.sin(lng) * zr
                glVertex3f(x, z, y)
            glEnd()
        
        # vertical circles
        for j in range(slices):
            lng = 2 * math.pi * float(j) / slices
            
            glBegin(GL_LINE_STRIP)
            for i in range(stacks + 1):
                lat = math.pi * (-0.5 + float(i) / stacks)
                z = radius * math.sin(lat)
                zr = radius * math.cos(lat)
                x = math.cos(lng) * zr
                y = math.sin(lng) * zr
                glVertex3f(x, z, y)
            glEnd()
        
        glPopMatrix()

class Laser(GameObject):
    def __init__(self, position, direction, color=CYAN, owner="player"):
        super().__init__(position, color)
        self.direction = direction
        self.speed = 20.0
        self.radius = 0.15 
        self.lifetime = 3.0  
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
        
        if self.owner == "player":
            # Cyan laser
            glColor3f(0.2, 1.0, 1.0)
        else:
            # Red laser
            glColor3f(1.0, 0.2, 0.2)
        
        glScalef(0.1, 0.1, 0.7)
        
        # Front face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, 1)
        glEnd()
        
        # Back face
        glBegin(GL_LINE_LOOP)
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(-1, 1, -1)
        glEnd()
        
        # Connect front to back edges
        glBegin(GL_LINES)
        glVertex3f(-1, -1, 1)
        glVertex3f(-1, -1, -1)
        
        glVertex3f(1, -1, 1)
        glVertex3f(1, -1, -1)
        
        glVertex3f(1, 1, 1)
        glVertex3f(1, 1, -1)
        
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, 1, -1)
        glEnd()
        
        glPopMatrix()

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Arctic Tank 3D")
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize OpenGL with better lighting
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)  
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE) 
        glEnable(GL_BLEND)
        
        # background color (dark blue sky)
        glClearColor(0.05, 0.05, 0.2, 1.0)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.02, 0.02, 0.05, 1])
    
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (WINDOW_WIDTH/WINDOW_HEIGHT), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GAME_STATE_INTRO
        self.player_lives = 3
        self.score = 0
   
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 3.0  
        self.max_enemies = 5  
        
        # Initialize game objects
        self.init_game_objects()
        
        self.camera_pos = Vector3(0, 5, 10)
        self.camera_target = Vector3(0, 0, 0)
        
        # Intro animation
        self.intro_rotation = 0

    def init_game_objects(self):
        self.player_position = Vector3(0, 0, 0)
        self.player_rotation_y = 0  
        self.player_speed = 5.0
        self.player_rotation_speed = 90.0
        self.player_radius = 1.0  
        self.last_shot_time = 0
        self.shot_cooldown = 0.5
        
        # Screen shake/flash effects
        self.screen_shake_time = 0
        self.screen_shake_intensity = 0
        self.red_flash_time = 0
        self.red_flash_intensity = 0
        
        self.enemy_tanks = []
        
        # many more mountains scattered across a larger area
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
            # Spawn enemy at random position around the player 
            player_pos = self.player_position
            
            # random spawn method
            spawn_method = random.choice(['circle', 'forward', 'sides'])
            
            if spawn_method == 'circle':
                # Spawn in a circle around player
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(15, 30)
                spawn_x = player_pos.x + math.cos(angle) * distance
                spawn_z = player_pos.z + math.sin(angle) * distance
            
            elif spawn_method == 'forward':
                # Spawn ahead of player's movement direction
                player_direction = math.radians(self.player_rotation_y)
                forward_distance = random.uniform(20, 40)
                side_offset = random.uniform(-15, 15)
                
                spawn_x = player_pos.x + math.sin(player_direction) * forward_distance + side_offset
                spawn_z = player_pos.z + math.cos(player_direction) * forward_distance + side_offset
            
            else:  # sides
                # Spawn to the sides of player
                side = random.choice([-1, 1])
                side_distance = random.uniform(20, 35)
                forward_offset = random.uniform(-10, 20)
                
                player_direction = math.radians(self.player_rotation_y)
               
                perp_direction = player_direction + (math.pi/2 * side)
                
                spawn_x = player_pos.x + math.sin(perp_direction) * side_distance + math.sin(player_direction) * forward_offset
                spawn_z = player_pos.z + math.cos(perp_direction) * side_distance + math.cos(player_direction) * forward_offset
            
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
                elif self.game_state == GAME_STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        # Restart game
                        self.game_state = GAME_STATE_PLAYING
                        self.player_lives = 3
                        self.score = 0
                        self.init_game_objects()
    
    def update_intro(self, dt):
        self.intro_rotation += dt * 30  
    
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            # Move forward
            forward_x = math.sin(math.radians(self.player_rotation_y))
            forward_z = math.cos(math.radians(self.player_rotation_y))
            self.player_position.x += forward_x * self.player_speed * dt
            self.player_position.z += forward_z * self.player_speed * dt
        
        if keys[pygame.K_s]:
            # Move backward
            forward_x = math.sin(math.radians(self.player_rotation_y))
            forward_z = math.cos(math.radians(self.player_rotation_y))
            self.player_position.x -= forward_x * self.player_speed * dt
            self.player_position.z -= forward_z * self.player_speed * dt
        
        if keys[pygame.K_a]:
            self.player_rotation_y += self.player_rotation_speed * dt
        
        if keys[pygame.K_d]:
            self.player_rotation_y -= self.player_rotation_speed * dt
    
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_shot_time >= self.shot_cooldown:
                self.last_shot_time = current_time
                
                # Calculate shooting direction based on camera rotation
                direction = Vector3(
                    math.sin(math.radians(self.player_rotation_y)),
                    -0.1,
                    math.cos(math.radians(self.player_rotation_y))
                )
                # Normalize the direction
                direction = direction.normalize()
                
                # Start laser from camera position
                laser_start = Vector3(
                    self.player_position.x + direction.x * 1,
                    self.player_position.y + 1.5, 
                    self.player_position.z + direction.z * 1
                )
                
                laser = Laser(laser_start, direction, CYAN, "player")
                self.lasers.append(laser)
        
        # Update camera to follow player position
        self.update_camera()
    
    def update_camera(self):
        camera_height = 1.8  
        
        self.camera_pos = Vector3(
            self.player_position.x, 
            self.player_position.y + camera_height, 
            self.player_position.z
        )
        
        look_direction = Vector3(
            math.sin(math.radians(self.player_rotation_y)),
            0,
            math.cos(math.radians(self.player_rotation_y))
        )
        
        self.camera_target = Vector3(
            self.camera_pos.x + look_direction.x,
            self.camera_pos.y,
            self.camera_pos.z + look_direction.z
        )
    
    def update_game(self, dt):
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            self.enemy_spawn_interval = max(2.0, self.enemy_spawn_interval - 0.05)  # Faster decrease
        
        # screen shaking when collide with mountain
        if self.screen_shake_time > 0:
            self.screen_shake_time -= dt
        if self.red_flash_time > 0:
            self.red_flash_time -= dt
            
        self.ensure_enemies_nearby()
    
        
        for enemy in self.enemy_tanks:
            enemy.update(dt)
            current_time = pygame.time.get_ticks() / 1000.0
            if random.random() < 0.01: 
                laser = enemy.shoot(current_time)
                if laser:
                    self.lasers.append(laser)
        
        for sphere in self.life_spheres:
            sphere.update(dt)
        
        for laser in self.lasers[:]:
            laser.update(dt)
            if not laser.active:
                self.lasers.remove(laser)
        
        self.check_collisions()
        
        if self.player_lives <= 0:
            self.game_state = GAME_STATE_GAME_OVER
    
    def ensure_enemies_nearby(self):
        if len(self.enemy_tanks) < 2: 
            self.spawn_enemy()
            
        player_pos = self.player_position
        closest_enemy_distance = float('inf')
        
        for enemy in self.enemy_tanks:
            dist = self.distance(player_pos, enemy.position)
            closest_enemy_distance = min(closest_enemy_distance, dist)
        
        if closest_enemy_distance > 25:  
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(12, 20)  
            spawn_x = player_pos.x + math.cos(angle) * distance
            spawn_z = player_pos.z + math.sin(angle) * distance
            
            new_enemy = Tank(Vector3(spawn_x, 0, spawn_z), RED, is_enemy=True)
            self.enemy_tanks.append(new_enemy)
            print(f"Close enemy spawned at ({spawn_x:.1f}, 0, {spawn_z:.1f})")
    
    def check_collisions(self):
        for sphere in self.life_spheres[:]:
            if self.distance(self.player_position, sphere.position) < (self.player_radius + sphere.radius):
                self.life_spheres.remove(sphere)
                self.player_lives += 1
                self.score += 5
                print(f"Life sphere collected! Lives: {self.player_lives}")
        
        for laser in self.lasers[:]:
            if laser.owner == "player":
                for enemy in self.enemy_tanks[:]:
                    if self.distance(laser.position, enemy.position) < (laser.radius + enemy.radius):
                        self.lasers.remove(laser)
                        self.enemy_tanks.remove(enemy)
                        self.score += 10
                        print(f"Enemy destroyed! Score: {self.score}")
                        break
        
        # Check laser-player collisions
        for laser in self.lasers[:]:
            if laser.owner == "enemy":
                if self.distance(laser.position, self.player_position) < (laser.radius + self.player_radius):
                    # Player hit by enemy laser
                    self.lasers.remove(laser)
                    self.player_lives -= 1
                    print(f"Player hit by laser! Lives remaining: {self.player_lives}")
        
        # Check laser-mountain collisions 
        for laser in self.lasers[:]:
            for mountain in self.mountains:
                if self.distance(laser.position, mountain.position) < (laser.radius + mountain.radius):
                    self.lasers.remove(laser)
                    print("Laser blocked by mountain!")
                    break
        
        # Check player-mountain collisions
        for mountain in self.mountains:
            if self.distance(self.player_position, mountain.position) < (self.player_radius + mountain.radius):
                # Player loses a life when hitting mountain
                self.player_lives -= 1
                print(f"Player hit mountain! Lives remaining: {self.player_lives}")
                
                # Trigger screen shake 
                self.screen_shake_time = 0.5  
                self.screen_shake_intensity = 20 
                self.red_flash_time = 0.3  
                self.red_flash_intensity = 0.6  
                
                # Push back player
                direction = Vector3(
                    self.player_position.x - mountain.position.x,
                    0,
                    self.player_position.z - mountain.position.z
                )
                distance = direction.magnitude()
                if distance > 0:
                    direction.x /= distance
                    direction.z /= distance
                  
                    push_distance = (self.player_radius + mountain.radius) - distance + 0.5
                   
                    self.player_position.x += direction.x * push_distance
                    self.player_position.z += direction.z * push_distance
                
                break 
    
    def distance(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)
    
    #rendering for intro page
    def render_intro(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1) 
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        self.draw_animated_background_simple()
        
        self.render_text_to_opengl("ARCTIC TANK", WINDOW_WIDTH//2 - 150, 100, self.title_font, CYAN)
        self.render_text_to_opengl("3D WIREFRAME", WINDOW_WIDTH//2 - 120, 180, self.large_font, WHITE)
        
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
        
        start_color = ORANGE
        if int(pygame.time.get_ticks() / 500) % 2:
            start_color = RED
        
        self.render_text_to_opengl("Press ENTER or SPACE to start", WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT - 100, self.medium_font, start_color)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)  
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def render_text_to_opengl(self, text, x, y, font, color):
        text_surface = font.render(text, True, (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glRasterPos2f(x, y)
        
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
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
        glDisable(GL_LIGHTING)
        
        glEnable(GL_FOG)
        glFogf(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
        glFogfv(GL_FOG_COLOR, [0.05, 0.05, 0.2, 1.0])
        
        gluLookAt(self.camera_pos.x, self.camera_pos.y, self.camera_pos.z,
                  self.camera_target.x, self.camera_target.y, self.camera_target.z,
                  0, 1, 0)
        
        #render all game objs
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
        glEnable(GL_LIGHTING) 
        self.render_hud()
    
    def render_game_over(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
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
        glDisable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)  
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        if self.red_flash_time > 0:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            fade = self.red_flash_time / 0.3  
            alpha = self.red_flash_intensity * fade
            glColor4f(1.0, 0.0, 0.0, alpha) 
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(WINDOW_WIDTH, 0)
            glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
            glVertex2f(0, WINDOW_HEIGHT)
            glEnd()
            glDisable(GL_BLEND)
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        for i in range(self.player_lives):
            x = 20 + i * 40 
            y = 25
            
            if self.player_lives <= 1:
                # Pulse when only 1 life left (critical health)
                self.draw_pulsing_heart(x, y, 15, current_time)
            else:
                # Normal heart
                self.draw_filled_heart(x, y, 15)
  
        self.render_text_to_opengl(f"Score: {self.score}", WINDOW_WIDTH - 200, 30, self.small_font, YELLOW)
        self.render_text_to_opengl(f"Enemies: {len(self.enemy_tanks)}", WINDOW_WIDTH - 200, 60, self.small_font, RED)
        
        if self.player_lives > 0:
            self.render_text_to_opengl(f"Lives: {self.player_lives}", 20, 70, self.small_font, WHITE)
        else:
            if int(current_time * 4) % 2:
                self.render_text_to_opengl("NO LIVES!", 20, 70, self.small_font, RED)
        
        self.draw_sniper_scope()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)  
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_sniper_scope(self):
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100  # Moved down by 100 pixels
        
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake_time > 0:
            import random
            shake_fade = self.screen_shake_time / 0.5
            current_intensity = self.screen_shake_intensity * shake_fade
            shake_offset_x = random.uniform(-current_intensity, current_intensity)
            shake_offset_y = random.uniform(-current_intensity, current_intensity)
            center_x += shake_offset_x
            center_y += shake_offset_y
        
        outer_radius = 150
        glColor3f(0.0, 1.0, 0.0)  
        glLineWidth(2.0)
        
        segments = 60
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center_x + outer_radius * math.cos(angle)
            y = center_y + outer_radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        # inner circle (smaller)
        inner_radius = 10
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        # crosshair lines 
        glLineWidth(1.5)
        glBegin(GL_LINES)
        # Horizontal line (left)
        glVertex2f(center_x - outer_radius, center_y)
        glVertex2f(center_x - inner_radius, center_y)
        # Horizontal line (right)
        glVertex2f(center_x + inner_radius, center_y)
        glVertex2f(center_x + outer_radius, center_y)
        # Vertical line (top)
        glVertex2f(center_x, center_y - outer_radius)
        glVertex2f(center_x, center_y - inner_radius)
        # Vertical line (bottom)
        glVertex2f(center_x, center_y + inner_radius)
        glVertex2f(center_x, center_y + outer_radius)
        glEnd()
        
        # tick marks for distance measurement
        tick_length = 15
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for i in range(4):
            angle = (i / 4) * 2 * math.pi
            for dist in [50, 100]:
                x1 = center_x + dist * math.cos(angle)
                y1 = center_y + dist * math.sin(angle)
                x2 = center_x + (dist + tick_length) * math.cos(angle)
                y2 = center_y + (dist + tick_length) * math.sin(angle)
                glVertex2f(x1, y1)
                glVertex2f(x2, y2)
        glEnd()
        
        # diagonal lines for mil-dot style
        glLineWidth(1.0)
        glBegin(GL_LINES)
        # Top-left to center
        glVertex2f(center_x - outer_radius * 0.7, center_y - outer_radius * 0.7)
        glVertex2f(center_x - 20, center_y - 20)
        # Top-right to center
        glVertex2f(center_x + outer_radius * 0.7, center_y - outer_radius * 0.7)
        glVertex2f(center_x + 20, center_y - 20)
        # Bottom-left to center
        glVertex2f(center_x - outer_radius * 0.7, center_y + outer_radius * 0.7)
        glVertex2f(center_x - 20, center_y + 20)
        # Bottom-right to center
        glVertex2f(center_x + outer_radius * 0.7, center_y + outer_radius * 0.7)
        glVertex2f(center_x + 20, center_y + 20)
        glEnd()
        
        dot_radius = 2
        dot_spacing = 25
        for direction in [-1, 1]:
            for mult in range(1, 5):
                glBegin(GL_TRIANGLE_FAN)
                dot_x = center_x + direction * (inner_radius + dot_spacing * mult)
                dot_y = center_y
                glVertex2f(dot_x, dot_y)
                for i in range(segments + 1):
                    angle = (i / segments) * 2 * math.pi
                    x = dot_x + dot_radius * math.cos(angle)
                    y = dot_y + dot_radius * math.sin(angle)
                    glVertex2f(x, y)
                glEnd()

                glBegin(GL_TRIANGLE_FAN)
                dot_x = center_x
                dot_y = center_y + direction * (inner_radius + dot_spacing * mult)
                glVertex2f(dot_x, dot_y)
                for i in range(segments + 1):
                    angle = (i / segments) * 2 * math.pi
                    x = dot_x + dot_radius * math.cos(angle)
                    y = dot_y + dot_radius * math.sin(angle)
                    glVertex2f(x, y)
                glEnd()
        
        glLineWidth(1.0)  

    def draw_filled_heart(self, x, y, size):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(1.0, 0.2, 0.2, 0.9) 
        
        # Heart is made of two circles and a triangle
        # The heart shape is created by:
        # two circles at the top (left and right lobes)
        # a triangle at the bottom (pointy part)
        
        circle_radius = size * 0.4
        left_center_x = x + size * 0.3
        left_center_y = y + size * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(left_center_x, left_center_y)  
        segments = 20
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            circle_x = left_center_x + circle_radius * math.cos(angle)
            circle_y = left_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        right_center_x = x + size * 0.7
        right_center_y = y + size * 0.3
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(right_center_x, right_center_y)  
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            circle_x = right_center_x + circle_radius * math.cos(angle)
            circle_y = right_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        # bottom triangle 
        glBegin(GL_TRIANGLES)
        # Main triangle body
        glVertex2f(x + size * 0.1, y + size * 0.5)  
        glVertex2f(x + size * 0.9, y + size * 0.5)   
        glVertex2f(x + size * 0.5, y + size * 1.2)   
        glEnd()
        
        # fill in the connection between circles and triangle
        glBegin(GL_QUADS)
        glVertex2f(x + size * 0.1, y + size * 0.3)
        glVertex2f(x + size * 0.5, y + size * 0.3)
        glVertex2f(x + size * 0.5, y + size * 0.6)
        glVertex2f(x + size * 0.1, y + size * 0.6)
        
        glVertex2f(x + size * 0.5, y + size * 0.3)
        glVertex2f(x + size * 0.9, y + size * 0.3)
        glVertex2f(x + size * 0.9, y + size * 0.6)
        glVertex2f(x + size * 0.5, y + size * 0.6)
        glEnd()
        
        glColor4f(1.0, 0.6, 0.6, 0.7)  
        
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
        
       
        glColor4f(0.8, 0.1, 0.1, 1.0) 
        glLineWidth(2.0)
        
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            circle_x = left_center_x + circle_radius * math.cos(angle)
            circle_y = left_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            circle_x = right_center_x + circle_radius * math.cos(angle)
            circle_y = right_center_y + circle_radius * math.sin(angle)
            glVertex2f(circle_x, circle_y)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + size * 0.1, y + size * 0.5)   
        glVertex2f(x + size * 0.9, y + size * 0.5)   
        glVertex2f(x + size * 0.5, y + size * 1.2)  
        glEnd()
        
        glLineWidth(1.0)  
        glDisable(GL_BLEND)

    def draw_pulsing_heart(self, x, y, base_size, pulse_time):
        pulse_factor = 1.0 + 0.2 * math.sin(pulse_time * 8)  
        size = base_size * pulse_factor
        
        intensity = 0.8 + 0.2 * math.sin(pulse_time * 8)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(intensity, 0.1, 0.1, 0.9)
        self.draw_filled_heart(x, y, size)

if __name__ == "__main__":
    game = Game()
    game.run()