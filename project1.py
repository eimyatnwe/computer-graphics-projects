import pygame
import sys
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame.font
import pygame.mixer

#Game constant
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

#Game states
GAME_STATE_INTRO = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2

#Colors
WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)
CYAN = (0.0, 1.0, 1.0)
ORANGE = (1.0,0.5,0.0)
PURPLE = (1.0,0.0,1.0)

class Vector3:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self,other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self,other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if (mag > 0):
            return Vector3(self.x/mag, self.y/mag, self.z/mag)
        return Vector3(0,0,0)
    

class GameObject:
    def __init__(self, position, color=WHITE):
        self.position = position
        self.rotation = Vector3(0,0,0)
        self.scale = Vector3(1,1,1)
        self.color = color
        self.active = True
        self.radius = 1.0 
    
    def update(self,dt):
        pass

    def render(self):
        pass


class Tank(GameObject):
    def __init__(self, position, color=GREEN, is_enemy=False ):
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
        self.ai_move_direction = random.uniform(0,360)

    def can_shoot(self,current_time):
        return current_time - self.last_shot_time >= self.shot_cooldown
    
    def shoot(self,current_time):
        if self.can_shoot(current_time):
            self.last_shot_time = current_time

            #calculate shooting direction based on tank rotation
            direction = Vector3(
                math.sin(math.radians(self.rotation.y)),
                0,
                math.cos(math.radians(self.rotation.y))
            )

            #start laser from tank barrel position
            laser_start = Vector3(
                self.position.x + direction.x * 2,
                self.position.y + 0.5,
                self.position.z + direction.z * 2
            )
            laser_color = CYAN if not self.is_enemy else RED
            owner = "enemy" if self.is_enemy else "player"
            return Laser(laser_start,direction,laser_color,owner)
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

        #Enable tank shadow first
        self.render_shadow()

        #set base tank material properties
        if self.is_enemy:
            #enemy tank
            base_color = [0.7, 0.1, 0.1]
            highlight_color = [0.9, 0.3, 0.3]
            dark_color = [0.4, 0.05, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.1, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        else:
            #player tank
            base_color = [0.1, 0.6, 0.1]
            highlight_color = [0.3, 0.8, 0.3]
            dark_color = [0.05, 0.3, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.2, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.1, 0.7, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 32.0)

        #draw tank body with depth
        glColor3f(*base_color)
        self.draw_tank_hull(1.6, 0.5, 2.4)

        #draw tank tracks
        glColor3f(*dark_color)
        self.draw_tank_tracks()

        #draw turret
        glPushMatrix()
        glTranslatef(0, 0.4, -0.2)
        glColor3f(*highlight_color)
        self.draw_tank_turret(0.8, 0.4, 0.8)

        #draw canon barrel
        glTranslatef(0, 0.15, 0.6)
        glColor3f(0.3, 0.3, 0.3)
        self.draw_tank_barrel()

        #add tank details
        glPopMatrix()
        self.draw_tank_details(base_color, dark_color)

        glPopMatrix()

    def render_shadow(self):
        #Render a simple projected shadow on the ground"""
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





    



