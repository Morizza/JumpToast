from typing import Any
import pygame
import time
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
dt = 0
Gravity = pygame.Vector2(0, 9.81)

class Toaster(pygame.sprite.Sprite):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.image = pygame.transform.scale2x(pygame.image.load("assets/toaster.png").convert_alpha())
        self.rect = self.image.get_rect(**kwargs)
        self.boden = Wall((50, 10), midbottom=(pygame.Vector2(self.rect.midbottom) + pygame.Vector2(0, -50)).xy)
        # self.boden.image.set_alpha()
        wall_group.add(self.boden)

    def kill(self) -> None:
        self.boden.kill()
        return super().kill()

class Wall(pygame.sprite.Sprite):
    def __init__(self, size, **kwargs) -> None:
        super().__init__()
        self.image = pygame.Surface(size).convert_alpha()
        self.image.fill("black")
        self.rect = self.image.get_rect(**kwargs)

class Plate(pygame.sprite.Sprite):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.image = pygame.transform.scale2x(pygame.image.load("assets/plate.png").convert_alpha())
        self.rect = self.image.get_rect(**kwargs)



class Toast(pygame.sprite.Sprite):
    v = 6
    m = 1
    def __init__(self, pos, jam_or_peanut) -> None:
        super().__init__()
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()

        self.image = pygame.transform.scale_by(pygame.image.load("assets/jamToast.png" if jam_or_peanut else "assets/peanutToast.png").convert_alpha(), 2.5)
        self.rect = self.image.get_rect(center=self.position.xy)

        self.can_jump = True
        self.carrier = None
        self.other_toast: Toast = None
        self.in_toaster = False

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
            raise Exception(f"{main_boden} There should always be a wall below me, but there isn't")

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

        if pygame.sprite.spritecollide(self, toaster_group, dokill=False):
            self.in_toaster = True
        else:
            self.in_toaster = False

    def jump(self): 
            jumpforce = -30
            if self.in_toaster:
                jumpforce -=30
            self.velocity.y += jumpforce
            self.can_jump = False
            self.carrier = None

    def move(self, direction):
        self.position.x -= 300 * dt * direction

class Camera:
    def __init__(self, surface: pygame.Surface) -> None:
        self.offset = pygame.Vector2()
        self.surface = surface

    def draw(self, group: pygame.sprite.Group):
        for sprite in group.sprites():
            pos = (pygame.Vector2(sprite.rect.topleft) + self.offset).xy
            if isinstance(sprite, Plate) and pos.y - 250 > screen.get_height():
                sprite.kill()
                continue
            self.surface.blit(sprite.image, pos)




toastA = Toast((500, 500), True)
toastB = Toast((500, 500), False)
toastA.other_toast, toastB.other_toast = toastB, toastA

toasts = pygame.sprite.Group(toastA, toastB)

toaster_group = pygame.sprite.Group()

wall_group = pygame.sprite.Group()
main_boden = Wall((screen.get_width(), 10), topleft=(0, screen.get_height() - 10))
wall_group.add(main_boden)

font = pygame.font.SysFont("arial", 18)
cam = Camera(screen)

for _ in range(10):
    wall_group.add(Plate(bottomleft=(random.randint(10, screen.get_width()-10-64), random.randint(0, 600) - cam.offset.y)))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_SPACE | pygame.K_w:
                   if toastA.can_jump:
                    toastA.jump()
                case pygame.K_q:
                    toastA.position = toastB.position.xy + pygame.Vector2(0, -10)
                case pygame.K_RETURN:
                    toastB.position = toastA.position.xy + pygame.Vector2(0, -10)
                case pygame.K_UP:
                    if toastB.can_jump:
                        toastB.jump()
            

    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        if toastA.rect.left >= 0:
            toastA.move(1)
    if keys[pygame.K_d]:
        if toastA.rect.right <= screen.get_width():
            toastA.move(-1)
    if keys[pygame.K_RIGHT]:
        if toastB.rect.right <= screen.get_width(): 
            toastB.move(-1)
    if keys[pygame.K_LEFT]:
        if toastB.rect.left >= 0:
            toastB.move(1)
    toasts.update()
    wall_group.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("blue")
    cam.draw(wall_group)
    cam.draw(toasts)
    cam.draw(toaster_group)

    
    text = font.render(f"{cam.offset.y}", False, "black")
    screen.blit(text, (100, 100))


    while len(wall_group) <= 10:
        highest: Plate | Wall = list(sorted(wall_group.sprites(), key=lambda wall: wall.rect.top, reverse=False))[0]
        new_pos = pygame.Vector2(highest.rect.midtop) + pygame.Vector2(random.randint(-600, 600), random.randint(-320, -50))
        if 0 < new_pos.x < screen.get_width():
            if random.randint(0, 9) == 0:
                toaster_group.add(Toaster(midbottom=new_pos.xy))
            else:
                wall_group.add(Plate(midbottom=new_pos.xy))


            

    if len(toaster_group) == 0:
        toaster_group.add(Toaster(bottomleft=(random.randint(80, screen.get_width()-80), screen.get_height() - cam.offset.y)))



    # flip() the display to put your work on screen
    pygame.display.flip()

    cam.offset.y = screen.get_height() -max(toastA.rect.bottom, toastB.rect.bottom) - 100

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()