import math
import random
import time  # Import time for consistent dt calculation

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Constants ---
# World and Grid
CELL_SIZE = 100  # Size of each grid cell
# Player
PLAYER_SPEED = 220.0
PLAYER_TURN_SPEED = 90.0  # Degrees per second (if using keys for turning)
MOUSE_SENSITIVITY = 0.15
PLAYER_RADIUS = 25.0
# Shooting
BULLET_SPEED = 700.0  # Slightly faster bullets
BULLET_DAMAGE = 15
BULLET_SIZE = 6  # Increased bullet size slightly
MUZZLE_FLASH_DURATION = 0.08  # Seconds the flash is visible
PITCH_MIN = -80.0
PITCH_MAX = 80.0
# Enemies
ENEMY_BULLET_SPEED = 300.0
ENEMY_COLLISION_DAMAGE_INTERVAL = 0.5
# Systems & Powerups
REPAIR_TIME = 5.0
POWERUP_PICKUP_RADIUS = 30.0
SYSTEM_REPAIR_RADIUS = 50.0

# Camera settings
CAMERA_DEFAULT_DISTANCE_THIRD = 350  # Default zoom
CAMERA_DEFAULT_HEIGHT_THIRD = 180  # Default height
CAMERA_MIN_DISTANCE_THIRD = 150
CAMERA_MAX_DISTANCE_THIRD = 600
CAMERA_MIN_HEIGHT_THIRD = 50
CAMERA_MAX_HEIGHT_THIRD = 400
CAMERA_ZOOM_SPEED = 50.0  # Units per key press
CAMERA_ORBIT_SPEED = 5.0  # Degrees per key press
CAMERA_HEIGHT_ADJUST_SPEED = 20.0  # Units per key press
CAMERA_HEIGHT_FIRST = 35  # Eye height for first person (relative to player base z=0)

# Enemy types and their properties - Reduced speeds, adjusted radii
ENEMY_TYPES = {
    "scout": {
        "health": 20,
        "speed": 110.0,
        "damage": 5,
        "points": 10,
        "size": 15.0,
        "radius": 18.0,
        "shoot_range": 0,
        "fire_rate": 0,
    },  # Slower
    "tank": {
        "health": 50,
        "speed": 60.0,
        "damage": 10,
        "points": 20,
        "size": 30.0,
        "radius": 30.0,
        "shoot_range": 0,
        "fire_rate": 0,
    },  # Slower
    "sniper": {
        "health": 30,
        "speed": 0.0,
        "damage": 15,
        "points": 30,
        "size": 25.0,
        "radius": 22.0,
        "shoot_range": 600.0,
        "fire_rate": 1.5,
    },
    
    # ... (existing enemies)
    "drone": {"health": 15, 
              "speed": 80.0, 
              "damage": 10, 
              "points": 15, 
              "size": 20.0, 
              "radius": 20.0, 
              "shoot_range": 0, 
              "fire_rate": 0, 
              "altitude": 100.0},
}


# Colors - Changed System color
COLORS = {
    "player_body": (0.2, 0.5, 1.0),
    "player_head": (1.0, 0.8, 0.6),
    "gun": (0.4, 0.4, 0.4),
    "bullet": (1.0, 1.0, 0.0),
    "muzzle_flash": (1.0, 0.8, 0.2),
    "enemy_scout": (0.0, 0.0, 0.0),
    "enemy_tank": (0.0, 0.0, 0.0),
    "enemy_sniper": (0.0, 0.0, 0.0),
    "enemy_bullet": (0.9, 0.1, 0.1),
    "health_pack": (0.0, 1.0, 0.0),
    "ammo_pack": (0.0, 0.0, 1.0),
    "system": (0.8, 0.0, 0.8),  # Changed to Purple
    "system_repaired": (0.0, 1.0, 0.0),
    "wall": (1.0, 0.75, 0.8),
    "floor1": (0.7, 0.7, 0.7),
    "floor2": (0.4, 0.4, 0.4),
    "text": (1.0, 1.0, 1.0),
    "upgrade_text": (0.9, 0.9, 0.3),
    "repair_bar_bg": (0.4, 0.4, 0.4),
    "repair_bar_fg": (1.0, 0.0, 0.0),
    "crosshair": (1.0, 1.0, 1.0, 0.8),  # White, slightly transparent
}

# Level layouts - Expanded to 15x15
# (0=empty, 1=wall, 2=system)
LEVEL_LAYOUTS = [
    # Level 1: Larger simple area with 2 systems
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # Level 2: Larger complex layout with 3 systems
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 2, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # Level 3: Larger complex maze with 3 systems
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [1, 2, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 2, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
]


# --- Global Game State ---
player = {}
enemies = []
systems = []
powerups = []
bullets = []
enemy_bullets = []

level = 1
score = 0
system_being_repaired = None  # Add with other global variables
upgrading = False
repairing = False
repair_timer = 0.0
game_over = False
level_complete = False
points_available = 0
last_player_enemy_collision_time = {}  # Track last collision time per enemy index

# Camera state
camera_mode = "third"  # "first" or "third"
# Third person specific camera controls state
camera_orbit_angle_offset = 0.0  # Offset relative to player's facing angle
camera_current_distance = CAMERA_DEFAULT_DISTANCE_THIRD
camera_current_height = CAMERA_DEFAULT_HEIGHT_THIRD

# Input state
keys_pressed = set()  # Store currently pressed keys
special_keys_pressed = set()  # Store currently pressed special keys (arrows)

# Timing
last_frame_time = 0.0
show_muzzle_flash_until = 0.0  # Time when muzzle flash should disappear


# --- Utility Functions ---
def get_level_bounds():
    """Returns the boundaries of the current level."""
    layout_index = min(level - 1, len(LEVEL_LAYOUTS) - 1)
    layout = LEVEL_LAYOUTS[layout_index]
    rows = len(layout)
    cols = len(layout[0])
    return 0, cols * CELL_SIZE, 0, rows * CELL_SIZE


def is_wall(x, y):
    """Checks if the given world coordinates are inside a wall."""
    min_x, max_x, min_y, max_y = get_level_bounds()
    if not (min_x <= x < max_x and min_y <= y < max_y):
        return True

    layout_index = min(level - 1, len(LEVEL_LAYOUTS) - 1)
    layout = LEVEL_LAYOUTS[layout_index]
    cell_x = int(x / CELL_SIZE)
    cell_y = int(y / CELL_SIZE)

    if 0 <= cell_y < len(layout) and 0 <= cell_x < len(layout[0]):
        return layout[cell_y][cell_x] == 1
    return True


def distance(x1, y1, x2, y2):
    """Calculates Euclidean distance between two points."""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
def distance_3d(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


# --- Initialization ---
def reset_level():
    """Resets the state for the current or next level."""
    global player, enemies, systems, powerups, bullets, enemy_bullets
    global repair_timer, repairing, level_complete, last_player_enemy_collision_time
    global camera_orbit_angle_offset, camera_current_distance, camera_current_height  # Reset camera offsets

    if level > len(LEVEL_LAYOUTS):
        print(
            f"Attempting to load level {level}, max is {len(LEVEL_LAYOUTS)}. Resetting game."
        )
        reset_game()
        return

    current_layout = LEVEL_LAYOUTS[level - 1]
    rows = len(current_layout)
    cols = len(current_layout[0])

    start_x, start_y = -1, -1
    for r in range(rows):
        for c in range(cols):
            if current_layout[r][c] == 0:
                start_x = c * CELL_SIZE + CELL_SIZE / 2
                start_y = r * CELL_SIZE + CELL_SIZE / 2
                break
        if start_x != -1:
            break

    player["x"] = start_x if start_x != -1 else cols * CELL_SIZE / 2
    player["y"] = start_y if start_y != -1 else rows * CELL_SIZE / 2
    player["z"] = 0
    player["angle"] = 0

    player["ammo"] = player.get("max_ammo", 20)

    enemies.clear()
    systems.clear()
    powerups.clear()
    bullets.clear()
    enemy_bullets.clear()
    repair_timer = 0.0
    repairing = False
    level_complete = False
    last_player_enemy_collision_time.clear()

    # Reset camera view offsets for the new level
    camera_orbit_angle_offset = 0.0
    camera_current_distance = CAMERA_DEFAULT_DISTANCE_THIRD
    camera_current_height = CAMERA_DEFAULT_HEIGHT_THIRD

    for y, row in enumerate(current_layout):
        for x, cell in enumerate(row):
            if cell == 2:
                systems.append(
                    {
                        "x": x * CELL_SIZE + CELL_SIZE / 2,
                        "y": y * CELL_SIZE + CELL_SIZE / 2,
                        "z": 0,
                        "repaired": False,
                    }
                )

    # Spawn initial enemies - Reduced counts
    spawn_count = {
        "scout": 2 + level * 1,  # Reduced scout count
        "tank": max(0, level - 1) * 1,  # Reduced tank count
        "sniper": max(0, level - 2) * 1,  # Sniper starts later
        "drone": level * 2,
    }

    for enemy_type, count in spawn_count.items():
        if count > 0:
            for _ in range(count):
                spawn_enemy(enemy_type)


def reset_game():
    """Resets the entire game state to start from level 1."""
    global player, level, score, upgrading, game_over, points_available, last_frame_time, level_complete
    global camera_orbit_angle_offset, camera_current_distance, camera_current_height  # Reset camera

    player = {
        "x": 0,
        "y": 0,
        "z": 0,
        "angle": 0,
        "pitch": 0.0,
        "health": 100,
        "max_health": 100,
        "ammo": 20,
        "max_ammo": 20,
        "fire_rate": 0.5,
        "shield": 0,
        "max_shield": 0,
        "last_shot_time": 0.0,
    }

    level = 1
    score = 0
    upgrading = False
    game_over = False
    level_complete = False
    points_available = 0
    last_frame_time = time.time()

    # Reset camera view offsets
    camera_orbit_angle_offset = 0.0
    camera_current_distance = CAMERA_DEFAULT_DISTANCE_THIRD
    camera_current_height = CAMERA_DEFAULT_HEIGHT_THIRD

    reset_level()


def spawn_enemy(enemy_type):
    """Spawns an enemy of a given type at a valid location."""
    if level > len(LEVEL_LAYOUTS):
        return

    layout = LEVEL_LAYOUTS[level - 1]
    rows = len(layout)
    cols = len(layout[0])
    min_dist_from_player = CELL_SIZE * 4  # Increase min spawn distance slightly

    attempts = 0
    while attempts < 100:
        attempts += 1
        x_cell = random.randint(0, cols - 1)
        y_cell = random.randint(0, rows - 1)

        if layout[y_cell][x_cell] == 0:
            spawn_x = x_cell * CELL_SIZE + CELL_SIZE / 2
            spawn_y = y_cell * CELL_SIZE + CELL_SIZE / 2

            if (
                distance(player["x"], player["y"], spawn_x, spawn_y)
                >= min_dist_from_player
            ):
                enemies.append({
                      "type": enemy_type,
                       "x": spawn_x,
                       "y": spawn_y,
                       "z": ENEMY_TYPES[enemy_type].get("altitude", 0),
                       "health": ENEMY_TYPES[enemy_type]["health"],
                       "angle": random.uniform(0, 360),
                       "last_shot_time": 0.0,
})
                
                return
    print(
        f"Warning: Could not find valid spawn location for {enemy_type} after {attempts} attempts."
    )


def spawn_powerup(x, y):
    """Spawns a random powerup at the given location."""
    powerup_type = random.choice(["health", "ammo"])
    powerups.append({"type": powerup_type, "x": x, "y": y, "z": 15, "rotation": 0.0})


# --- Drawing Functions ---
def draw_player():
    """Draws the player model and muzzle flash."""
    global show_muzzle_flash_until
    current_time = time.time()

    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])
    glRotatef(player["angle"], 0, 0, 1)

    body_height = 60
    head_radius = 15
    gun_length = 50
    gun_radius = 6
    gun_pos_forward = 10
    gun_pos_right = 15
    gun_pos_up = body_height * 0.55

    # Body
    glColor3f(*COLORS["player_body"])
    glPushMatrix()
    glTranslatef(0, 0, body_height / 2)
    glScalef(30, 30, body_height)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    glColor3f(*COLORS["player_head"])
    glPushMatrix()
    glTranslatef(0, 0, body_height + head_radius * 0.8)
    glutSolidSphere(head_radius, 20, 20)
    glPopMatrix()

    # Gun
    glPushMatrix()
    glTranslatef(gun_pos_forward, gun_pos_right, gun_pos_up)
    glColor3f(*COLORS["gun"])
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), gun_radius, gun_radius, gun_length, 10, 10)
    # Gun tip cube
    glTranslatef(0, 0, gun_length)
    glScalef(gun_radius * 1.5, gun_radius * 1.5, gun_radius * 1.5)
    glutSolidCube(1)
    glPopMatrix()  # Gun transform

    # Muzzle Flash (if active)
    if current_time < show_muzzle_flash_until:
        glPushMatrix()
        # Position flash at the gun tip
        flash_x = gun_pos_forward + gun_length * math.cos(
            math.radians(0)
        )  # Gun points along local X before rotation
        flash_y = gun_pos_right
        flash_z = gun_pos_up
        # Apply gun rotation to flash position relative to player center
        # This part is tricky without matrix math, approximate:
        # Flash should be at the end of the gun barrel in world space
        # Calculate world offset based on player angle
        angle_rad = math.radians(player["angle"])
        gun_world_offset_x = (
            math.cos(angle_rad) * (gun_pos_forward + gun_length)
            - math.sin(angle_rad) * gun_pos_right
        )
        gun_world_offset_y = (
            math.sin(angle_rad) * (gun_pos_forward + gun_length)
            + math.cos(angle_rad) * gun_pos_right
        )

        # We draw relative to player, so just use the local gun tip position
        glTranslatef(
            gun_pos_forward + gun_length, gun_pos_right, gun_pos_up
        )  # Position at tip
        glColor3f(*COLORS["muzzle_flash"])
        glutSolidSphere(gun_radius * 1.8, 8, 8)  # Slightly larger than barrel
        glPopMatrix()

    # Shield
    if player.get("shield", 0) > 0:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        alpha = 0.2 + 0.3 * (player["shield"] / player.get("max_shield", 1))
        glColor4f(0.3, 0.6, 1.0, alpha)
        glPushMatrix()
        glTranslatef(0, 0, body_height / 2 + 5)
        glutSolidSphere(PLAYER_RADIUS + 15, 20, 20)
        glPopMatrix()
        glDisable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 1.0)

    glPopMatrix()  # Player base transform


def draw_enemy(enemy):
    """Draws a single enemy based on its type."""
    enemy_type = enemy["type"]
    props = ENEMY_TYPES[enemy_type]
    size = props["size"]

    glPushMatrix()
    glTranslatef(enemy["x"], enemy["y"], enemy["z"])
    glRotatef(enemy["angle"], 0, 0, 1)

    if enemy_type == "scout":
        glColor3f(*COLORS["enemy_scout"])
        glPushMatrix()
        glTranslatef(0, 0, size * 0.7)
        glutSolidSphere(size, 16, 16)
        glPopMatrix()
    elif enemy_type == "tank":
        glColor3f(*COLORS["enemy_tank"])
        glPushMatrix()
        glTranslatef(0, 0, size / 2)
        glScalef(size, size, size)
        glutSolidCube(1)
        glPopMatrix()
    elif enemy_type == "drone":
        glPushMatrix()
        # Slight hover animation
        hover_offset = math.sin(time.time() * 4) * 2  # Small up-down motion
        glTranslatef(0, 0, hover_offset)
        # Central body (cylinder)
        glColor3f(1.0, 0.0, 0.0)  # Red for drone body
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), size * 0.4, size * 0.4, size * 0.3, 16, 16)
        glPopMatrix()
        # Rotor arms (4 arms at 90-degree intervals)
        glColor3f(0.7, 0.0, 0.0)  # Darker red for arms
        for angle in [0, 90, 180, 270]:
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(size * 0.6, 0, size * 0.15)
            glScalef(size * 0.4, size * 0.1, size * 0.1)
            glutSolidCube(1)
            glPopMatrix()
        # Rotors (discs at end of arms)
        glColor3f(0.5, 0.5, 0.5)  # Gray for rotors
        for angle in [0, 90, 180, 270]:
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(size * 0.6, 0, size * 0.25)
            gluDisk(gluNewQuadric(), 0, size * 0.3, 16, 1)
            glPopMatrix()
        glPopMatrix()
    elif enemy_type == "sniper":
        glColor3f(*COLORS["enemy_sniper"])
        cylinder_height = size * 1.8
        cylinder_radius = size * 0.5
        eye_radius = size * 0.4
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(
            gluNewQuadric(), cylinder_radius, cylinder_radius, cylinder_height, 10, 10
        )
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, cylinder_height + eye_radius * 0.5)
        glutSolidSphere(eye_radius, 10, 10)
        glPopMatrix()

    glPopMatrix()


def draw_bullet(bullet, is_enemy=False):
    """Draws a bullet."""
    glPushMatrix()
    glTranslatef(bullet["x"], bullet["y"], bullet["z"])
    if is_enemy:
        glColor3f(*COLORS["enemy_bullet"])
        glutSolidSphere(BULLET_SIZE * 0.8, 8, 8)  # Enemy bullets slightly smaller
    else:
        glColor3f(*COLORS["bullet"])
        glutSolidSphere(BULLET_SIZE, 8, 8)  # Use constant size
    glPopMatrix()


def draw_system(system):
    """Draws a repairable system."""
    system_size = 40
    glPushMatrix()
    glTranslatef(system["x"], system["y"], system["z"])
    if system["repaired"]:
        glColor3f(*COLORS["system_repaired"])
    else:
        glColor3f(*COLORS["system"])  # Use updated color
    glPushMatrix()
    glTranslatef(0, 0, system_size / 2)
    glScalef(system_size, system_size, system_size)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()


def draw_powerup(powerup):
    """Draws a powerup."""
    glPushMatrix()
    glTranslatef(powerup["x"], powerup["y"], powerup["z"])
    glRotatef(powerup["rotation"], 0, 0, 1)

    if powerup["type"] == "health":
        glColor3f(*COLORS["health_pack"])
        glutSolidCube(20)
    elif powerup["type"] == "ammo":
        glColor3f(*COLORS["ammo_pack"])
        glutSolidSphere(12, 10, 10)

    glPopMatrix()


def draw_level():
    """Draws the walls and floor of the current level."""
    if level > len(LEVEL_LAYOUTS):
        return

    layout = LEVEL_LAYOUTS[level - 1]
    rows = len(layout)
    cols = len(layout[0])
    wall_height = CELL_SIZE * 0.9

    for y in range(rows):
        for x in range(cols):
            cell = layout[y][x]
            x_pos = x * CELL_SIZE
            y_pos = y * CELL_SIZE

            if cell == 1:
                glColor3f(*COLORS["wall"])
                glPushMatrix()
                glTranslatef(
                    x_pos + CELL_SIZE / 2, y_pos + CELL_SIZE / 2, wall_height / 2
                )
                glScalef(CELL_SIZE, CELL_SIZE, wall_height)
                glutSolidCube(1)
                glPopMatrix()
            else:
                if ((x + y) // 1) % 2 == 0:  # Ensure integer division for index
                    glColor3f(*COLORS["floor1"])
                else:
                    glColor3f(*COLORS["floor2"])

                glBegin(GL_QUADS)
                glVertex3f(x_pos, y_pos, 0)
                glVertex3f(x_pos + CELL_SIZE, y_pos, 0)
                glVertex3f(x_pos + CELL_SIZE, y_pos + CELL_SIZE, 0)
                glVertex3f(x_pos, y_pos + CELL_SIZE, 0)
                glEnd()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=COLORS["text"]):
    """Draws text on the screen using GLUT bitmap fonts."""
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))


def draw_crosshair():
    """Draws a simple 2D crosshair in the center of the screen."""
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    center_x = win_w / 2
    center_y = win_h / 2
    size = 10  # Size of the crosshair lines

    glColor4f(*COLORS["crosshair"])  # Use color with alpha
    glLineWidth(2.0)  # Make lines thicker

    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(center_x - size, center_y)
    glVertex2f(center_x + size, center_y)
    # Vertical line
    glVertex2f(center_x, center_y - size)
    glVertex2f(center_x, center_y + size)
    glEnd()


def draw_ui():
    """Draws the 2D UI elements."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    gluOrtho2D(0, win_w, 0, win_h)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    # Enable blending for crosshair transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # --- Draw Standard UI ---
    draw_text(10, win_h - 30, f"Level: {level}")
    draw_text(
        10, win_h - 60, f"Health: {player['health']}/{player.get('max_health', 100)}"
    )
    draw_text(10, win_h - 90, f"Ammo: {player['ammo']}/{player.get('max_ammo', 20)}")
    draw_text(10, win_h - 120, f"Score: {score}")
    if player.get("shield", 0) > 0:
        draw_text(
            10, win_h - 150, f"Shield: {player['shield']}/{player.get('max_shield', 0)}"
        )

    systems_remaining = sum(1 for s in systems if not s["repaired"])
    objective_text = f"Systems Left: {systems_remaining}"
    draw_text(win_w - 160, win_h - 30, objective_text)

    # --- Draw Repair Bar ---
    if repairing:
        bar_width = 200
        bar_height = 20
        bar_x = (win_w - bar_width) / 2
        bar_y = 50
        progress = min(1.0, repair_timer / REPAIR_TIME)

        glColor3f(*COLORS["repair_bar_bg"])
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        glColor3f(*COLORS["repair_bar_fg"])
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width * progress, bar_y)
        glVertex2f(bar_x + bar_width * progress, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        draw_text(
            bar_x + bar_width / 2 - 40,
            bar_y + bar_height / 2 - 5,
            "REPAIRING...",
            GLUT_BITMAP_HELVETICA_12,
        )

    # --- Draw Crosshair (only in first person) ---
    if camera_mode == "first":
        draw_crosshair()

    # --- Restore OpenGL state ---
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()  # Modelview
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()  # Projection
    glMatrixMode(GL_MODELVIEW)


def draw_game_over_screen():
    """Draws the game over message."""
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    center_x = win_w / 2
    center_y = win_h / 2
    draw_text(
        center_x - 80,
        center_y + 50,
        "GAME OVER",
        GLUT_BITMAP_TIMES_ROMAN_24,
        (1.0, 0.0, 0.0),
    )
    draw_text(center_x - 100, center_y, f"You reached level {level}")
    draw_text(center_x - 90, center_y - 30, f"Final Score: {score}")
    draw_text(center_x - 100, center_y - 80, "Press 'R' to restart")


def draw_level_complete_screen():
    """Draws the level complete message."""
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    center_x = win_w / 2
    center_y = win_h / 2
    draw_text(
        center_x - 120,
        center_y + 50,
        "LEVEL COMPLETE!",
        GLUT_BITMAP_TIMES_ROMAN_24,
        (0.0, 1.0, 0.0),
    )
    draw_text(center_x - 100, center_y, "All systems repaired")
    draw_text(center_x - 140, center_y - 50, "Press SPACE for Upgrade Menu")


def draw_upgrade_menu():
    """Draws the upgrade selection menu."""
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    center_x = win_w / 2
    y_pos = win_h * 0.8
    draw_text(
        center_x - 100,
        y_pos,
        "UPGRADE MENU",
        GLUT_BITMAP_TIMES_ROMAN_24,
        color=COLORS["upgrade_text"],
    )
    y_pos -= 50
    draw_text(
        center_x - 150,
        y_pos,
        f"Points Available: {points_available}",
        color=COLORS["upgrade_text"],
    )
    y_pos -= 50
    draw_text(
        center_x - 150,
        y_pos,
        "1. Faster Fire Rate (50 pts)",
        color=COLORS["upgrade_text"],
    )
    y_pos -= 40
    draw_text(
        center_x - 150,
        y_pos,
        "2. Increase Max Ammo (+10) (30 pts)",
        color=COLORS["upgrade_text"],
    )
    y_pos -= 40
    draw_text(
        center_x - 150,
        y_pos,
        "3. Increase Max Health (+25) (40 pts)",
        color=COLORS["upgrade_text"],
    )
    y_pos -= 40
    draw_text(
        center_x - 150,
        y_pos,
        "4. Add/Improve Shield (+50 Max) (80 pts)",
        color=COLORS["upgrade_text"],
    )
    y_pos -= 60
    draw_text(
        center_x - 150,
        y_pos,
        "Press 1, 2, 3, or 4 to upgrade",
        color=COLORS["upgrade_text"],
    )
    draw_text(
        center_x - 150,
        y_pos - 30,
        "Press SPACE to skip and continue",
        color=COLORS["upgrade_text"],
    )


import math
import time

# Global variables assumed to be defined elsewhere
last_print_time = 0  # To limit repair progress prints

def update_player(dt):
    """Updates player state: movement and repair actions with debug output."""
    global repairing, repair_timer, system_being_repaired, last_print_time

    # --- Movement (only if not currently repairing) ---
    if not repairing:
        move_forward = 0
        move_strafe = 0
        if b"w" in keys_pressed:
            move_forward += 1
        if b"s" in keys_pressed:
            move_forward -= 1
        if b"a" in keys_pressed:
            move_strafe -= 1
        if b"d" in keys_pressed:
            move_strafe += 1

        if move_forward != 0 or move_strafe != 0:
            angle_rad = math.radians(player["angle"])
            forward_dx = math.cos(angle_rad)
            forward_dy = math.sin(angle_rad)
            strafe_dx = math.cos(angle_rad + math.pi / 2)
            strafe_dy = math.sin(angle_rad + math.pi / 2)
            final_dx_intent = move_forward * forward_dx + move_strafe * strafe_dx
            final_dy_intent = move_forward * forward_dy + move_strafe * strafe_dy
            magnitude = math.sqrt(final_dx_intent**2 + final_dy_intent**2)

            if magnitude > 0:
                norm_dx = final_dx_intent / magnitude
                norm_dy = final_dy_intent / magnitude
                delta_dist = PLAYER_SPEED * dt
                delta_x = norm_dx * delta_dist
                delta_y = norm_dy * delta_dist
                potential_x = player["x"] + delta_x
                potential_y = player["y"] + delta_y

                if not is_wall(potential_x, potential_y):
                    player["x"] = potential_x
                    player["y"] = potential_y
                else:
                    if not is_wall(potential_x, player["y"]):
                        player["x"] = potential_x
                    elif not is_wall(player["x"], potential_y):
                        player["y"] = potential_y

    # --- Repair Action Logic with Debug Prints ---
    if repairing:
        # Continue or interrupt an ongoing repair
        if (
            b"r" in keys_pressed
            and system_being_repaired is not None
            and distance(
                player["x"], player["y"],
                system_being_repaired["x"], system_being_repaired["y"],
            ) < SYSTEM_REPAIR_RADIUS
        ):
            repair_timer += dt
            # Print repair progress every second
            current_time = time.time()
            if current_time - last_print_time >= 1.0:
                print(f"Repairing... {repair_timer:.1f}/{REPAIR_TIME} seconds")
                last_print_time = current_time
            # Once done, mark repaired and reset state
            if repair_timer >= REPAIR_TIME:
                system_being_repaired["repaired"] = True
                print(
                    f"Repair complete on system at "
                    f"({system_being_repaired['x']:.0f}, {system_being_repaired['y']:.0f})!"
                )
                repairing = False
                repair_timer = 0.0
                system_being_repaired = None
                check_level_complete()
        else:
            # Interrupted (ran out of range or released 'r')
            print("Repair interrupted!")
            repairing = False
            repair_timer = 0.0
            system_being_repaired = None

    # --- Start a new repair if not already repairing ---
    elif b"r" in keys_pressed:
        target_system = None
        closest_dist_sq = SYSTEM_REPAIR_RADIUS**2
        for system_candidate in systems:
            if not system_candidate.get("repaired", False):
                dx = player["x"] - system_candidate["x"]
                dy = player["y"] - system_candidate["y"]
                dist_sq = dx*dx + dy*dy
                if dist_sq < closest_dist_sq:
                    target_system = system_candidate
                    closest_dist_sq = dist_sq

        if target_system is not None:
            repairing = True
            repair_timer = 0.0
            system_being_repaired = target_system
            print(
                f"Starting repair on system at "
                f"({target_system['x']:.0f}, {target_system['y']:.0f})"
            )
            last_print_time = time.time()  # Reset for progress tracking


def update_enemies(dt):
    """Updates enemy state: movement, AI, shooting."""
    global player, enemies, score, game_over, last_player_enemy_collision_time, points_available

    current_time = time.time()

    for i in range(len(enemies) - 1, -1, -1):
        enemy = enemies[i]
        enemy_type = enemy["type"]
        props = ENEMY_TYPES[enemy_type]
        speed = props["speed"]  # Uses updated slower speeds
        radius = props["radius"]

        dx = player["x"] - enemy["x"]
        dy = player["y"] - enemy["y"]
        dist_to_player_sq = dx**2 + dy**2
        dist_to_player = math.sqrt(dist_to_player_sq)

        # AI Behavior
        if enemy_type == "sniper":
            if dist_to_player > 0:
                enemy["angle"] = math.degrees(math.atan2(dy, dx))
            shoot_range_sq = props["shoot_range"] ** 2
            fire_rate = props["fire_rate"]
            if (
                dist_to_player_sq <= shoot_range_sq
                and current_time - enemy["last_shot_time"] >= fire_rate
            ):
                angle_rad = math.radians(enemy["angle"])
                bullet_dx = math.cos(angle_rad) * ENEMY_BULLET_SPEED
                bullet_dy = math.sin(angle_rad) * ENEMY_BULLET_SPEED
                eye_height = props["size"] * 1.8
                enemy_bullets.append(
                    {
                        "x": enemy["x"],
                        "y": enemy["y"],
                        "z": eye_height,
                        "dx": bullet_dx,
                        "dy": bullet_dy,
                        "damage": props["damage"],
                    }
                )
                enemy["last_shot_time"] = current_time
        else:  # Scout and Tank
            if dist_to_player_sq > (radius * 1.5) ** 2 and dist_to_player > 0:
                enemy["angle"] = math.degrees(math.atan2(dy, dx))
                move_dist = speed * dt
                move_dx = (dx / dist_to_player) * move_dist
                move_dy = (dy / dist_to_player) * move_dist
                potential_x = enemy["x"] + move_dx
                potential_y = enemy["y"] + move_dy
                if not is_wall(potential_x, potential_y):
                    enemy["x"] = potential_x
                    enemy["y"] = potential_y

        # Collision with Player
        collision_dist = PLAYER_RADIUS + radius
        if dist_to_player < collision_dist:
            last_collision = last_player_enemy_collision_time.get(i, 0)
            if current_time - last_collision > ENEMY_COLLISION_DAMAGE_INTERVAL:
                damage = props["damage"]
                if player.get("shield", 0) > 0:
                    shield_damage = min(player["shield"], damage)
                    player["shield"] -= shield_damage
                    damage -= shield_damage
                if damage > 0:
                    player["health"] -= damage
                last_player_enemy_collision_time[i] = current_time
                if player["health"] <= 0:
                    player["health"] = 0
                    game_over = True


def update_bullets(dt):
    """Updates bullet positions and handles collisions."""
    global bullets, enemies, score, enemy_bullets, player, game_over, points_available

    min_x, max_x, min_y, max_y = get_level_bounds()

    # Update Player Bullets
    for i in range(len(bullets) - 1, -1, -1):
        bullet = bullets[i]
        bullet["x"] += bullet["dx"] * dt
        bullet["y"] += bullet["dy"] * dt
        bullet["z"] += bullet["dz"] * dt

        if is_wall(bullet["x"], bullet["y"]):
            bullets.pop(i)
            continue

        hit_enemy = False
        for j in range(len(enemies) - 1, -1, -1):
            enemy = enemies[j]
            props = ENEMY_TYPES[enemy["type"]]
            radius = props["radius"]
            if distance_3d(bullet["x"], bullet["y"], bullet["z"], enemy["x"], enemy["y"], enemy["z"]) < props["radius"]:
                enemy["health"] -= BULLET_DAMAGE
                bullets.pop(i)
                hit_enemy = True
                if enemy["health"] <= 0:
                    score += props["points"]
                    points_available += props["points"]
                    spawn_powerup(enemy["x"], enemy["y"])
                    enemies.pop(j)
                    if j in last_player_enemy_collision_time:
                        del last_player_enemy_collision_time[j]
                break
        if hit_enemy:
            continue

        if not (min_x <= bullet["x"] < max_x and min_y <= bullet["y"] < max_y):
            bullets.pop(i)
            continue

    # Update Enemy Bullets
    for i in range(len(enemy_bullets) - 1, -1, -1):
        bullet = enemy_bullets[i]
        bullet["x"] += bullet["dx"] * dt
        bullet["y"] += bullet["dy"] * dt

        if is_wall(bullet["x"], bullet["y"]):
            enemy_bullets.pop(i)
            continue

        if distance(bullet["x"], bullet["y"], player["x"], player["y"]) < PLAYER_RADIUS:
            damage = bullet["damage"]
            if player.get("shield", 0) > 0:
                shield_damage = min(player["shield"], damage)
                player["shield"] -= shield_damage
                damage -= shield_damage
            if damage > 0:
                player["health"] -= damage
            enemy_bullets.pop(i)
            if player["health"] <= 0:
                player["health"] = 0
                game_over = True
            continue

        if not (min_x <= bullet["x"] < max_x and min_y <= bullet["y"] < max_y):
            enemy_bullets.pop(i)
            continue


def update_powerups(dt):
    """Updates powerup animations and handles player collision."""
    global player, powerups
    for i in range(len(powerups) - 1, -1, -1):
        powerup = powerups[i]
        powerup["rotation"] = (powerup["rotation"] + 60 * dt) % 360
        if (
            distance(player["x"], player["y"], powerup["x"], powerup["y"])
            < POWERUP_PICKUP_RADIUS
        ):
            if powerup["type"] == "health":
                heal_amount = 20
                player["health"] = min(
                    player.get("max_health", 100), player["health"] + heal_amount
                )
            elif powerup["type"] == "ammo":
                ammo_amount = 10
                player["ammo"] = min(
                    player.get("max_ammo", 20), player["ammo"] + ammo_amount
                )
            powerups.pop(i)


def check_level_complete():
    """Checks if all systems are repaired and sets level_complete flag."""
    global level_complete, points_available, score
    if not systems:
        return
    all_repaired = all(s.get("repaired", False) for s in systems)
    if all_repaired and not level_complete:
        level_complete = True
        level_bonus = level * 50
        points_available += level_bonus
        score += level_bonus
        print(f"Level {level} cleared! +{level_bonus} bonus points.")


# --- Input Handling ---
def keyboard_down(key, x, y):
    """Handles key press events."""
    global keys_pressed, game_over, level_complete, upgrading, level
    try:
        processed_key = key.lower()
    except AttributeError:
        processed_key = key
    keys_pressed.add(processed_key)

    if key == b" " or key == b"\x20":
        if level_complete:
            level_complete = False
            upgrading = True
        elif upgrading:
            upgrading = False
            level += 1
            if level > len(LEVEL_LAYOUTS):
                game_over = True  # Win condition
            else:
                reset_level()
    elif processed_key == b"r" and game_over:
        reset_game()
    elif upgrading and b"1" <= key <= b"4":
        try:
            handle_upgrade_selection(int(key))
        except ValueError:
            pass


def keyboard_up(key, x, y):
    """Handles key release events."""
    global keys_pressed
    try:
        processed_key = key.lower()
    except AttributeError:
        processed_key = key
    # Ensure processed_key is a bytes literal for consistency
    if isinstance(processed_key, str):
        processed_key = processed_key.encode()
    if processed_key in keys_pressed:
        keys_pressed.remove(processed_key)


def special_keys_down(key, x, y):
    """Handles special key presses (like arrows)."""
    global special_keys_pressed
    special_keys_pressed.add(key)


def special_keys_up(key, x, y):
    """Handles special key releases."""
    global special_keys_pressed
    if key in special_keys_pressed:
        special_keys_pressed.remove(key)


def update_camera_controls(dt):
    """Updates third person camera based on arrow key input."""
    global camera_orbit_angle_offset, camera_current_distance, camera_current_height

    # Orbit Left/Right
    if GLUT_KEY_LEFT in special_keys_pressed:
        camera_orbit_angle_offset -= CAMERA_ORBIT_SPEED * dt * 60  # Scale speed with dt
    if GLUT_KEY_RIGHT in special_keys_pressed:
        camera_orbit_angle_offset += CAMERA_ORBIT_SPEED * dt * 60

    # Zoom In/Out (Adjust Distance) & Adjust Height
    if GLUT_KEY_UP in special_keys_pressed:
        camera_current_distance -= CAMERA_ZOOM_SPEED * dt * 60
        # camera_current_height += CAMERA_HEIGHT_ADJUST_SPEED * dt * 60 # Optional: Link Up/Down to height too
    if GLUT_KEY_DOWN in special_keys_pressed:
        camera_current_distance += CAMERA_ZOOM_SPEED * dt * 60
        # camera_current_height -= CAMERA_HEIGHT_ADJUST_SPEED * dt * 60 # Optional: Link Up/Down to height too

    # Clamp values
    camera_current_distance = max(
        CAMERA_MIN_DISTANCE_THIRD,
        min(camera_current_distance, CAMERA_MAX_DISTANCE_THIRD),
    )
    camera_current_height = max(
        CAMERA_MIN_HEIGHT_THIRD, min(camera_current_height, CAMERA_MAX_HEIGHT_THIRD)
    )
    camera_orbit_angle_offset %= 360  # Keep angle offset within range


def mouse_click(button, state, x, y):
    """Handles mouse button clicks."""
    global player, bullets, camera_mode, show_muzzle_flash_until

    current_time = time.time()

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
      if upgrading or game_over or level_complete or repairing:
        return
      if player["ammo"] > 0 and current_time - player["last_shot_time"] >= player["fire_rate"]:
        yaw_rad = math.radians(player["angle"])
        pitch_rad = math.radians(player["pitch"])
        dir_x = math.cos(yaw_rad) * math.cos(pitch_rad)
        dir_y = math.sin(yaw_rad) * math.cos(pitch_rad)
        dir_z = math.sin(pitch_rad)
        spawn_x = player["x"]
        spawn_y = player["y"]
        spawn_z = player["z"] + 60 * 0.55
        vel_dx = dir_x * BULLET_SPEED
        vel_dy = dir_y * BULLET_SPEED
        vel_dz = dir_z * BULLET_SPEED
        bullets.append({"x": spawn_x, "y": spawn_y, "z": spawn_z, "dx": vel_dx, "dy": vel_dy, "dz": vel_dz})
        player["ammo"] -= 1
        player["last_shot_time"] = current_time
        show_muzzle_flash_until = current_time + MUZZLE_FLASH_DURATION

    elif player["ammo"] <= 0:
            pass  # Optionally print "Out of ammo!"

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if upgrading or game_over or level_complete:
            return
        camera_mode = "first" if camera_mode == "third" else "third"


def mouse_passive_motion(x, y):
    if upgrading or game_over or level_complete:
        glutSetCursor(GLUT_CURSOR_INHERIT)
        return
    glutSetCursor(GLUT_CURSOR_NONE)
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    center_x = window_width / 2
    center_y = window_height / 2
    delta_x = x - center_x
    delta_y = y - center_y
    if abs(delta_x) > 1 or abs(delta_y) > 1:
        player["angle"] -= delta_x * MOUSE_SENSITIVITY
        player["angle"] %= 360
        player["pitch"] -= delta_y * MOUSE_SENSITIVITY
        player["pitch"] = max(PITCH_MIN, min(PITCH_MAX, player["pitch"]))
        glutWarpPointer(int(center_x), int(center_y))


# --- Upgrade Logic ---
def handle_upgrade_selection(choice):
    """Applies the selected upgrade if affordable."""
    global player, upgrading, points_available, level, game_over

    cost = 0
    success = False

    if choice == 1:
        cost = 50
        if points_available >= cost:
            # Faster Fire Rate
            player["fire_rate"] = max(0.1, player["fire_rate"] * 0.8)
            success = True

    elif choice == 2:
        cost = 30
        if points_available >= cost:
            # Increase Max Ammo
            player["max_ammo"] = player.get("max_ammo", 20) + 10
            player["ammo"] = player["max_ammo"]
            success = True

    elif choice == 3:
        cost = 40
        if points_available >= cost:
            # Increase Max Health
            player["max_health"] = player.get("max_health", 100) + 25
            player["health"] = player["max_health"]
            success = True

    elif choice == 4:
        cost = 80
        if points_available >= cost:
            # Add/Improve Shield
            player["max_shield"] = player.get("max_shield", 0) + 50
            player["shield"] = player["max_shield"]
            success = True

    else:
        # Invalid choice
        return

    if success:
        points_available -= cost
        upgrading = False
        level += 1
        if level > len(LEVEL_LAYOUTS):
            game_over = True
        else:
            reset_level()
    else:
        print(f"Not enough points! Need {cost}, have {points_available}.")



# --- Main Display and Idle Functions ---
def display():
    """The main GLUT display function."""
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if game_over or level_complete or upgrading:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, win_w, 0, win_h)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        if game_over:
            draw_game_over_screen()
        elif level_complete:
            draw_level_complete_screen()
        elif upgrading:
            draw_upgrade_menu()
        glEnable(GL_DEPTH_TEST)
    else:
        # 3D Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = win_w / win_h if win_h > 0 else 1
        fov = 60 if camera_mode == "first" else 45
        near_clip = 0.5 if camera_mode == "first" else 1.0
        far_clip = 3500.0  # Increased far clip for larger levels
        gluPerspective(fov, aspect_ratio, near_clip, far_clip)

        # Camera View
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        player_center_z = player["z"] + 30

        if camera_mode == "third":
            # Calculate the base camera angle (player's facing angle) + orbit offset
            total_orbit_angle = player["angle"] + camera_orbit_angle_offset
            cam_angle_rad = math.radians(total_orbit_angle)
            # Calculate camera position based on player pos, angle, distance, height
            cam_x = player["x"] - camera_current_distance * math.cos(cam_angle_rad)
            cam_y = player["y"] - camera_current_distance * math.sin(cam_angle_rad)
            cam_z = player_center_z + camera_current_height
            target_x = player["x"]
            target_y = player["y"]
            target_z = player_center_z
            gluLookAt(cam_x, cam_y, cam_z, target_x, target_y, target_z, 0, 0, 1)
        elif camera_mode == "first":
          eye_x = player["x"]
          eye_y = player["y"]
          eye_z = player["z"] + CAMERA_HEIGHT_FIRST
          yaw_rad = math.radians(player["angle"])
          pitch_rad = math.radians(player["pitch"])
          dir_x = math.cos(yaw_rad) * math.cos(pitch_rad)
          dir_y = math.sin(yaw_rad) * math.cos(pitch_rad)
          dir_z = math.sin(pitch_rad)
          look_dist = 100
          center_x = eye_x + look_dist * dir_x
          center_y = eye_y + look_dist * dir_y
          center_z = eye_z + look_dist * dir_z
          gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

        # Draw Scene
        glEnable(GL_DEPTH_TEST)
        draw_level()
        draw_player()
        for enemy in enemies:
            draw_enemy(enemy)
        for bullet in bullets:
            draw_bullet(bullet, is_enemy=False)
        for bullet in enemy_bullets:
            draw_bullet(bullet, is_enemy=True)
        for system in systems:
            draw_system(system)
        for powerup in powerups:
            draw_powerup(powerup)
        draw_ui()  # Draw UI overlay

    glutSwapBuffers()


def idle():
    """The GLUT idle function, called when no events are pending."""
    global last_frame_time
    current_time = time.time()
    dt = current_time - last_frame_time
    dt = min(dt, 0.05)  # Clamp dt
    last_frame_time = current_time

    if not game_over and not level_complete and not upgrading:
        update_camera_controls(dt)  # Update camera based on arrow keys
        update_player(dt)
        update_enemies(dt)
        update_bullets(dt)
        update_powerups(dt)

    glutPostRedisplay()


# --- Main Function ---
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Space Station Siege v3")  # Updated title

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glShadeModel(GL_SMOOTH)

    # Register GLUT callbacks
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys_down)  # Register special key down handler
    glutSpecialUpFunc(special_keys_up)  # Register special key up handler
    glutMouseFunc(mouse_click)
    glutPassiveMotionFunc(mouse_passive_motion)
    glutIdleFunc(idle)

    glutSetCursor(GLUT_CURSOR_NONE)
    reset_game()

    print("--- Space Station Siege v3 ---")
    print("Controls:")
    print(" W/S: Move Forward/Backward | A/D: Strafe Left/Right")
    print(" Mouse: Aim | Left Click: Shoot | Right Click: Toggle Camera")
    print(" R (Hold): Repair System | Space: Continue/Skip Upgrade")
    print(
        " Arrow Keys (Third Person): Orbit (Left/Right), Zoom (Up/Down)"
    )  # Updated controls
    print(" 1/2/3/4: Select Upgrade")
    print("----------------------------")

    glutMainLoop()


if __name__ == "__main__":
    main()