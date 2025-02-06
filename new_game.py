import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_HEIGHT = HEIGHT - 50
PARTICLE_LIFETIME = 10

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scroller Game")

# Player properties
player = pygame.Rect(100, GROUND_HEIGHT - 40, 40, 40)
player_speed = 5
jump_power = -12
gravity = 0.5
velocity_y = 0
is_jumping = False
animation_index = 0

# Obstacle properties
obstacle = pygame.Rect(random.randint(500, 700), GROUND_HEIGHT - 30, 30, 30)
obstacle_speed = 4

# Particle effects
particles = []
def add_particles():
    for _ in range(5):
        particles.append([[player.x + 20, player.y + 40], [random.randint(-2, 2), random.randint(-2, 0)], PARTICLE_LIFETIME])

def update_particles():
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 1
        if particle[2] <= 0:
            particles.remove(particle)

# Score
score = 0
font = pygame.font.SysFont(None, 36)

def draw_score():
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

# Game loop
running = True
while running:
    pygame.time.delay(30)  # Control game speed
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Key events
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_SPACE] and not is_jumping:
        velocity_y = jump_power
        is_jumping = True
        add_particles()
    
    # Apply gravity
    velocity_y += gravity
    player.y += velocity_y
    
    # Collision with ground
    if player.y >= GROUND_HEIGHT - player.height:
        player.y = GROUND_HEIGHT - player.height
        is_jumping = False
    
    # Move obstacle
    obstacle.x -= obstacle_speed
    if obstacle.x < -30:
        obstacle.x = random.randint(500, 700)
        score += 1  # Increase score when obstacle resets
    
    # Check collision with obstacle
    if player.colliderect(obstacle):
        print("Game Over! Final Score:", score)
        pygame.time.delay(2000)
        running = False
    
    # Update player animation
    animation_index = (animation_index + 1) % 4
    
    # Update particles
    update_particles()
    
    # Drawing
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, player)
    pygame.draw.rect(screen, BLACK, obstacle)
    pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (WIDTH, GROUND_HEIGHT), 2)
    draw_score()
    
    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, BLACK, (int(particle[0][0]), int(particle[0][1])), 3)
    
    pygame.display.update()

pygame.quit()
