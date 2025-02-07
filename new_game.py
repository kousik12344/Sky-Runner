import pygame
import random
import cv2
import mediapipe as mp
import threading
import os
import numpy as np

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
GROUND_HEIGHT = HEIGHT - 50
PARTICLE_LIFETIME = 10
FPS = 30

# Cloud properties
CLOUD_WIDTH, CLOUD_HEIGHT = 100, 50
clouds = []
for _ in range(3):  # Create 3 clouds
    clouds.append(pygame.Rect(random.randint(WIDTH, WIDTH + 200), random.randint(50, 150), CLOUD_WIDTH, CLOUD_HEIGHT))

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Runner")

# Player properties
player = pygame.Rect(100, GROUND_HEIGHT - 50, 40, 50)
player_speed = 5
jump_power = -12
gravity = 0.5
velocity_y = 0
is_jumping = False
shield = False
speed_boost = False
double_points = False

# Power-up durations
powerup_durations = {
    "shield": 10 * FPS,  # 10 seconds
    "speed_boost": 10 * FPS,
    "double_points": 10 * FPS
}

# Animation properties
animation_frames = 2  # Number of frames for the animation
current_frame = 0
frame_counter = 0
frame_delay = 10  # Delay between frame updates

# Obstacle properties
obstacles = [pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30)]
obstacle_speed = 5  # Define obstacle_speed here

# Power-up properties
powerups = []
POWERUP_TYPES = ["shield", "speed_boost", "double_points"]
POWERUP_SIZE = 20

# Particle effects
particles = []
def add_particles():
    for _ in range(5):
        particles.append([[player.x + 20, player.y + 50], [random.randint(-2, 2), random.randint(-2, 0)], PARTICLE_LIFETIME])

def update_particles():
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 1
        if particle[2] <= 0:
            particles.remove(particle)

# Score, Level, and High Score
score = 0
level = 1
high_score = 0
font = pygame.font.SysFont(None, 36)

# Load high score from file
def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            return int(file.read())
    return 0

# Save high score to file
def save_high_score(high_score):
    with open("high_score.txt", "w") as file:
        file.write(str(high_score))

# Initialize high score
high_score = load_high_score()

# Function to draw score and level
def draw_score_and_level():
    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 150, 10))
    screen.blit(high_score_text, (10, 50))  # Display high score below the current score

# Function to draw active power-ups
def draw_active_powerups():
    powerup_texts = []
    if shield:
        powerup_texts.append("Shield")
    if speed_boost:
        powerup_texts.append("Speed Boost")
    if double_points:
        powerup_texts.append("Double Points")

    for i, text in enumerate(powerup_texts):
        powerup_surface = font.render(text, True, BLACK)
        screen.blit(powerup_surface, (10, 100 + i * 30))

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.8,  # Increase for better detection accuracy
    min_tracking_confidence=0.8,   # Increase for better tracking accuracy
    max_num_hands=2
)

# OpenCV camera setup
cap = cv2.VideoCapture(0)

# Hand detection thread
results = None
def hand_detection_thread():
    global results
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (320, 240))  # Reduce resolution for faster processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

# Start the thread
threading.Thread(target=hand_detection_thread, daemon=True).start()

# Function to spawn power-ups
def spawn_powerup():
    powerup_type = random.choice(POWERUP_TYPES)
    powerup = pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 50, POWERUP_SIZE, POWERUP_SIZE)
    powerups.append((powerup, powerup_type))

landmark_buffer = []

def smooth_landmarks(landmarks, buffer_size=5):
    global landmark_buffer
    landmark_buffer.append(landmarks)
    if len(landmark_buffer) > buffer_size:
        landmark_buffer.pop(0)
    return np.mean(landmark_buffer, axis=0)

# Function to apply power-ups
def apply_powerup(powerup_type):
    global shield, speed_boost, double_points
    if powerup_type == "shield":
        shield = True
    elif powerup_type == "speed_boost":
        speed_boost = True
    elif powerup_type == "double_points":
        double_points = True

# Function to update power-up durations
def update_powerups():
    global shield, speed_boost, double_points
    if shield:
        powerup_durations["shield"] -= 1
        if powerup_durations["shield"] <= 0:
            shield = False
            powerup_durations["shield"] = 10 * FPS
    if speed_boost:
        powerup_durations["speed_boost"] -= 1
        if powerup_durations["speed_boost"] <= 0:
            speed_boost = False
            powerup_durations["speed_boost"] = 10 * FPS
    if double_points:
        powerup_durations["double_points"] -= 1
        if powerup_durations["double_points"] <= 0:
            double_points = False
            powerup_durations["double_points"] = 10 * FPS

# Function to draw the player with walking animation
def draw_player(x, y, frame):
    # Triangle head (upside down)
    head_points = [(x + 20, y + 10), (x + 10, y), (x + 30, y)]
    pygame.draw.polygon(screen, BLACK, head_points)

    # Rectangle body
    body_rect = pygame.Rect(x + 15, y + 10, 10, 20)
    pygame.draw.rect(screen, BLACK, body_rect)

    # Arms (alternate between frames for animation)
    if frame == 0:
        pygame.draw.line(screen, BLACK, (x + 15, y + 15), (x + 5, y + 25), 2)  # Left arm up
        pygame.draw.line(screen, BLACK, (x + 25, y + 15), (x + 35, y + 25), 2)  # Right arm down
    else:
        pygame.draw.line(screen, BLACK, (x + 15, y + 15), (x + 5, y + 25), 2)  # Left arm down
        pygame.draw.line(screen, BLACK, (x + 25, y + 15), (x + 35, y + 25), 2)  # Right arm up

    # Legs (alternate between frames for animation)
    leg_length = 20  # Fixed leg length
    if frame == 0:
        pygame.draw.line(screen, BLACK, (x + 15, y + 30), (x + 10, y + 30 + leg_length), 2)  # Left leg forward
        pygame.draw.line(screen, BLACK, (x + 25, y + 30), (x + 30, y + 30 + leg_length), 2)  # Right leg backward
    else:
        pygame.draw.line(screen, BLACK, (x + 15, y + 30), (x + 10, y + 30 + leg_length), 2)  # Left leg backward
        pygame.draw.line(screen, BLACK, (x + 25, y + 30), (x + 30, y + 30 + leg_length), 2)  # Right leg forward

# Game over screen
def game_over_screen():
    global score, high_score

    # Update high score if the current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    # Create a font for the game over screen
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 48)

    # Game over loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    game_loop()
                    return
                if event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    return

        # Draw the game over screen
        screen.fill(SKY_BLUE)
        game_over_text = font_large.render("Game Over", True, BLACK)
        score_text = font_medium.render(f"Score: {score}", True, BLACK)
        high_score_text = font_medium.render(f"High Score: {high_score}", True, BLACK)
        restart_text = font_medium.render("Press R to Restart", True, BLACK)
        quit_text = font_medium.render("Press Q to Quit", True, BLACK)

        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 10))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 130))

        pygame.display.update()

# Instruction Screen with Play Button
def instruction_screen():
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 24)

    # Button properties (Moved to the right side)
    card_width, card_height = 200, 80
    card_rect = pygame.Rect(WIDTH - card_width - 50, HEIGHT - 100, card_width, card_height)
    card_color = WHITE
    text_color = BLACK

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if card_rect.collidepoint(mouse_pos):
                    game_loop()  # Start the game directly
                    return

        # Draw the instruction screen
        screen.fill(SKY_BLUE)

        # Draw the title
        title_text = font_large.render("Instructions", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # Instructions
        instructions = [
            "1. Use an open hand gesture to jump.",
            "2. Avoid obstacles to keep running.",
            "3. Collect power-ups for special abilities:",
            "   - Shield: Protects you from one obstacle ('dark blue square').",
            "   - Speed Boost: Increases your speed ('light green square').",
            "   - Double Points: Doubles your score ('orange square').",
            "4. Pause the game by showing two hands.",
            "5. Resume the game by making a fist.",
            "6. Reach the highest score possible!"
        ]

        for i, line in enumerate(instructions):
            instruction_text = font_small.render(line, True, BLACK)
            screen.blit(instruction_text, (50, 100 + i * 30))

        # Draw the "Play" button with shadow
        shadow_rect = card_rect.move(5, 5)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, card_rect, 2, border_radius=10)

        # Draw the text on the button
        font_medium = pygame.font.SysFont(None, 48)
        text_surface = font_medium.render("Play", True, text_color)
        text_rect = text_surface.get_rect(center=card_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.update()


# Update the splash screen to transition to the instruction screen
def splash_screen():
    font_large = pygame.font.SysFont(None, 72)
    title_text = font_large.render("Sky Runner", True, WHITE)
    alpha = 0  # Initial transparency
    fade_speed = 2  # Speed of fade-in

    while alpha < 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Increase alpha for fade-in effect
        alpha += fade_speed
        if alpha > 255:
            alpha = 255

        # Draw the splash screen
        screen.fill(SKY_BLUE)
        title_text.set_alpha(alpha)  # Set transparency
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))

        pygame.display.update()
        pygame.time.delay(30)  # Control the speed of the fade-in

    # Wait for a moment before transitioning to the instruction screen
    pygame.time.delay(1000)
    instruction_screen()  # Transition to the instruction screen

def is_fist(landmarks):
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Check if thumb is close to index and other fingers are folded
    thumb_index_distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    fingers_folded = (
        middle_tip.y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        ring_tip.y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        pinky_tip.y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y
    )
    return thumb_index_distance < 0.1 and fingers_folded

def is_open_hand(landmarks):
    # Check if all fingers are extended
    return (
        landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.PINKY_TIP].y < landmarks[mp_hands.HandLandmark.PINKY_PIP].y
    )

# Game loop
def game_loop():
    global score, level, obstacles, is_jumping, velocity_y, particles, clouds, current_frame, frame_counter, high_score
    global shield, speed_boost, double_points, obstacle_speed  # Declare obstacle_speed as global

    # Reset game state
    score = 0
    level = 1
    obstacles = [pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30)]
    player.x = 100
    player.y = GROUND_HEIGHT - 50
    velocity_y = 0
    is_jumping = False
    particles = []
    clouds = []
    for _ in range(3):
        clouds.append(pygame.Rect(random.randint(WIDTH, WIDTH + 200), random.randint(50, 150), CLOUD_WIDTH, CLOUD_HEIGHT))
    shield = False
    speed_boost = False
    double_points = False

    running = True
    paused = False
    clock = pygame.time.Clock()

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause the game
                    paused = not paused

        # Pause the game if two hands are detected
        if results and results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) == 2:  # Two hands detected
                paused = True

        # Resume the game if right fist is detected
        if results and results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) == 1:  # One hand detected
                landmarks = results.multi_hand_landmarks[0].landmark
                if is_fist(landmarks):  # Check if the hand is a fist
                    paused = False

        if paused:
                # Display "Paused" text
            font_large = pygame.font.SysFont(None, 72)
            paused_text = font_large.render("Paused", True, BLACK)
            paused_rect = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(paused_text, paused_rect)
            pygame.display.update()
            continue

            # Hand gesture detection
        if results and results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            if is_open_hand(landmarks) and not is_jumping:  # Open hand detected
                velocity_y = jump_power
                is_jumping = True
                add_particles()

            # Apply gravity
        velocity_y += gravity
        player.y += velocity_y

            # Collision with ground
        if player.y >= GROUND_HEIGHT - player.height:
            player.y = GROUND_HEIGHT - player.height
            velocity_y = 0
            is_jumping = False

            # Move obstacles
        for obs in obstacles:
            obs.x -= obstacle_speed
            if obs.x < -30:
                obs.x = random.randint(500, 700)
                score += 1  # Increase score when obstacle resets
                if double_points:
                    score += 1  # Add +1 for double points

            # Check collision with obstacles
        for obs in obstacles:
            if player.colliderect(obs):
                if shield:
                    shield = False
                else:
                    game_over_screen()
                    return

            # Spawn power-ups
        if random.randint(1, 100) == 1:  # 1% chance to spawn a power-up
            spawn_powerup()

            # Check collision with power-ups
        for powerup, powerup_type in powerups[:]:
            powerup.x -= obstacle_speed
            if player.colliderect(powerup):
                apply_powerup(powerup_type)
                powerups.remove((powerup, powerup_type))
            elif powerup.x < -POWERUP_SIZE:
                powerups.remove((powerup, powerup_type))

            # Update power-up durations
        update_powerups()

            # Apply power-up effects
        if speed_boost:
            obstacle_speed = 10  # Increase obstacle speed
        else:
            obstacle_speed = 5  # Reset obstacle speed

            # Update particles
        update_particles()

            # Increase level and difficulty
        if score % 10 == 0 and level < score // 10 + 1:
            level += 1
            obstacle_speed += 1
            obstacles.append(pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30))

            # Move clouds
        for cloud in clouds:
            cloud.x -= 2
            if cloud.x < -CLOUD_WIDTH:
                cloud.x = random.randint(WIDTH, WIDTH + 200)
                cloud.y = random.randint(50, 150)

            # Update animation frame
        frame_counter += 1
        if frame_counter >= frame_delay:
            frame_counter = 0
            current_frame = (current_frame + 1) % animation_frames

            # Drawing
        screen.fill(SKY_BLUE)  # Draw sky background
        pygame.draw.rect(screen, GROUND_GREEN, (0, GROUND_HEIGHT, WIDTH, HEIGHT - GROUND_HEIGHT))  # Draw ground

            # Draw clouds
        for cloud in clouds:
            pygame.draw.ellipse(screen, WHITE, cloud)

            # Draw player with walking animation
        draw_player(player.x, player.y, current_frame)

            # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, BLACK, obs)

            # Draw power-ups
        for powerup, powerup_type in powerups:
            color = {
                "shield": (0, 0, 255),
                "speed_boost": (255, 165, 0),
                "double_points": (0, 255, 0)
            }[powerup_type]
            pygame.draw.rect(screen, color, powerup)

            # Draw score and level
        draw_score_and_level()

            # Draw active power-ups
        draw_active_powerups()

            # Draw particles
        for particle in particles:
            pygame.draw.circle(screen, BLACK, (int(particle[0][0]), int(particle[0][1])), 3)

        pygame.display.update()

    cap.release()
    pygame.quit()

        # Start the game with the splash screen
splash_screen()
# Run the instruction screen first
instruction_screen()
