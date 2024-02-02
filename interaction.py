# Импорт необходимых модулей
from config import *
from map import world_map
from ray_casting import mapping
import math
import pygame

# Функция для лучевого трассирования между NPC и игроком
def ray_casting_npc_player(npc_x, npc_y, blocked_doors, world_map, player_pos):
    # Получение координат игрока
    ox, oy = player_pos

    # Преобразование координат игрока в координаты карты
    xm, ym = mapping(ox, oy)

    # Вычисление угла между NPC и игроком
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = math.atan2(delta_y, delta_x)
    cur_angle += math.pi

    # Вычисление синуса и косинуса угла
    sin_a = math.sin(cur_angle)
    sin_a = sin_a if sin_a else 0.000001
    cos_a = math.cos(cur_angle)
    cos_a = cos_a if cos_a else 0.000001

    # Лучи для вертикальных столбцов
    x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
    for _ in range(0, int(abs(delta_x)) // TILE):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map or tile_v in blocked_doors:
            return False
        x += dx * TILE

    # Лучи для горизонтальных строк
    y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
    for _ in range(0, int(abs(delta_y)) // TILE):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map or tile_h in blocked_doors:
            return False
        y += dy * TILE
    return True


# Класс для обработки взаимодействий в игре
class Interaction:
    def __init__(self, player, sprites, drawing):
        # Инициализация объектов игрока, спрайтов и отрисовки
        self.player = player
        self.sprites = sprites
        self.drawing = drawing
        self.pain_sound = pygame.mixer.Sound('sound/pain.wav')

    # Метод обработки взаимодействия объектов
    def interaction_objects(self):
        # Проверка наличия выстрела игрока и активации анимации выстрела
        if self.player.shot and self.drawing.shot_animation_trigger:
            # Перебор объектов в порядке удаления по расстоянию
            for obj in sorted(self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite):
                # Обработка выстрела по NPC
                if obj.is_on_fire[1]:
                    if obj.is_dead != 'immortal' and not obj.is_dead:
                        if ray_casting_npc_player(obj.x, obj.y,
                                                  self.sprites.blocked_doors,
                                                  world_map, self.player.pos):
                            if obj.flag == 'npc':
                                self.pain_sound.play()
                            obj.is_dead = True
                            obj.blocked = None
                            self.drawing.shot_animation_trigger = False
                    # Обработка выстрела по дверям
                    if obj.flag in {'door_h', 'door_v'} and obj.distance_to_sprite < TILE:
                        obj.door_open_trigger = True
                        obj.blocked = None
                    break

    # Метод определения действий NPC
    def npc_action(self):
        for obj in self.sprites.list_of_objects:
            if obj.flag == 'npc' and not obj.is_dead:
                if ray_casting_npc_player(obj.x, obj.y,
                                          self.sprites.blocked_doors,
                                          world_map, self.player.pos):
                    obj.npc_action_trigger = True
                    self.npc_move(obj)
                else:
                    obj.npc_action_trigger = False

    # Метод перемещения NPC в сторону игрока
    def npc_move(self, obj):
        if abs(obj.distance_to_sprite) > TILE:
            dx = obj.x - self.player.pos[0]
            dy = obj.y - self.player.pos[1]
            obj.x = obj.x + 1 if dx < 0 else obj.x - 1
            obj.y = obj.y + 1 if dy < 0 else obj.y - 1

    # Метод удаления объектов, помеченных для удаления
    def clear_world(self):
        deleted_objects = self.sprites.list_of_objects[:]
        [self.sprites.list_of_objects.remove(obj) for obj in deleted_objects if obj.delete]

    # Метод проигрывания фоновой музыки
    def play_music(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.mixer.music.load('sound/theme.mp3')
        pygame.mixer.music.play(10)

    # Метод проверки условия победы
    def check_win(self):
        if not len([obj for obj in self.sprites.list_of_objects if obj.flag == 'npc' and not obj.is_dead]):
            pygame.mixer.music.stop()
            pygame.mixer.music.load('sound/win.mp3')
            pygame.mixer.music.play()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                self.drawing.win()