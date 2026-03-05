# Tank 3D - Mini Game 2

A 3D tank battle game built with Python, Pygame, and OpenGL featuring advanced lighting, materials, transparency effects, and a dynamic day/night cycle.

**Student ID:** 66011534

---

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
      cd path/to/mini_project2
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install required dependencies:**
   ```bash
   pip install pygame PyOpenGL PyOpenGL_accelerate
   ```

4. **Run the game:**
   ```bash
   python proj2_66011534.py
   ```

### Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| pygame | >= 2.0 | Window management, input handling, font rendering |
| PyOpenGL | >= 3.1 | OpenGL bindings for 3D rendering |
| PyOpenGL_accelerate | >= 3.1 | Performance optimization (optional) |

---

## Game Controls

| Key/Input | Action |
|-----------|--------|
| `W` | Move forward |
| `S` | Move backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Click SPACE BAR` | Shoot laser |
| `H` | Toggle headlights ON/OFF |
| `1` | Switch to Day mode |
| `2` | Switch to Night mode |
| `ENTER` | Start game / Restart after game over |
| `ESC` | Quit game |

---

## Feature Checklist

### Lighting System
- [x] **GL_LIGHT0** - Main sun/moon light with dynamic positioning
- [x] **GL_LIGHT1** - Ambient fill light for softer shadows
- [x] **GL_LIGHT2** - Player tank headlight (spotlight with cone)
- [x] **Dynamic light colors** - Yellow sun during day, blue-white moon at night
- [x] **Spotlight properties** - Cutoff angle, exponent, attenuation for headlights

### Material System
- [x] **Matte materials** - Low specular (mountains, ground, trees)
- [x] **Glossy materials** - High specular, high shininess (tanks, metallic parts)
- [x] **Glass materials** - Transparent with alpha blending (collectible spheres)
- [x] **Specialized materials** - Snow, rock, wood, foliage with unique properties
- [x] **Material class** - Reusable material definitions with ambient, diffuse, specular, shininess, alpha

### Transparency
- [x] **Alpha blending** - GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
- [x] **Transparent glass spheres** - Collectible items with see-through effect
- [x] **Additive blending** - Explosions and laser effects (GL_SRC_ALPHA, GL_ONE)
- [x] **Depth mask control** - Proper rendering order for transparent objects
- [x] **Render order** - Opaque objects first, transparent objects last

### Day/Night Cycle
- [x] **Manual switching** - Press 1 for Day, 2 for Night
- [x] **Sky color changes** - Bright blue (day) to dark blue (night)
- [x] **Ground color changes** - White snow (day) to dark blue frozen (night)
- [x] **Light intensity changes** - Bright sun vs dim moonlight
- [x] **Sun/moon positioning** - Light source moves based on time

### HUD (Heads-Up Display)
- [x] **Lives counter** - Current player lives
- [x] **Score display** - Points earned
- [x] **Enemy count** - Active enemies on field
- [x] **Time indicator** - Current day/night mode with control hints
- [x] **Headlight status** - ON/OFF indicator
- [x] **Directional D-pad** - Visual movement indicator (bottom-left)
- [x] **Semi-transparent backgrounds** - Improved text readability

### Additional Features
- [x] **Collision detection** - Player vs mountains, trees, enemies, collectibles
- [x] **Bounce mechanics** - Player bounces back when hitting obstacles
- [x] **Life hearts** - Collectible hearts that restore lives
- [x] **Explosions** - Particle effects when tanks are destroyed
- [x] **Enemy AI** - Tanks move, rotate, and shoot at player
- [x] **Screen shake** - Visual feedback on collision damage
- [x] **Red flash overlay** - Damage indication

---

## Gameplay Overview

### Objective
Survive as long as possible while destroying enemy tanks and collecting items.

### Scoring System
| Action | Points |
|--------|--------|
| Destroy enemy tank | +25 |
| Collect glass sphere | +10 |
| Collect life heart | +1 Life (no points) |

### Game Elements
- **Green Mountains** - Obstacles with collision (lose 1 life on impact)
- **Trees** - Smaller obstacles with collision (lose 1 life on impact)
- **Glass Spheres** - Transparent collectibles worth +10 points (various colors: Red, Blue, Yellow, Purple, Cyan)
- **Life Hearts** - Red bouncing hearts that restore +1 life (disappear after 10 seconds)
- **Enemy Tanks** - Red tanks that chase and shoot at player (+100 points when destroyed)

### Tips
- Use headlights at night for better visibility
- Collect life hearts before they disappear (10 second timer)
- Avoid hitting mountains and trees - you lose 1 life per collision
- Keep moving to avoid enemy fire
- Glass spheres give +10 points each - collect them all!

---

## 📁 Project Structure

```
mini_project2/
├── proj2_66011534.py    # Main game file
├── README.md            # This file
```
