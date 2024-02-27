from typing import Any
import pygame
import time
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Gravity = pygame.Vector2(0, 9.81)



class Wall(pygame.sprite.Sprite):
    def __init__(self, size, **kwargs) -> None:
        super().__init__()
        self.image = pygame.Surface(size).convert_alpha()
        self.image.fill("black")
        self.rect = self.image.get_rect(**kwargs)

class Toast(pygame.sprite.Sprite):
    v = 6
    m = 1
    def __init__(self, pos) -> None:
        super().__init__()
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()

        self.image = pygame.Surface((100, 100))
        
        self.rect = self.image.get_rect(center=self.position.xy)

        self.can_jump = True
        self.carrier = None
        self.other_toast: Toast = None

    def wall_below_me(self) -> Wall | Any:
        possible_walls = filter(lambda wall: wall.rect.top >= self.rect.bottom and any((
            wall.rect.left >= self.rect.left and wall.rect.right <= self.rect.right, 
            wall.rect.left <= self.rect.left and wall.rect.right >= self.rect.right,
            wall.rect.left >= self.rect.left and wall.rect.left <= self.rect.right,
            wall.rect.right >= self.rect.left and wall.rect.right <= self.rect.right,
        )), [*wall_group.sprites(), self.other_toast])

        try:
            return sorted(possible_walls, key=lambda wall: wall.rect.top - self.rect.bottom)[0]
        except IndexError:
            raise Exception("There should always be a wall below me, but there isn't")

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.position.y += self.velocity.y
        if self.other_toast.carrier is self:
            self.other_toast.position.y += self.velocity.y

        below_me = self.wall_below_me()
        if self.carrier is not None and below_me != self.carrier:
            self.carrier = None
        distance_to_ground = abs(self.rect.bottom - below_me.rect.top)

        if distance_to_ground <= (Gravity.y + self.velocity.y):
            self.position.y += distance_to_ground
            self.velocity.y = 0
            if isinstance(below_me, Toast):
                self.carrier = below_me
            self.can_jump = True
        else:
            self.position.y += Gravity.y
        self.rect.center = self.position.xy

        self.velocity.y *= 0.967
        if self.velocity.y > -3:
            self.velocity.y = 0

    def jump(self): 
            self.velocity.y += -30
            self.can_jump = False
            self.carrier = None

    def move(self, direction):
        self.position.x -= 300 * dt * direction




toastA = Toast((500, 500))
toastB = Toast((500, 500))
toastA.other_toast, toastB.other_toast = toastB, toastA
toastA.image.fill("red")
toastB.image.fill("green")
toasts = pygame.sprite.Group(toastA, toastB)

wall_group = pygame.sprite.Group()
wall_group.add(Wall((screen.get_width(), 10), topleft=(0, screen.get_height() - 10)))

for _ in range(10):
    width = random.randint(20, 200)
    wall_group.add(Wall((width, 40), bottomleft=(random.randint(10, screen.get_width()-10-width), random.randint(0, 600))))


font = pygame.font.SysFont("arial", 18)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_SPACE | pygame.K_w:
                   if toastA.can_jump:
                    toastA.jump()
                case pygame.K_UP:
                    if toastB.can_jump:
                        toastB.jump()
            

    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        toastA.move(1)
    if keys[pygame.K_d]:
        toastA.move(-1)
    if keys[pygame.K_RIGHT]:
        toastB.move(-1)
    if keys[pygame.K_LEFT]:
        toastB.move(1)
    toasts.update()
    wall_group.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("blue")
    wall_group.draw(screen)
    toasts.draw(screen)
    # text = font.render(f"{toast.velocity.y} {toast.rect.bottom} {screen.get_height()} {toast.position.distance_to(pygame.Vector2(pygame.mouse.get_pos()))}", False, "black")
    # screen.blit(text, (100, 100))
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()