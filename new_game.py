import pygame
import random
import cv2
import mediapipe as mp

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

# Cloud properties
CLOUD_WIDTH, CLOUD_HEIGHT = 100, 50
clouds = []
for _ in range(3):  # Create 3 clouds
    clouds.append(pygame.Rect(random.randint(WIDTH, WIDTH + 200), random.randint(50, 150), CLOUD_WIDTH, CLOUD_HEIGHT))

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Runner")

# Player properties
player = pygame.Rect(100, GROUND_HEIGHT - 50, 40, 50)  # Adjusted height and position
player_speed = 5
jump_power = -12
gravity = 0.5
velocity_y = 0
is_jumping = False

# Animation properties
animation_frames = 2  # Number of frames for the animation
current_frame = 0
frame_counter = 0
frame_delay = 10  # Delay between frame updates

# Obstacle properties
obstacles = [pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30)]
obstacle_speed = 5  # Increased obstacle speed

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

# Score and Level
score = 0
level = 1
font = pygame.font.SysFont(None, 36)

def draw_score_and_level():
    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 150, 10))

# Function to increase the level
def increase_level():
    global level, obstacle_speed, obstacles
    if score % 10 == 0 and level < score // 10 + 1:  # Level up every 10 points
        level += 1
        obstacle_speed += 1  # Increase obstacle speed
        # Add a new obstacle every 10 points scored
        obstacles.append(pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30))

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# OpenCV camera setup
cap = cv2.VideoCapture(0)

# Function for the splash screen with fade-in animation
def splash_screen():
    screen.fill(SKY_BLUE)
    font_large = pygame.font.SysFont(None, 100)  # Increased text size
    title_text = font_large.render("Sky Runner", True, WHITE)

    # Create a surface for the text with per-pixel alpha
    text_surface = pygame.Surface((title_text.get_width(), title_text.get_height()), pygame.SRCALPHA)
    text_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    # Fade-in animation
    for alpha in range(0, 256, 5):  # Gradually increase alpha from 0 to 255
        text_surface.fill((255, 255, 255, 0))  # Clear the surface
        text_surface.blit(title_text, (0, 0))  # Draw the text
        text_surface.set_alpha(alpha)  # Set the alpha value

        screen.fill(SKY_BLUE)  # Clear the screen
        screen.blit(text_surface, text_rect)  # Draw the text surface
        pygame.display.update()
        pygame.time.delay(30)  # Control the speed of the fade-in

    pygame.time.delay(1000)  # Keep the text visible for 1 second after fade-in

# Function to draw the start game button
def draw_start_button():
    screen.fill(SKY_BLUE)  # Clear the screen
    button_width, button_height = 200, 80
    button_x, button_y = (WIDTH // 2) - (button_width // 2), (HEIGHT // 2) - (button_height // 2)
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Draw button (card-like appearance)
    pygame.draw.rect(screen, WHITE, button_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, button_rect, 2, border_radius=10)

    # Draw button text
    font_button = pygame.font.SysFont(None, 36)
    button_text = font_button.render("Start Game", True, BLACK)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    pygame.display.update()
    return button_rect

# Function for the Game Over screen
def game_over_screen():
    screen.fill(SKY_BLUE)
    font_large = pygame.font.SysFont(None, 72)
    game_over_text = font_large.render("Game Over", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)

    final_score_text = font.render(f"Final Score: {score}", True, BLACK)
    final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(final_score_text, final_score_rect)

    restart_text = font.render("Press 'R' to Restart or 'Q' to Quit", True, BLACK)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(restart_text, restart_rect)

    pygame.display.update()

    # Wait for restart or quit input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False  # Restart the game
                    game_loop()  # Start the game again
                elif event.key == pygame.K_q:
                    pygame.quit()  # Quit the game
                    quit()

# Function to draw the player character with walking animation
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

# Game loop
def game_loop():
    global score, level, obstacles, is_jumping, velocity_y, particles, clouds, current_frame, frame_counter
    score = 0  # Reset score
    level = 1  # Reset level
    obstacles = [pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30)]  # Reset obstacles
    player.x = 100  # Reset player position
    player.y = GROUND_HEIGHT - 50  # Reset player position
    velocity_y = 0  # Reset player velocity
    is_jumping = False  # Reset jump state
    particles = []  # Clear particles
    clouds = []  # Reset clouds
    for _ in range(3):  # Create 3 new clouds
        clouds.append(pygame.Rect(random.randint(WIDTH, WIDTH + 200), random.randint(50, 150), CLOUD_WIDTH, CLOUD_HEIGHT))

    running = True
    paused = False  # Pause state
    while running:
        pygame.time.delay(30)  # Control game speed

        # Get webcam frame
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame for faster processing
        frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Hand gesture detection
        if results.multi_hand_landmarks:
            num_hands = len(results.multi_hand_landmarks)  # Number of hands detected

            # Pause if two hands are shown
            if num_hands == 2:
                paused = True
            # Resume if one hand is shown
            elif num_hands == 1:
                if paused:
                    paused = False

                # Jump if the hand is open (thumb and pinky far apart)
                for landmarks in results.multi_hand_landmarks:
                    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                    # Calculate distance between thumb and pinky
                    distance = ((thumb_tip.x - pinky_tip.x) ** 2 + (thumb_tip.y - pinky_tip.y) ** 2) ** 0.5

                    # Trigger jump if hand is open
                    if distance > 0.15:
                        if not is_jumping:
                            velocity_y = jump_power
                            is_jumping = True
                            add_particles()

        # If paused, skip game logic
        if paused:
            # Display "Paused" text
            font_large = pygame.font.SysFont(None, 72)
            paused_text = font_large.render("Paused", True, BLACK)
            paused_rect = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(paused_text, paused_rect)
            pygame.display.update()
            continue

        # Process game logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
            frame_counter += 1  # Update frame counter for animation
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
            frame_counter += 1  # Update frame counter for animation

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

        # Check collision with obstacles
        for obs in obstacles:
            if player.colliderect(obs):
                game_over_screen()  # Trigger the game over screen
                return  # End the game loop

        # Update particles
        update_particles()

        # Increase level and difficulty
        increase_level()

        # Move clouds (slightly faster)
        for cloud in clouds:
            cloud.x -= 2  # Increased cloud movement speed
            if cloud.x < -CLOUD_WIDTH:  # Reset cloud position to right side
                cloud.x = random.randint(WIDTH, WIDTH + 200)
                cloud.y = random.randint(50, 150)

        # Update animation frame (only when moving)
        if frame_counter >= frame_delay:
            frame_counter = 0
            current_frame = (current_frame + 1) % animation_frames

        # Drawing
        screen.fill(SKY_BLUE)  # Draw sky background
        pygame.draw.rect(screen, GROUND_GREEN, (0, GROUND_HEIGHT, WIDTH, HEIGHT - GROUND_HEIGHT))  # Draw ground

        # Draw clouds
        for cloud in clouds:
            pygame.draw.ellipse(screen, WHITE, cloud)  # Draw each cloud

        # Draw player with walking animation
        draw_player(player.x, player.y, current_frame)

        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, BLACK, obs)

        pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (WIDTH, GROUND_HEIGHT), 2)
        draw_score_and_level()  # Draw score and level

        # Draw particles
        for particle in particles:
            pygame.draw.circle(screen, BLACK, (int(particle[0][0]), int(particle[0][1])), 3)

        pygame.display.update()

# Show splash screen before starting the game
splash_screen()

# Transition to the start game button screen
button_rect = draw_start_button()

# Wait for the button to be clicked
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                waiting = False  # Start the game

# Start the game loop
game_loop()

cap.release()
pygame.quit()
