# импорт библиотек и файлов
from config import *
import pygame  
import math  
from map import collision_walls  

class Player:
    def __init__(self, sprites):
        self.x, self.y = player_pos  # Начальные координаты игрока
        self.sprites = sprites  # Список спрайтов
        self.angle = player_angle  # Угол направления взгляда игрока
        self.sensitivity = 0.004  # Чувствительность мыши
        self.side = 50  # Размер стороны прямоугольника коллизии
        self.rect = pygame.Rect(*player_pos, self.side, self.side)  # Прямоугольник коллизии
        self.shot = False  # Флаг выстрела

    @property
    def pos(self):
        return (self.x, self.y)  # Свойство, возвращающее текущие координаты игрока

    @property
    def collision_list(self):
        return collision_walls + [pygame.Rect(*obj.pos, obj.side, obj.side) for obj in self.sprites.list_of_objects if obj.blocked]  # Список объектов для проверки столкновения

    def detect_collision(self, dx, dy): 
        next_rect = self.rect.copy()
        next_rect.move_ip(dx, dy)
        hit_indexes = next_rect.collidelistall(self.collision_list)

        if hit_indexes:
            delta_x, delta_y = 0, 0
            for hit_index in hit_indexes:
                hit_rect = self.collision_list[hit_index]
                delta_x += (next_rect.right - hit_rect.left) if dx > 0 else (hit_rect.right - next_rect.left)
                delta_y += (next_rect.bottom - hit_rect.top) if dy > 0 else (hit_rect.bottom - next_rect.top)

            if abs(delta_x - delta_y) < 10:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            elif delta_y > delta_x:
                dx = 0
        self.x += dx
        self.y += dy

    def movement(self):
        # Обработка управления игроком
        self.keys_control()
        self.mouse_control()
        self.rect.center = (self.x, self.y)  # Обновление центра прямоугольника коллизии
        self.angle %= DOUBLE_PI

    def keys_control(self):
        # Обработка клавиш управления
        sin_a, cos_a = math.sin(self.angle), math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit()

        if keys[pygame.K_w]:
            dx, dy = player_speed * cos_a, player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_s]:
            dx, dy = -player_speed * cos_a, -player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_a]:
            dx, dy = player_speed * sin_a, -player_speed * cos_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_d]:
            dx, dy = -player_speed * sin_a, player_speed * cos_a
            self.detect_collision(dx, dy)

        if keys[pygame.K_LEFT]:
            self.angle -= 0.02
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.shot:
                    self.shot = True

    def mouse_control(self):
        # Обработка движения мыши
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - HALF_WIDTH
            pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))
            self.angle += difference * self.sensitivity