# импорт библиотек и файлов
from player import Player
from sprite_objects import * 
from ray_casting import ray_casting_walls  
from drawing import Drawing  
from interaction import Interaction  

def main():
    # Инициализация Pygame
    pygame.init()  
    # Создание окна с размерами WIDTH и HEIGHT
    sc = pygame.display.set_mode((WIDTH, HEIGHT))  
    # Создание поверхности для миникарты
    sc_map = pygame.Surface(MINIMAP_RES)  

    # название игры
    pygame.display.set_caption('DOOM')

    pygame.display.set_icon(pygame.image.load('img/logo.jpg'))
    # Создание объекта Sprites для управления спрайтами 
    sprites = Sprites()  
    # Создание объекта Clock для управления временем
    clock = pygame.time.Clock()  
    # Создание объекта Player с использованием объекта Sprites
    player = Player(sprites)  
    # Создание объекта Drawing для отрисовки игровых элементов
    drawing = Drawing(sc, sc_map, player, clock)  
    # Создание объекта Interaction для обработки взаимодействий
    interaction = Interaction(player, sprites, drawing)  

    # Отображение начального меню
    drawing.menu()  
    # Скрытие курсора мыши
    pygame.mouse.set_visible(False)  
    # Воспроизведение музыки в игре
    interaction.play_music()  

    while True:
        # Обработка движения игрока
        player.movement()  
        # Отображение фона с учетом угла обзора игрока
        drawing.background(player.angle)  
        # Применение алгоритма бросания лучей
        walls, wall_shot = ray_casting_walls(player, drawing.textures)  
        # Отрисовка мира
        drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])  
        # Отображение FPS
        drawing.fps(clock)  
        # Отображение миникарты
        drawing.mini_map(player)  
        # Отображение оружия игрока
        drawing.player_weapon([wall_shot, sprites.sprite_shot])  

        # Обработка взаимодействия с объектами
        interaction.interaction_objects()  
         # Обработка действий NPC
        interaction.npc_action() 
        # Очистка мира от спрайтов, помеченных для удаления
        interaction.clear_world()  
        interaction.check_win()  
        # Обновление экрана
        pygame.display.flip()  
        # Ограничение FPS
        clock.tick(FPS)  

# запуск кода
if __name__ == '__main__':
    main()  