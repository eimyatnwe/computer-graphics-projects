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

# Colors
WHITE = (1.0, 1.0, 1.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)
CYAN = (0.0, 1.0, 1.0)
ORANGE = (1.0, 0.5, 0.0)
PURPLE = (1.0, 0.0, 1.0)

# Material class for different surface properties
class Material:
    def __init__(self, name, ambient, diffuse, specular, shininess, alpha=1.0):
        self.name = name
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.alpha = alpha 
    
    def apply(self):
        """Apply this material to current OpenGL state
        
        Properly handles transparency with:
        - Alpha blending enabled for transparent materials (alpha < 1.0)
        - Depth writing disabled (glDepthMask(GL_FALSE)) to prevent depth artifacts
        - Standard blend function: SRC_ALPHA, ONE_MINUS_SRC_ALPHA
        """
        # Set material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.ambient + [self.alpha])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse + [self.alpha])
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular + [self.alpha])
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
        
        # Handle transparency correctly to avoid depth artifacts
        if self.alpha < 1.0:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  
            glDepthMask(GL_FALSE)  # Disable depth writing for transparent objects
        else:
            glDepthMask(GL_TRUE)  # Re-enable depth writing for opaque objects

# Predefined materials
class Materials:
    # Opaque Matte Materials 
    MATTE_WHITE = Material(
        "Matte White",
        ambient=[0.2, 0.2, 0.2],
        diffuse=[0.9, 0.9, 0.9],
        specular=[0.1, 0.1, 0.1],
        shininess=8.0
    )
    
    MATTE_RED = Material(
        "Matte Red",
        ambient=[0.2, 0.0, 0.0],
        diffuse=[0.8, 0.1, 0.1],
        specular=[0.1, 0.1, 0.1],
        shininess=8.0
    )
    
    MATTE_GREEN = Material(
        "Matte Green",
        ambient=[0.0, 0.2, 0.0],
        diffuse=[0.1, 0.7, 0.1],
        specular=[0.1, 0.1, 0.1],
        shininess=8.0
    )
    
    MATTE_GRAY = Material(
        "Matte Gray",
        ambient=[0.2, 0.2, 0.2],
        diffuse=[0.5, 0.5, 0.5],
        specular=[0.05, 0.05, 0.05],
        shininess=4.0
    )
    
    # Opaque Glossy Materials
    METALLIC_SILVER = Material(
        "Metallic Silver",
        ambient=[0.2, 0.2, 0.25],
        diffuse=[0.4, 0.4, 0.5],
        specular=[1.0, 1.0, 1.0],
        shininess=128.0
    )
    
    METALLIC_GOLD = Material(
        "Metallic Gold",
        ambient=[0.25, 0.2, 0.07],
        diffuse=[0.75, 0.6, 0.23],
        specular=[1.0, 0.9, 0.5],
        shininess=96.0
    )
    
    GLOSSY_PLASTIC_RED = Material(
        "Glossy Plastic Red",
        ambient=[0.2, 0.0, 0.0],
        diffuse=[0.8, 0.1, 0.1],
        specular=[0.9, 0.9, 0.9],
        shininess=64.0
    )
    
    GLOSSY_PLASTIC_GREEN = Material(
        "Glossy Plastic Green",
        ambient=[0.0, 0.2, 0.0],
        diffuse=[0.1, 0.7, 0.1],
        specular=[0.9, 0.9, 0.9],
        shininess=64.0
    )
    
    # Glass Materials 
    GLASS_CLEAR = Material(
        "Clear Glass",
        ambient=[0.2, 0.2, 0.3],
        diffuse=[0.5, 0.5, 0.6],
        specular=[1.0, 1.0, 1.0],
        shininess=128.0,
        alpha=0.3
    )
    
    GLASS_BLUE = Material(
        "Blue Glass",
        ambient=[0.0, 0.1, 0.3],
        diffuse=[0.1, 0.3, 0.8],
        specular=[1.0, 1.0, 1.0],
        shininess=128.0,
        alpha=0.4
    )
    
    GLASS_GREEN = Material(
        "Green Glass",
        ambient=[0.0, 0.2, 0.1],
        diffuse=[0.1, 0.7, 0.3],
        specular=[1.0, 1.0, 1.0],
        shininess=128.0,
        alpha=0.4
    )
    
    GLASS_RED = Material(
        "Red Glass",
        ambient=[0.2, 0.0, 0.0],
        diffuse=[0.8, 0.1, 0.1],
        specular=[1.0, 1.0, 1.0],
        shininess=128.0,
        alpha=0.4
    )
    
    # Specialized materials
    SNOW = Material(
        "Snow/Ice",
        ambient=[0.8, 0.8, 0.9],
        diffuse=[0.95, 0.95, 1.0],
        specular=[1.0, 1.0, 1.0],
        shininess=96.0
    )
    
    ROCK = Material(
        "Rock",
        ambient=[0.3, 0.3, 0.35],
        diffuse=[0.7, 0.7, 0.75],
        specular=[0.4, 0.4, 0.45],
        shininess=16.0
    )
    
    WOOD = Material(
        "Wood",
        ambient=[0.2, 0.1, 0.05],
        diffuse=[0.4, 0.25, 0.15],
        specular=[0.1, 0.1, 0.1],
        shininess=8.0
    )
    
    FOLIAGE = Material(
        "Foliage",
        ambient=[0.0, 0.15, 0.0],
        diffuse=[0.1, 0.5, 0.1],
        specular=[0.2, 0.6, 0.2],
        shininess=32.0
    )

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

class Explosion(GameObject):
    def __init__(self, position, color=ORANGE):
        super().__init__(position, color)
        self.lifetime = 0.5
        self.age = 0
        self.max_size = 2.0
        self.radius = 0.5
        
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
        
        # Grow explosion
        growth_rate = self.max_size / self.lifetime
        self.scale.x = self.scale.y = self.scale.z = self.age * growth_rate
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glScalef(self.scale.x, self.scale.y, self.scale.z)
        
        # Enable additive blending for explosion
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)
        
        # Emissive material for explosion
        alpha = 1.0 - (self.age / self.lifetime)
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 0.5, 0.0, alpha])
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.0, 0.0, alpha])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.6, 0.1, alpha])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 0.0, alpha])
        glMaterialf(GL_FRONT, GL_SHININESS, 32.0)
        
        glColor4f(1.0, 0.5 + (1.0 - alpha) * 0.5, 0.0, alpha)
        
        # Draw explosion as expanding sphere
        segments = 12
        for i in range(segments):
            lat1 = (i / segments) * math.pi
            lat2 = ((i + 1) / segments) * math.pi
            
            for j in range(segments * 2):
                lon1 = (j / (segments * 2)) * 2 * math.pi
                lon2 = ((j + 1) / (segments * 2)) * 2 * math.pi
                
                # Calculate vertices
                x1 = math.sin(lat1) * math.cos(lon1)
                y1 = math.cos(lat1)
                z1 = math.sin(lat1) * math.sin(lon1)
                
                x2 = math.sin(lat1) * math.cos(lon2)
                y2 = math.cos(lat1)
                z2 = math.sin(lat1) * math.sin(lon2)
                
                x3 = math.sin(lat2) * math.cos(lon2)
                y3 = math.cos(lat2)
                z3 = math.sin(lat2) * math.sin(lon2)
                
                x4 = math.sin(lat2) * math.cos(lon1)
                y4 = math.cos(lat2)
                z4 = math.sin(lat2) * math.sin(lon1)
                
                glBegin(GL_QUADS)
                glNormal3f(x1, y1, z1)
                glVertex3f(x1, y1, z1)
                glNormal3f(x2, y2, z2)
                glVertex3f(x2, y2, z2)
                glNormal3f(x3, y3, z3)
                glVertex3f(x3, y3, z3)
                glNormal3f(x4, y4, z4)
                glVertex3f(x4, y4, z4)
                glEnd()
        
        # Reset emission
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPopMatrix()

class Mountain(GameObject):
    def __init__(self, position, size, color=WHITE):
        super().__init__(position, color)
        self.size = size
        self.radius = size * 0.7
        self.material = Materials.MATTE_GREEN  # Matte material
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        self.material.apply()
        glColor3f(0.2, 0.5, 0.2)
        
        height = self.size
        base = self.size * 0.8
        
        # Mountains
        # Front face
        glBegin(GL_TRIANGLES)
        glNormal3f(0, 0.7, 0.7)
        glVertex3f(0, height, 0)
        glVertex3f(-base, 0, base)
        glVertex3f(base, 0, base)
        glEnd()
        
        # Right face
        glBegin(GL_TRIANGLES)
        glNormal3f(0.7, 0.7, 0)
        glVertex3f(0, height, 0)
        glVertex3f(base, 0, base)
        glVertex3f(base, 0, -base)
        glEnd()
        
        # Back face
        glBegin(GL_TRIANGLES)
        glNormal3f(0, 0.7, -0.7)
        glVertex3f(0, height, 0)
        glVertex3f(base, 0, -base)
        glVertex3f(-base, 0, -base)
        glEnd()
        
        # Left face
        glBegin(GL_TRIANGLES)
        glNormal3f(-0.7, 0.7, 0)
        glVertex3f(0, height, 0)
        glVertex3f(-base, 0, -base)
        glVertex3f(-base, 0, base)
        glEnd()
        
        # Base 
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glVertex3f(-base, 0, base)
        glVertex3f(base, 0, base)
        glVertex3f(base, 0, -base)
        glVertex3f(-base, 0, -base)
        glEnd()
        
        # Add snow cap on top with different material
        glPushMatrix()
        glTranslatef(0, height * 0.7, 0)

        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.3, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.4, 0.6, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.4, 0.2, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 16.0)
        glColor3f(0.35, 0.55, 0.2)  # Lighter yellow-green for peak
        
        peak_height = height * 0.3
        peak_base = base * 0.4

        glBegin(GL_TRIANGLES)
        glNormal3f(0, 0.7, 0.7)
        glVertex3f(0, peak_height, 0)
        glVertex3f(-peak_base, 0, peak_base)
        glVertex3f(peak_base, 0, peak_base)
        
        glNormal3f(0.7, 0.7, 0)
        glVertex3f(0, peak_height, 0)
        glVertex3f(peak_base, 0, peak_base)
        glVertex3f(peak_base, 0, -peak_base)
        
        glNormal3f(0, 0.7, -0.7)
        glVertex3f(0, peak_height, 0)
        glVertex3f(peak_base, 0, -peak_base)
        glVertex3f(-peak_base, 0, -peak_base)
        
        glNormal3f(-0.7, 0.7, 0)
        glVertex3f(0, peak_height, 0)
        glVertex3f(-peak_base, 0, -peak_base)
        glVertex3f(-peak_base, 0, peak_base)
        glEnd()
        
        glPopMatrix()
        glPopMatrix()

       
        

class Tree(GameObject):
    def __init__(self, position, color=GREEN):
        super().__init__(position, color)
        self.radius = 0.5
        self.trunk_material = Materials.WOOD  
        self.foliage_material = Materials.FOLIAGE  
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Apply trunk material
        self.trunk_material.apply()
        glColor3f(0.4, 0.25, 0.15)
        
        # Trunk (cylinder)
        trunk_height = 1.0
        trunk_radius = 0.1
        segments = 8
        
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            x1 = trunk_radius * math.cos(angle1)
            z1 = trunk_radius * math.sin(angle1)
            x2 = trunk_radius * math.cos(angle2)
            z2 = trunk_radius * math.sin(angle2)
            
            nx = (math.cos(angle1) + math.cos(angle2)) / 2
            nz = (math.sin(angle1) + math.sin(angle2)) / 2
            
            glBegin(GL_QUADS)
            glNormal3f(nx, 0, nz)
            glVertex3f(x1, 0, z1)
            glVertex3f(x2, 0, z2)
            glVertex3f(x2, trunk_height, z2)
            glVertex3f(x1, trunk_height, z1)
            glEnd()
        
        # Foliage material - dark green, slightly shiny
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.15, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.1, 0.5, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.6, 0.2, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 32.0)
        glColor3f(0.1, 0.5, 0.1)
        
        # Foliage (3 cone layers)
        for layer in range(3):
            glPushMatrix()
            glTranslatef(0, trunk_height + layer * 0.3, 0)
            
            cone_base = 0.6 - layer * 0.15
            cone_height = 0.5
            
            for i in range(segments):
                angle1 = (i / segments) * 2 * math.pi
                angle2 = ((i + 1) / segments) * 2 * math.pi
                
                x1 = cone_base * math.cos(angle1)
                z1 = cone_base * math.sin(angle1)
                x2 = cone_base * math.cos(angle2)
                z2 = cone_base * math.sin(angle2)
                
                # Normal calculation for cone
                nx1 = math.cos(angle1)
                nz1 = math.sin(angle1)
                nx2 = math.cos(angle2)
                nz2 = math.sin(angle2)
                
                glBegin(GL_TRIANGLES)
                glNormal3f((nx1 + nx2) / 2, 0.5, (nz1 + nz2) / 2)
                glVertex3f(0, cone_height, 0)
                glVertex3f(x1, 0, z1)
                glVertex3f(x2, 0, z2)
                glEnd()
            
            glPopMatrix()
        
        glPopMatrix()

class ColorSphere(GameObject):
    def __init__(self, position, color):
        super().__init__(position, color)
        self.radius = 0.5
        self.rotation_speed = Vector3(
            random.uniform(10, 30),
            random.uniform(10, 30),
            random.uniform(10, 30)
        )
        
        # Assign glass material based on color
        if color == RED:
            self.material = Materials.GLASS_RED
        elif color == BLUE:
            self.material = Materials.GLASS_BLUE
        elif color == GREEN:
            self.material = Materials.GLASS_GREEN
        else:
            self.material = Materials.GLASS_CLEAR
        
    def update(self, dt):
        self.rotation.x += self.rotation_speed.x * dt
        self.rotation.y += self.rotation_speed.y * dt
        self.rotation.z += self.rotation_speed.z * dt
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y + 0.5, self.position.z)
        glRotatef(self.rotation.x, 1, 0, 0)
        glRotatef(self.rotation.y, 0, 1, 0)
        glRotatef(self.rotation.z, 0, 0, 1)
        
        # Apply glass material (transparent with high specular)
        self.material.apply()
        glColor4f(self.color[0], self.color[1], self.color[2], self.material.alpha)
        
        # Draw sphere
        segments = 16
        for i in range(segments):
            lat1 = (i / segments) * math.pi
            lat2 = ((i + 1) / segments) * math.pi
            
            for j in range(segments * 2):
                lon1 = (j / (segments * 2)) * 2 * math.pi
                lon2 = ((j + 1) / (segments * 2)) * 2 * math.pi
                
                # Calculate vertices and normals
                x1 = self.radius * math.sin(lat1) * math.cos(lon1)
                y1 = self.radius * math.cos(lat1)
                z1 = self.radius * math.sin(lat1) * math.sin(lon1)
                
                x2 = self.radius * math.sin(lat1) * math.cos(lon2)
                y2 = self.radius * math.cos(lat1)
                z2 = self.radius * math.sin(lat1) * math.sin(lon2)
                
                x3 = self.radius * math.sin(lat2) * math.cos(lon2)
                y3 = self.radius * math.cos(lat2)
                z3 = self.radius * math.sin(lat2) * math.sin(lon2)
                
                x4 = self.radius * math.sin(lat2) * math.cos(lon1)
                y4 = self.radius * math.cos(lat2)
                z4 = self.radius * math.sin(lat2) * math.sin(lon1)
                
                glBegin(GL_QUADS)
                # Normals point outward from center
                glNormal3f(x1/self.radius, y1/self.radius, z1/self.radius)
                glVertex3f(x1, y1, z1)
                glNormal3f(x2/self.radius, y2/self.radius, z2/self.radius)
                glVertex3f(x2, y2, z2)
                glNormal3f(x3/self.radius, y3/self.radius, z3/self.radius)
                glVertex3f(x3, y3, z3)
                glNormal3f(x4/self.radius, y4/self.radius, z4/self.radius)
                glVertex3f(x4, y4, z4)
                glEnd()
        
        glPopMatrix()

class LifeHeart(GameObject):
    def __init__(self, position):
        super().__init__(position, RED)
        self.radius = 0.5
        self.lifetime = 10.0  # Disappears after 10 seconds
        self.age = 0
        self.bounce_speed = 2.0
        self.bounce_offset = 0
        
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
        
        # Bounce up and down
        self.bounce_offset = math.sin(self.age * self.bounce_speed) * 0.3
        
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y + 0.5 + self.bounce_offset, self.position.z)
        
        # Rotate for better view
        glRotatef(-20, 1, 0, 0)
        
        # Apply glossy red material
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.3, 0.0, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.9, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 0.8, 0.8, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 96.0)
        
        # Flash effect as it's about to disappear
        if self.age > self.lifetime - 2.0:
            flash = math.sin(self.age * 10) * 0.5 + 0.5
            glColor3f(1.0, flash * 0.5, flash * 0.5)
        else:
            glColor3f(1.0, 0.1, 0.1)
        
        scale = 0.4
        
        # Draw heart shape using spheres and geometry
        # Left lobe of heart
        glPushMatrix()
        glTranslatef(-0.35 * scale, 0.35 * scale, 0)
        self.draw_sphere(0.5 * scale, 12)
        glPopMatrix()
        
        # Right lobe of heart
        glPushMatrix()
        glTranslatef(0.35 * scale, 0.35 * scale, 0)
        self.draw_sphere(0.5 * scale, 12)
        glPopMatrix()
        
        # Bottom point (pyramid)
        glBegin(GL_TRIANGLES)
        # Front face
        glNormal3f(0, -0.5, 0.87)
        glVertex3f(-0.6 * scale, 0.2 * scale, 0.3 * scale)
        glVertex3f(0.6 * scale, 0.2 * scale, 0.3 * scale)
        glVertex3f(0, -0.8 * scale, 0)
        
        # Back face
        glNormal3f(0, -0.5, -0.87)
        glVertex3f(-0.6 * scale, 0.2 * scale, -0.3 * scale)
        glVertex3f(0, -0.8 * scale, 0)
        glVertex3f(0.6 * scale, 0.2 * scale, -0.3 * scale)
        
        # Left face
        glNormal3f(-0.87, -0.5, 0)
        glVertex3f(-0.6 * scale, 0.2 * scale, -0.3 * scale)
        glVertex3f(-0.6 * scale, 0.2 * scale, 0.3 * scale)
        glVertex3f(0, -0.8 * scale, 0)
        
        # Right face
        glNormal3f(0.87, -0.5, 0)
        glVertex3f(0.6 * scale, 0.2 * scale, 0.3 * scale)
        glVertex3f(0.6 * scale, 0.2 * scale, -0.3 * scale)
        glVertex3f(0, -0.8 * scale, 0)
        glEnd()
        
        # Fill middle section
        glBegin(GL_QUADS)
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-0.6 * scale, 0.2 * scale, 0.3 * scale)
        glVertex3f(-0.35 * scale, 0.5 * scale, 0.3 * scale)
        glVertex3f(0.35 * scale, 0.5 * scale, 0.3 * scale)
        glVertex3f(0.6 * scale, 0.2 * scale, 0.3 * scale)
        
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-0.6 * scale, 0.2 * scale, -0.3 * scale)
        glVertex3f(0.6 * scale, 0.2 * scale, -0.3 * scale)
        glVertex3f(0.35 * scale, 0.5 * scale, -0.3 * scale)
        glVertex3f(-0.35 * scale, 0.5 * scale, -0.3 * scale)
        glEnd()
        
        glPopMatrix()
    
    def draw_sphere(self, radius, segments):
        """Helper to draw a sphere"""
        for i in range(segments):
            lat1 = (i / segments) * math.pi
            lat2 = ((i + 1) / segments) * math.pi
            
            for j in range(segments * 2):
                lon1 = (j / (segments * 2)) * 2 * math.pi
                lon2 = ((j + 1) / (segments * 2)) * 2 * math.pi
                
                x1 = radius * math.sin(lat1) * math.cos(lon1)
                y1 = radius * math.cos(lat1)
                z1 = radius * math.sin(lat1) * math.sin(lon1)
                
                x2 = radius * math.sin(lat1) * math.cos(lon2)
                y2 = radius * math.cos(lat1)
                z2 = radius * math.sin(lat1) * math.sin(lon2)
                
                x3 = radius * math.sin(lat2) * math.cos(lon2)
                y3 = radius * math.cos(lat2)
                z3 = radius * math.sin(lat2) * math.sin(lon2)
                
                x4 = radius * math.sin(lat2) * math.cos(lon1)
                y4 = radius * math.cos(lat2)
                z4 = radius * math.sin(lat2) * math.sin(lon1)
                
                glBegin(GL_QUADS)
                glNormal3f(x1/radius, y1/radius, z1/radius)
                glVertex3f(x1, y1, z1)
                glNormal3f(x2/radius, y2/radius, z2/radius)
                glVertex3f(x2, y2, z2)
                glNormal3f(x3/radius, y3/radius, z3/radius)
                glVertex3f(x3, y3, z3)
                glNormal3f(x4/radius, y4/radius, z4/radius)
                glVertex3f(x4, y4, z4)
                glEnd()

class Laser(GameObject):
    def __init__(self, position, direction, color=CYAN, owner="player"):
        super().__init__(position, color)
        self.direction = direction.normalize()
        self.speed = 25.0
        self.lifetime = 3.0
        self.age = 0
        self.radius = 0.3
        self.owner = owner
    
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
        
        self.position.x += self.direction.x * self.speed * dt
        self.position.y += self.direction.y * self.speed * dt
        self.position.z += self.direction.z * self.speed * dt
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Enable transparency for laser
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow effect
        glDepthMask(GL_FALSE)  # Don't write to depth buffer
        
        # Set laser material - emissive glow
        glMaterialfv(GL_FRONT, GL_EMISSION, [self.color[0], self.color[1], self.color[2], 1.0])
        glMaterialfv(GL_FRONT, GL_AMBIENT, [self.color[0] * 0.5, self.color[1] * 0.5, self.color[2] * 0.5, 0.8])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [self.color[0], self.color[1], self.color[2], 0.8])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 128.0)
        
        glColor4f(self.color[0], self.color[1], self.color[2], 0.8)
        
        # Draw laser beam as elongated sphere/cylinder
        segments = 8
        length = 0.8
        radius = 0.15
        
        # Draw cylinder for laser beam
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            x1 = radius * math.cos(angle1)
            y1 = radius * math.sin(angle1)
            x2 = radius * math.cos(angle2)
            y2 = radius * math.sin(angle2)
            
            nx = (math.cos(angle1) + math.cos(angle2)) / 2
            ny = (math.sin(angle1) + math.sin(angle2)) / 2
            
            glBegin(GL_QUADS)
            glNormal3f(nx, ny, 0)
            glVertex3f(x1, y1, -length/2)
            glVertex3f(x2, y2, -length/2)
            glVertex3f(x2, y2, length/2)
            glVertex3f(x1, y1, length/2)
            glEnd()
        
        # Draw end caps
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, length/2)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, length/2)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -length/2)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, -length/2)
        glEnd()
        
        # Reset material emission
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        
        # Restore normal blending and depth
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glPopMatrix()

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
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        else:
            # Green player tank
            base_color = [0.1, 0.6, 0.1]
            highlight_color = [0.2, 0.8, 0.2]
            dark_color = [0.05, 0.3, 0.05]
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.2, 0.0, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.1, 0.7, 0.1, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.9, 0.9, 0.9, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0)
        
        # tank hull
        glColor3f(*base_color)
        self.draw_tank_hull_solid(1.6, 0.5, 2.4)
        
        # tank tracks 
        glColor3f(*dark_color)
        self.draw_tank_tracks_solid()
        
        # turret 
        glPushMatrix()
        glTranslatef(0, 0.4, -0.2) 
        glColor3f(*highlight_color)
        self.draw_tank_turret_solid(0.8, 0.4, 0.8)
        
        # cannon barrel 
        glTranslatef(0, 0.15, 0.6)
        glColor3f(0.3, 0.3, 0.3)
        # Set metallic material for barrel
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.3, 0.3, 0.3, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 128.0)
        self.draw_tank_barrel_solid()
        
        # tank details
        glPopMatrix()
        self.draw_tank_details_solid(base_color, dark_color)
        
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
    
    # ========== SOLID RENDERING METHODS ==========
    def draw_tank_hull_solid(self, width, height, depth):
        """Draw solid tank hull with lighting"""
        w, h, d = width/2, height/2, depth/2
        
        # Front face (angled)
        glBegin(GL_QUADS)
        glNormal3f(0, 0.3, 0.95)  # Angled normal
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, d*0.8)
        glEnd()
        
        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        glEnd()
        
        # Top face (angled)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-w*0.8, h, -d)
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, d*0.8)
        glVertex3f(w*0.8, h, -d)
        glEnd()
        
        # Bottom face
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        glEnd()
        
        # Left side
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, d)
        glVertex3f(-w*0.8, h, d*0.8)
        glVertex3f(-w*0.8, h, -d)
        glVertex3f(-w, -h, -d)
        glEnd()
        
        # Right side
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, d)
        glVertex3f(w, -h, -d)
        glVertex3f(w*0.8, h, -d)
        glVertex3f(w*0.8, h, d*0.8)
        glEnd()
    
    def draw_tank_tracks_solid(self):
        """Draw solid tank tracks"""
        track_width = 0.2
        track_height = 0.3
        hull_width = 1.6
        
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (hull_width/2 + track_width/2), -0.1, 0)
            
            # Track body - simple box
            # Front
            glBegin(GL_QUADS)
            glNormal3f(0, 0, 1)
            glVertex3f(-track_width/2, -track_height, 1.0)
            glVertex3f(track_width/2, -track_height, 1.0)
            glVertex3f(track_width/2, track_height, 1.0)
            glVertex3f(-track_width/2, track_height, 1.0)
            glEnd()
            
            # Back
            glBegin(GL_QUADS)
            glNormal3f(0, 0, -1)
            glVertex3f(-track_width/2, -track_height, -1.0)
            glVertex3f(-track_width/2, track_height, -1.0)
            glVertex3f(track_width/2, track_height, -1.0)
            glVertex3f(track_width/2, -track_height, -1.0)
            glEnd()
            
            # Outer side
            glBegin(GL_QUADS)
            glNormal3f(side, 0, 0)
            glVertex3f(track_width/2 * side, -track_height, 1.0)
            glVertex3f(track_width/2 * side, -track_height, -1.0)
            glVertex3f(track_width/2 * side, track_height, -1.0)
            glVertex3f(track_width/2 * side, track_height, 1.0)
            glEnd()
            
            glPopMatrix()
    
    def draw_tank_turret_solid(self, width, height, depth):
        """Draw solid turret"""
        w, h, d = width/2, height/2, depth/2
        
        # Front (angled)
        glBegin(GL_QUADS)
        glNormal3f(0, 0.2, 0.98)
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(w*0.7, -h, d)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        glEnd()
        
        # Back
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        glEnd()
        
        # Top (rounded approximation)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-w*0.8, h, -d*0.8)
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(w*0.5, h, d*0.8)
        glVertex3f(w*0.8, h, -d*0.8)
        glEnd()
        
        # Left side
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        glVertex3f(-w*0.7, -h, d)
        glVertex3f(-w*0.5, h, d*0.8)
        glVertex3f(-w*0.8, h, -d*0.8)
        glVertex3f(-w, -h, -d)
        glEnd()
        
        # Right side
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        glVertex3f(w*0.7, -h, d)
        glVertex3f(w, -h, -d)
        glVertex3f(w*0.8, h, -d*0.8)
        glVertex3f(w*0.5, h, d*0.8)
        glEnd()
    
    def draw_tank_barrel_solid(self):
        """Draw solid barrel using cylinder approximation"""
        barrel_length = 1.4
        barrel_radius = 0.08
        segments = 12
        
        # Draw barrel as a series of quad strips
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            x1 = barrel_radius * math.cos(angle1)
            y1 = barrel_radius * math.sin(angle1)
            x2 = barrel_radius * math.cos(angle2)
            y2 = barrel_radius * math.sin(angle2)
            
            # Normal for this segment
            nx = (math.cos(angle1) + math.cos(angle2)) / 2
            ny = (math.sin(angle1) + math.sin(angle2)) / 2
            
            glBegin(GL_QUADS)
            glNormal3f(nx, ny, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x2, y2, barrel_length)
            glVertex3f(x1, y1, barrel_length)
            glEnd()
        
        # Muzzle brake
        glPushMatrix()
        glTranslatef(0, 0, barrel_length - 0.1)
        brake_radius = barrel_radius * 1.3
        
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi
            angle2 = ((i + 1) / segments) * 2 * math.pi
            
            x1 = brake_radius * math.cos(angle1)
            y1 = brake_radius * math.sin(angle1)
            x2 = brake_radius * math.cos(angle2)
            y2 = brake_radius * math.sin(angle2)
            
            nx = (math.cos(angle1) + math.cos(angle2)) / 2
            ny = (math.sin(angle1) + math.sin(angle2)) / 2
            
            glBegin(GL_QUADS)
            glNormal3f(nx, ny, 0)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x2, y2, 0.15)
            glVertex3f(x1, y1, 0.15)
            glEnd()
        
        glPopMatrix()
    
    def draw_tank_details_solid(self, base_color, dark_color):
        """Draw solid tank details"""
        # Commander hatch
        glPushMatrix()
        glTranslatef(-0.2, 0.8, -0.3)
        glColor3f(*dark_color)
        glScalef(0.3, 0.05, 0.3)
        self.draw_solid_cube(1, 1, 1)
        glPopMatrix()
        
        # Side armor panels
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.9, 0, 0)
            glColor3f(base_color[0] * 0.8, base_color[1] * 0.8, base_color[2] * 0.8)
            glScalef(0.05, 0.3, 1.5)
            self.draw_solid_cube(1, 1, 1)
            glPopMatrix()
    
    def draw_solid_cube(self, width, height, depth):
        """Draw a solid cube with proper normals"""
        w, h, d = width/2, height/2, depth/2
        
        # Front
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        glEnd()
        
        # Back
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        glEnd()
        
        # Top
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        glEnd()
        
        # Bottom
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        glEnd()
        
        # Left
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()
        
        # Right
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        glEnd()

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Tank 3D - Mini Game 2")
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize OpenGL with full lighting and shading
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)  # Sun/main light
        glEnable(GL_LIGHT1)  # Fill light
        glEnable(GL_LIGHT2)  # Headlight (NEW - initially disabled)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable smooth shading
        glShadeModel(GL_SMOOTH)
        
        # background color (sky - will change with day/night)
        glClearColor(0.4, 0.6, 0.9, 1.0)  # Day sky
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Global ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.25, 1.0])
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        
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
        
        # Day/night cycle
        self.time_of_day = 0.0  # 0 = day, 1.0 = night
        self.manual_mode = 0  # 0=Day, 1=Night
        
        # Headlight system (NEW GAMEPLAY FEATURE)
        self.headlights_on = False
        
        # Life heart spawning
        self.life_hearts = []
        self.heart_spawn_timer = 0
        self.heart_spawn_interval = 5.0  # Spawn every 5 seconds
        
        # Initialize game objects
        self.init_game_objects()
        
        self.camera_pos = Vector3(0, 5, 10)
        self.camera_target = Vector3(0, 0, 0)
        
        # Intro animation
        self.intro_rotation = 0
    
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
    
    def update_lighting(self):
        """Update lighting based on day/night cycle"""
        # Simple day/night transition
        if self.time_of_day < 0.5:  # Day
            t = self.time_of_day * 2  # 0 to 1
            # Sky color - bright blue
            sky_r = 0.4
            sky_g = 0.6
            sky_b = 0.9
            # Sun intensity - bright
            sun_intensity = 1.0
            # Sun color - yellow
            sun_r = 1.0
            sun_g = 1.0
            sun_b = 0.9
        else:  # Night
            t = (self.time_of_day - 0.5) * 2  # 0 to 1
            # Sky color - dark blue
            sky_r = 0.05
            sky_g = 0.05
            sky_b = 0.15
            # Moon intensity - dim
            sun_intensity = 0.2
            # Moon color - white-blue
            sun_r = 0.8
            sun_g = 0.8
            sun_b = 1.0
        
        # Update sky color
        glClearColor(sky_r, sky_g, sky_b, 1.0)
        
        # Calculate sun/moon position (moves across sky)
        sun_angle = (self.time_of_day) * 180  # Half rotation
        sun_x = math.cos(math.radians(sun_angle)) * 50
        sun_y = abs(math.sin(math.radians(sun_angle)) * 50) + 10
        sun_z = -30
        
        # Main light (GL_LIGHT0 - Sun/Moon)
        glLightfv(GL_LIGHT0, GL_POSITION, [sun_x, sun_y, sun_z, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [sun_r * sun_intensity, sun_g * sun_intensity, sun_b * sun_intensity, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [sun_intensity, sun_intensity, sun_intensity, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.15, 1.0])
        
        # Fill light (GL_LIGHT1 - ambient fill from opposite direction)
        fill_intensity = sun_intensity * 0.3
        glLightfv(GL_LIGHT1, GL_POSITION, [-sun_x * 0.5, 20, -sun_z * 0.5, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [fill_intensity * 0.8, fill_intensity * 0.8, fill_intensity, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.05, 0.05, 0.1, 1.0])
        
        # Headlight (GL_LIGHT2) - player tank spotlight
        if self.headlights_on:
            # Position headlight at player tank position
            headlight_pos = [
                self.player_position.x,
                self.player_position.y + 0.5,
                self.player_position.z,
                1.0  # Positional light
            ]
            
            # Direction the headlight points (forward from tank)
            look_dir_x = math.sin(math.radians(self.player_rotation_y))
            look_dir_z = math.cos(math.radians(self.player_rotation_y))
            headlight_dir = [look_dir_x, -0.1, look_dir_z]
            
            glEnable(GL_LIGHT2)
            glLightfv(GL_LIGHT2, GL_POSITION, headlight_pos)
            glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, headlight_dir)
            
            # Bright white spotlight
            glLightfv(GL_LIGHT2, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
            glLightfv(GL_LIGHT2, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
            glLightfv(GL_LIGHT2, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
            
            # Spotlight properties
            glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, 35.0)  # 35 degree cone
            glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, 15.0)  # Focused beam
            
            # Attenuation for realistic falloff
            glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION, 0.05)
            glLightf(GL_LIGHT2, GL_QUADRATIC_ATTENUATION, 0.01)
        else:
            glDisable(GL_LIGHT2)
    
    def update_game(self, dt):
        # Set time based on manual_mode
        target_times = [0.0, 0.5]  # Day, Night
        self.time_of_day = target_times[self.manual_mode]
        
        self.update_lighting()
        
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
        
        # Spawn life hearts more frequently
        self.heart_spawn_timer += dt
        if self.heart_spawn_timer >= self.heart_spawn_interval:
            self.spawn_life_heart()
            self.heart_spawn_timer = 0
            self.heart_spawn_interval = random.uniform(5.0, 8.0)  # Random interval 5-8 seconds
            
        self.ensure_enemies_nearby()

    def init_game_objects(self):
        """Initialize or reset game objects"""
        self.player_tank = Tank(Vector3(0, 0, 5), GREEN, is_enemy=False)
        self.player_position = Vector3(0, 0, 5)
        self.player_rotation_y = 0
        
        # Input tracking
        self.keys_pressed = set()
        self.mouse_x, self.mouse_y = 0, 0
        
        # Game effects
        self.screen_shake_time = 0
        self.red_flash_time = 0
        
        # Environment objects
        self.mountains = []
        self.trees = []
        self.color_spheres = []
        self.enemy_tanks = []
        self.lasers = []
        self.explosions = []
        
        # Create static environment
        # Mountains
        mountain_positions = [
            (Vector3(15, 0, -20), 4),
            (Vector3(-18, 0, -15), 5),
            (Vector3(20, 0, 10), 3.5),
            (Vector3(-15, 0, 15), 4.5),
            (Vector3(0, 0, -25), 6)
        ]
        for pos, size in mountain_positions:
            self.mountains.append(Mountain(pos, size))
        
        # Trees
        for _ in range(15):
            pos = Vector3(
                random.uniform(-25, 25),
                0,
                random.uniform(-25, 25)
            )
            # Don't place trees too close to player spawn
            if (abs(pos.x) > 5 or abs(pos.z - 5) > 5):
                self.trees.append(Tree(pos))
        
        # Collectible spheres
        sphere_colors = [RED, BLUE, YELLOW, PURPLE, CYAN]
        for _ in range(8):
            pos = Vector3(
                random.uniform(-20, 20),
                0,
                random.uniform(-20, 20)
            )
            color = random.choice(sphere_colors)
            self.color_spheres.append(ColorSphere(pos, color))
    
    def draw_text_2d(self, text, x, y, font, color=(255, 255, 255), bg_color=None, padding=5):
        """Draw 2D text with optional semi-transparent background"""
        # Render text to surface first to get dimensions
        text_surface = font.render(text, True, color)
        w, h = text_surface.get_width(), text_surface.get_height()
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Switch to 2D mode
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Draw semi-transparent background if requested
        if bg_color:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(bg_color[0]/255, bg_color[1]/255, bg_color[2]/255, 0.75)
            
            # Draw background rectangle (properly aligned with text)
            glBegin(GL_QUADS)
            glVertex2f(x - padding, y - padding)
            glVertex2f(x + w + padding, y - padding)
            glVertex2f(x + w + padding, y + h + padding)
            glVertex2f(x - padding, y + h + padding)
            glEnd()
            
            # Draw subtle border
            glColor4f(1.0, 1.0, 1.0, 0.3)
            glLineWidth(1.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(x - padding, y - padding)
            glVertex2f(x + w + padding, y - padding)
            glVertex2f(x + w + padding, y + h + padding)
            glVertex2f(x - padding, y + h + padding)
            glEnd()
        
        # Draw text
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 1, 1)
        
        glRasterPos2f(x, y + h)  # Adjust y position for proper alignment
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_hud(self):
        """Draw game HUD with improved visibility"""
        # Lives
        self.draw_text_2d(
            f"Lives: {self.player_lives}", 
            20, 40, 
            self.medium_font, 
            (255, 255, 255),
            bg_color=(0, 0, 0),
            padding=10
        )
        
        # Score
        self.draw_text_2d(
            f"Score: {self.score}",
            20, 85,
            self.medium_font,
            (255, 255, 100),
            bg_color=(0, 0, 0),
            padding=10
        )
        
        # Enemy count
        enemy_count = len([e for e in self.enemy_tanks if e.active])
        self.draw_text_2d(
            f"Enemies: {enemy_count}",
            20, 130,
            self.small_font,
            (255, 100, 100),
            bg_color=(0, 0, 0),
            padding=8
        )
        
        # Day/night cycle indicator
        time_names = ["Day", "Night"]
        time_index = 0 if self.time_of_day < 0.5 else 1
        time_text = time_names[time_index]
        time_colors = [(255, 255, 100), (150, 150, 255)]
        
        mode_text = f"Time: {time_text} (Press 1: Day | 2: Night)"
        self.draw_text_2d(
            mode_text,
            20, 170,
            self.small_font,
            time_colors[time_index],
            bg_color=(0, 0, 0),
            padding=8
        )
        
        # Headlight indicator
        headlight_status = "ON" if self.headlights_on else "OFF"
        headlight_color = (100, 255, 100) if self.headlights_on else (150, 150, 150)
        self.draw_text_2d(
            f"Headlights: {headlight_status} (Press H to Toggle)",
            20, 210,
            self.small_font,
            headlight_color,
            bg_color=(0, 0, 0),
            padding=8
        )
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            
            if self.game_state == GAME_STATE_INTRO:
                self.update_intro(dt)
                self.render_intro()
            elif self.game_state == GAME_STATE_PLAYING:
                self.update(dt)
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
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GAME_STATE_PLAYING:
                        self.game_state = GAME_STATE_GAME_OVER
                    else:
                        self.running = False
                elif event.key == pygame.K_RETURN:
                    if self.game_state == GAME_STATE_INTRO:
                        self.game_state = GAME_STATE_PLAYING
                    elif self.game_state == GAME_STATE_GAME_OVER:
                        self.__init__()  
                        self.game_state = GAME_STATE_PLAYING

                
                elif event.key == pygame.K_SPACE:
                    laser = self.player_tank.shoot(pygame.time.get_ticks() / 1000.0)
                    if laser:
                        self.lasers.append(laser)
                
                
                # Manual day/night selection (1-2 keys)
                elif event.key == pygame.K_1 and self.game_state == GAME_STATE_PLAYING:
                    self.manual_mode = 0  # Day
                elif event.key == pygame.K_2 and self.game_state == GAME_STATE_PLAYING:
                    self.manual_mode = 1  # Night
                
                # Toggle headlights (H key) - NEW GAMEPLAY INTERACTION
                elif event.key == pygame.K_h and self.game_state == GAME_STATE_PLAYING:
                    self.headlights_on = not self.headlights_on
                
                # Track keys for movement
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    self.keys_pressed.add(event.key)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.discard(event.key)
            
            elif event.type == pygame.MOUSEMOTION and self.game_state == GAME_STATE_PLAYING:
                self.mouse_x, self.mouse_y = event.pos
    
    def update(self, dt):
        self.handle_player_input(dt)
        
        self.player_tank.position = self.player_position
        self.player_tank.rotation.y = self.player_rotation_y
        
        self.update_camera()
    
        self.update_game(dt)
        
        for laser in self.lasers:
            laser.update(dt)
        
        for enemy in self.enemy_tanks:
            enemy.update(dt)
            if enemy.active and random.random() < 0.01:  
                laser = enemy.shoot(pygame.time.get_ticks() / 1000.0)
                if laser:
                    self.lasers.append(laser)
        
        for explosion in self.explosions:
            explosion.update(dt)
        
        for sphere in self.color_spheres:
            sphere.update(dt)
        
        for heart in self.life_hearts:
            heart.update(dt)
        
        self.check_collisions()
        
        self.lasers = [l for l in self.lasers if l.active]
        self.enemy_tanks = [e for e in self.enemy_tanks if e.active]
        self.explosions = [e for e in self.explosions if e.active]
        self.color_spheres = [s for s in self.color_spheres if s.active]
        self.life_hearts = [h for h in self.life_hearts if h.active]

        if self.player_lives <= 0:
            self.game_state = GAME_STATE_GAME_OVER
    
    def handle_player_input(self, dt):
        move_speed = self.player_tank.speed * dt
        old_position = Vector3(self.player_position.x, self.player_position.y, self.player_position.z)

        
        if pygame.K_w in self.keys_pressed:
            self.player_position.x += math.sin(math.radians(self.player_rotation_y)) * move_speed
            self.player_position.z += math.cos(math.radians(self.player_rotation_y)) * move_speed
        if pygame.K_s in self.keys_pressed:
            self.player_position.x -= math.sin(math.radians(self.player_rotation_y)) * move_speed
            self.player_position.z -= math.cos(math.radians(self.player_rotation_y)) * move_speed
        if pygame.K_a in self.keys_pressed:
            self.player_rotation_y += self.player_tank.rotation_speed * dt
        if pygame.K_d in self.keys_pressed:
            self.player_rotation_y -= self.player_tank.rotation_speed * dt

        # Check collision with mountains and trees
        collision_obj = self.check_environment_collision()
        if collision_obj:
            # Bounce back 
            self.bounce_from_obstacle(old_position, collision_obj)
            
            # Lose a life 
            if not hasattr(self, 'collision_cooldown'):
                self.collision_cooldown = 0
            
            if self.collision_cooldown <= 0:
                self.player_lives -= 1
                self.collision_cooldown = 1.0  
                self.red_flash_time = 0.3
                self.screen_shake_time = 0.2
               
                self.explosions.append(Explosion(
                    Vector3(self.player_position.x, self.player_position.y + 0.5, self.player_position.z),
                    ORANGE
                ))
        
        if hasattr(self, 'collision_cooldown') and self.collision_cooldown > 0:
            self.collision_cooldown -= dt
        
        bound = 40
        self.player_position.x = max(-bound, min(bound, self.player_position.x))
        self.player_position.z = max(-bound, min(bound, self.player_position.z))
    
    def check_environment_collision(self):
        """Check if player collides with mountains or trees"""

        player_radius = self.player_tank.radius
        
        # Check mountains
        for mountain in self.mountains:
            dx = self.player_position.x - mountain.position.x
            dz = self.player_position.z - mountain.position.z
            dist = math.sqrt(dx*dx + dz*dz)
            
            # Mountain collision radius (base of mountain)
            mountain_collision_radius = mountain.size * 0.6
            
            if dist < (player_radius + mountain_collision_radius):
                return mountain
        
        # Check trees
        for tree in self.trees:
            dx = self.player_position.x - tree.position.x
            dz = self.player_position.z - tree.position.z
            dist = math.sqrt(dx*dx + dz*dz)
            
            # Tree collision radius (trunk + foliage)
            tree_collision_radius = 0.8
            
            if dist < (player_radius + tree_collision_radius):
                return tree
        
        return None
    
    def bounce_from_obstacle(self, old_position, obstacle):
        """Bounce player away from obstacle"""
        # Calculate direction from obstacle to player
        dx = self.player_position.x - obstacle.position.x
        dz = self.player_position.z - obstacle.position.z
        dist = math.sqrt(dx*dx + dz*dz)
        
        if dist > 0:
            dx /= dist
            dz /= dist
            
            if isinstance(obstacle, Mountain):
                obstacle_radius = obstacle.size * 0.6
            else:  # Tree
                obstacle_radius = 0.8
            
            push_distance = self.player_tank.radius + obstacle_radius + 0.5  # Extra 0.5 for safety
            self.player_position.x = obstacle.position.x + dx * push_distance
            self.player_position.z = obstacle.position.z + dz * push_distance
        else:
            self.player_position.x = old_position.x
            self.player_position.z = old_position.z

    
    def update_intro(self, dt):
        self.intro_rotation += dt * 20
    
    def render_intro(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        title_text = "TANK 3D - MINI GAME 2"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_x = (WINDOW_WIDTH - title_surface.get_width()) // 2
        self.draw_text_2d(
            title_text,
            title_x, 100,
            self.title_font,
            (100, 200, 255),
            bg_color=(0, 0, 50),
            padding=15
        )
        
        features_header = "User Guide:"
        header_surface = self.medium_font.render(features_header, True, (255, 255, 255))
        header_x = (WINDOW_WIDTH - header_surface.get_width()) // 2
        self.draw_text_2d(
            features_header,
            header_x, 250,
            self.medium_font,
            (200, 200, 200),
            bg_color=(0, 0, 0),
            padding=10
        )
        
        features = [
            "• WASD: Move Forward/Left/Backward/Right",
            "• Mouse: Aim your tank",
            "• SPACE: Shoot lasers at enemies",
            "• H: Toggle headlights ON/OFF",
            "• 1: Switch to Day mode | 2: Switch to Night mode",
            "• Collect glass spheres for +50 points",
            "• Collect life hearts for +1 life (disappear after 10 seconds)",
            "• Destroy enemy tanks for +25 points",
            "• Survive as long as possible!"
        ]
        
        y_offset = 300
        for feature in features:
            feature_surface = self.small_font.render(feature, True, (255, 255, 255))
            feature_x = (WINDOW_WIDTH - feature_surface.get_width()) // 2
            self.draw_text_2d(
                feature,
                feature_x, y_offset,
                self.small_font,
                (150, 255, 150),
                bg_color=(0, 0, 0),
                padding=5
            )
            y_offset += 35
        
        start_text = "Press ENTER to Start"
        start_surface = self.large_font.render(start_text, True, (255, 255, 255))
        start_x = (WINDOW_WIDTH - start_surface.get_width()) // 2
        self.draw_text_2d(
            start_text,
            start_x, WINDOW_HEIGHT - 100,
            self.large_font,
            (255, 255, 100),
            bg_color=(0, 0, 0),
            padding=10
        )
    
    def render_game(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        gluLookAt(
            self.camera_pos.x, self.camera_pos.y, self.camera_pos.z,
            self.camera_target.x, self.camera_target.y, self.camera_target.z,
            0, 1, 0
        )
        
        self.draw_ground()
        
        self.draw_direction_arrows()

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        
        for mountain in self.mountains:
            glColor3f(1.0, 1.0, 1.0)
            mountain.render()
        
        for tree in self.trees:
            tree.render()

        self.player_tank.render()
        
        self.player_tank.render()
        
        for enemy in self.enemy_tanks:
            if enemy.active:
                enemy.render()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        

        for sphere in self.color_spheres:
            if sphere.active:
                sphere.render()
                glDepthMask(GL_TRUE)
        
        for heart in self.life_hearts:
            if heart.active:
                heart.render()

        for laser in self.lasers:
            if laser.active:
                laser.render()
        
        for explosion in self.explosions:
            if explosion.active:
                explosion.render()
        
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        self.draw_hud()
    
    def render_game_over(self):
        # Render the game scene first
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set camera
        gluLookAt(
            self.camera_pos.x, self.camera_pos.y, self.camera_pos.z,
            self.camera_target.x, self.camera_target.y, self.camera_target.z,
            0, 1, 0
        )
        
        # Draw ground
        self.draw_ground()
        
        # Draw environment
        for mountain in self.mountains:
            mountain.render()
        
        for tree in self.trees:
            tree.render()
        
        # Draw tanks
        self.player_tank.render()
        for enemy in self.enemy_tanks:
            if enemy.active:
                enemy.render()
        
        # Game over overlay
        self.draw_text_2d(
            "GAME OVER",
            WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50,
            self.title_font,
            (255, 50, 50),
            bg_color=(0, 0, 0),
            padding=20
        )
        
        self.draw_text_2d(
            f"Final Score: {self.score}",
            WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 50,
            self.large_font,
            (255, 255, 100),
            bg_color=(0, 0, 0),
            padding=15
        )
        
        self.draw_text_2d(
            "Press ENTER to Restart or ESC to Quit",
            WINDOW_WIDTH // 2 - 220, WINDOW_HEIGHT // 2 + 120,
            self.medium_font,
            (200, 200, 200),
            bg_color=(0, 0, 0),
            padding=10
        )
    
    def check_collisions(self):
        # Player laser vs enemy tanks
        for laser in self.lasers:
            if not laser.active or laser.owner != "player":
                continue
            
            for enemy in self.enemy_tanks:
                if not enemy.active:
                    continue
                
                dx = laser.position.x - enemy.position.x
                dy = laser.position.y - enemy.position.y
                dz = laser.position.z - enemy.position.z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < (laser.radius + enemy.radius):
                    laser.active = False
                    enemy.active = False
                    self.explosions.append(Explosion(enemy.position))
                    self.score += 25
        
        # Enemy laser vs player
        for laser in self.lasers:
            if not laser.active or laser.owner != "enemy":
                continue
            
            dx = laser.position.x - self.player_position.x
            dy = laser.position.y - self.player_position.y
            dz = laser.position.z - self.player_position.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < (laser.radius + self.player_tank.radius):
                laser.active = False
                self.player_lives -= 1
                self.explosions.append(Explosion(self.player_position))
                self.red_flash_time = 0.5
        
        # Player vs spheres
        for sphere in self.color_spheres:
            if not sphere.active:
                continue
            
            dx = sphere.position.x - self.player_position.x
            dz = sphere.position.z - self.player_position.z
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (sphere.radius + self.player_tank.radius):
                sphere.active = False
                self.score += 10
        
        # Player vs life hearts
        for heart in self.life_hearts:
            if not heart.active:
                continue
            
            dx = heart.position.x - self.player_position.x
            dz = heart.position.z - self.player_position.z
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (heart.radius + self.player_tank.radius):
                heart.active = False
                self.player_lives += 1   
    
    def spawn_enemy(self):
        if len([e for e in self.enemy_tanks if e.active]) >= self.max_enemies:
            return
        
        # Spawn enemy away from player
        angle = random.uniform(0, 360)
        distance = random.uniform(15, 25)
        pos = Vector3(
            self.player_position.x + math.sin(math.radians(angle)) * distance,
            0,
            self.player_position.z + math.cos(math.radians(angle)) * distance
        )
        
        # Keep in bounds
        pos.x = max(-35, min(35, pos.x))
        pos.z = max(-35, min(35, pos.z))
        
        self.enemy_tanks.append(Tank(pos, RED, is_enemy=True))
    
    def ensure_enemies_nearby(self):
        # Make sure there are always some enemies
        active_enemies = len([e for e in self.enemy_tanks if e.active])
        if active_enemies < 2:
            self.spawn_enemy()
    
    def spawn_life_heart(self):
        """Spawn a life heart at a random location"""
        pos = Vector3(
            random.uniform(-25, 25),
            0,
            random.uniform(-25, 25)
        )
        self.life_hearts.append(LifeHeart(pos))
    
    def draw_ground(self):
        """Draw ground plane with proper material that changes with day/night"""
        if self.time_of_day < 0.5:  # Day mode (key 1)
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.7, 0.7, 0.8, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.9, 0.9, 0.95, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.6, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 32.0)
            glColor3f(0.9, 0.9, 0.95) 
            grid_color = (0.7, 0.7, 0.8, 0.3) 
        else:  # Night mode (key 2)
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.25, 0.4, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.5, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 64.0) 
            glColor3f(0.15, 0.18, 0.3)  
            grid_color = (0.3, 0.4, 0.6, 0.2)  
        
        size = 100
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()
        
        # Draw grid lines for visual reference
        glDisable(GL_LIGHTING)
        glColor4f(*grid_color)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        grid_size = 50
        grid_spacing = 5
        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1, grid_spacing):
            glVertex3f(i, 0.01, -grid_size)
            glVertex3f(i, 0.01, grid_size)
            glVertex3f(-grid_size, 0.01, i)
            glVertex3f(grid_size, 0.01, i)
        glEnd()
        
        glEnable(GL_LIGHTING)
    def draw_direction_arrows(self):
        """Draw circular D-pad style directional indicator in bottom-right corner"""
        glPushAttrib(GL_ENABLE_BIT | GL_LINE_BIT | GL_CURRENT_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        center_x = 100
        center_y = WINDOW_HEIGHT - 100
        
        circle_radius = 60
        segments = 32
        glColor4f(0.3, 0.7, 1.0, 0.5)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center_x + circle_radius * math.cos(angle)
            y = center_y + circle_radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        inner_radius = 35
        glColor4f(0.3, 0.7, 1.0, 0.4)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        glColor4f(0.3, 0.7, 1.0, 0.6)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(center_x, center_y)
        for i in range(segments + 1):
            angle = (i / segments) * 2 * math.pi
            x = center_x + 8 * math.cos(angle)
            y = center_y + 8 * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        arrow_distance = 48
        arrow_size = 15
        
        w_pressed = pygame.K_w in self.keys_pressed
        s_pressed = pygame.K_s in self.keys_pressed
        a_pressed = pygame.K_a in self.keys_pressed
        d_pressed = pygame.K_d in self.keys_pressed
        
        # Map to WASD: W=Up, D=Right, S=Down, A=Left
        directions_keys = [
            (270, w_pressed),   # Up - W key
            (0, d_pressed),     # Right - D key
            (90, s_pressed),    # Down - S key
            (180, a_pressed)    # Left - A key
        ]
        
        for direction, is_pressed in directions_keys:
            angle_rad = math.radians(direction)
            arrow_x = center_x + arrow_distance * math.cos(angle_rad)
            arrow_y = center_y + arrow_distance * math.sin(angle_rad)
            
            if is_pressed:
                glColor4f(0.2, 1.0, 0.3, 0.95) 
            else:
                glColor4f(0.5, 0.8, 1.0, 0.7)  
            
            glBegin(GL_TRIANGLES)
            tip_x = arrow_x + arrow_size * math.cos(angle_rad)
            tip_y = arrow_y + arrow_size * math.sin(angle_rad)
            
            left_angle = angle_rad + math.radians(135)
            left_x = arrow_x + arrow_size * 0.5 * math.cos(left_angle)
            left_y = arrow_y + arrow_size * 0.5 * math.sin(left_angle)
            
            right_angle = angle_rad - math.radians(135)
            right_x = arrow_x + arrow_size * 0.5 * math.cos(right_angle)
            right_y = arrow_y + arrow_size * 0.5 * math.sin(right_angle)
            
            glVertex2f(tip_x, tip_y)
            glVertex2f(left_x, left_y)
            glVertex2f(right_x, right_y)
            glEnd()
            
            # Draw arrow shaft
            shaft_width = 5
            shaft_length = arrow_size * 0.6
            
            shaft_end_x = arrow_x - shaft_length * math.cos(angle_rad)
            shaft_end_y = arrow_y - shaft_length * math.sin(angle_rad)
            
            perp_angle = angle_rad + math.radians(90)
            offset_x = shaft_width * math.cos(perp_angle)
            offset_y = shaft_width * math.sin(perp_angle)
            
            glBegin(GL_QUADS)
            glVertex2f(arrow_x + offset_x, arrow_y + offset_y)
            glVertex2f(arrow_x - offset_x, arrow_y - offset_y)
            glVertex2f(shaft_end_x - offset_x, shaft_end_y - offset_y)
            glVertex2f(shaft_end_x + offset_x, shaft_end_y + offset_y)
            glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glPopAttrib()

if __name__ == "__main__":
    game = Game()
    game.run()