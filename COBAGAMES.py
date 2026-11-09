import pygame
import random

pygame.init()

# Dimensions of the screen
WIDTH, HEIGHT = 600, 500

# Palet Warna Cerah & Terang (Neon / Bright Theme)
BLACK = (15, 15, 25)          # Latar belakang gelap lembut agar warna terang kontras
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)
NEON_CYAN = (0, 255, 255)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 140, 0)
NEON_PURPLE = (186, 85, 211)
RED = (255, 69, 0)

font = pygame.font.Font(None, 25)
big_font = pygame.font.Font(None, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker - Versi Warna Terang")

clock = pygame.time.Clock()
FPS = 60


# Striker class
class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color

        self.strikerRect = pygame.Rect(
            posx, posy, width, height
        )

    def display(self):
        # Menggambar striker utama dan efek kilau atasnya
        pygame.draw.rect(screen, self.color, self.strikerRect, border_radius=5)
        highlight_rect = pygame.Rect(self.posx, self.posy, self.width, 4)
        pygame.draw.rect(screen, WHITE, highlight_rect, border_radius=2)

    def update(self, xFac):
        self.posx += self.speed * xFac

        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH - self.width

        self.strikerRect.topleft = (self.posx, self.posy)

    def getRect(self):
        return self.strikerRect


# Block Class
class Block:
    def __init__(self, posx, posy, width, height, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = color
        self.damage = 100

        if color == WHITE:
            self.health = 200
        else:
            self.health = 100

        self.blockRect = pygame.Rect(
            posx, posy, width, height
        )

    def display(self):
        if self.health > 0:
            # Menggambar blok berwarna terang dengan sudut melengkung dan border putih
            pygame.draw.rect(screen, self.color, self.blockRect, border_radius=4)
            pygame.draw.rect(screen, WHITE, self.blockRect, 1, border_radius=4)

    def hit(self):
        self.health -= self.damage

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health


# Ball Class
class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.startx = posx
        self.starty = posy
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color

        self.xFac = 1
        self.yFac = -1

        self.ballRect = pygame.Rect(
            posx - radius,
            posy - radius,
            radius * 2,
            radius * 2
        )

    def display(self):
        # Bola dengan efek bercahaya (lingkaran luar tipis + bola utama)
        pygame.draw.circle(
            screen,
            NEON_CYAN,
            (int(self.posx), int(self.posy)),
            self.radius + 3,
            1
        )
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.posx), int(self.posy)),
            self.radius
        )

    def update(self):
        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed

        # Left and right wall collision
        if self.posx - self.radius <= 0:
            self.posx = self.radius
            self.xFac *= -1

        elif self.posx + self.radius >= WIDTH:
            self.posx = WIDTH - self.radius
            self.xFac *= -1

        # Top wall collision
        if self.posy - self.radius <= 0:
            self.posy = self.radius
            self.yFac *= -1

        # Update ball rectangle
        self.ballRect.center = (
            int(self.posx), int(self.posy)
        )

        # Ball falls below screen
        if self.posy - self.radius >= HEIGHT:
            return True

        return False

    def reset(self):
        self.posx = self.startx
        self.posy = self.starty
        self.xFac = 1
        self.yFac = -1

        self.ballRect.center = (
            int(self.posx), int(self.posy)
        )

    def hit(self):
        self.yFac *= -1

    def getRect(self):
        return self.ballRect


# Helper Functions
def collisionChecker(rect, ball):
    return rect.colliderect(ball)


# Populate blocks dengan variasi warna cerah
def populateBlocks(blockWidth, blockHeight,
                   horizontalGap, verticalGap):

    listOfBlocks = []
    # Daftar pilihan warna neon yang cerah
    color_choices = [NEON_GREEN, NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_ORANGE, NEON_PURPLE, WHITE]

    for i in range(10, WIDTH - blockWidth, blockWidth + horizontalGap):
        for j in range(30, HEIGHT // 2, blockHeight + verticalGap):

            color = random.choice(color_choices)

            listOfBlocks.append(
                Block(
                    i, j,
                    blockWidth,
                    blockHeight,
                    color
                )
            )

    return listOfBlocks


# Game Over
def gameOver():
    while True:
        screen.fill(BLACK)

        text = big_font.render("GAME OVER", True, RED)
        restart = font.render(
            "Press SPACE to Restart or ESC to Exit",
            True,
            NEON_YELLOW
        )

        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        )

        screen.blit(
            restart,
            restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True

                if event.key == pygame.K_ESCAPE:
                    return False

        clock.tick(FPS)


# Main Game
def main():
    running = True

    lives = 3
    score = 0

    striker = Striker(
        250, HEIGHT - 50,
        100, 15, 8, NEON_GREEN
    )

    strikerXFac = 0

    ball = Ball(
        300, HEIGHT - 100,
        7, 5, NEON_YELLOW
    )

    blockWidth = 40
    blockHeight = 15

    horizontalGap = 15
    verticalGap = 15

    listOfBlocks = populateBlocks(
        blockWidth,
        blockHeight,
        horizontalGap,
        verticalGap
    )

    while running:

        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    this_fac = -1
                    strikerXFac = -1

                elif event.key == pygame.K_RIGHT:
                    strikerXFac = 1

            if event.type == pygame.KEYUP:

                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    strikerXFac = 0

        # Update striker
        striker.update(strikerXFac)

        # Update ball
        lifeLost = ball.update()

        # Striker collision
        if collisionChecker(
            striker.getRect(),
            ball.getRect()
        ):
            if ball.yFac > 0:
                ball.hit()

        # Block collision
        for block in listOfBlocks[:]:

            if collisionChecker(
                block.getRect(),
                ball.getRect()
            ):

                ball.hit()
                block.hit()

                if block.getHealth() <= 0:
                    listOfBlocks.remove(block)
                    score += 5

                break

        # Life lost
        if lifeLost:
            lives -= 1
            ball.reset()

            if lives <= 0:
                running = gameOver()

                if running:
                    lives = 3
                    score = 0

                    listOfBlocks = populateBlocks(
                        blockWidth,
                        blockHeight,
                        horizontalGap,
                        verticalGap
                    )

                    striker.posx = 250
                    striker.strikerRect.x = 250
                    ball.reset()

        # Refill blocks
        if not listOfBlocks:
            listOfBlocks = populateBlocks(
                blockWidth,
                blockHeight,
                horizontalGap,
                verticalGap
            )

        # Display score and lives with bright colors
        scoreText = font.render(
            "Score: " + str(score),
            True,
            NEON_CYAN
        )

        livesText = font.render(
            "Lives: " + str(lives),
            True,
            NEON_PINK
        )

        screen.blit(scoreText, (10, HEIGHT - 25))
        screen.blit(livesText, (120, HEIGHT - 25))

        # Display objects
        striker.display()
        ball.display()

        for block in listOfBlocks:
            block.display()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()