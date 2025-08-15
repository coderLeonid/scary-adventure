import random  # Импортируем библиотеки рандом для генерации случайных чисел
import pygame as pg  # Импортируем библиотеки, которая будет отрисовывать все объекты для пользователя и проигрывать для него звуковые эффекты
import time  # Импортируем время для того, чтобы отсчитывать частоту выстрелов, время суток и многое другое
from math import ceil

# Ициализация модуля (библиотеки) pygame
pg.mixer.pre_init()
pg.init()

# Эта строчка кода для оптимизации кода, чтобы не приходилось сверять все клавиши, а лишь некоторые из тех, что мы разрешили
pg.event.set_allowed((pg.QUIT, pg.KEYDOWN, pg.K_ESCAPE, pg.MOUSEBUTTONDOWN, pg.K_SPACE, pg.K_RETURN))

# Сохраняем цвета с определённым RGB-кодом (кодом яркости красного, синего и зелёного) в переменные, так как буду использовать их часто в коде
DARK_GRAY, LIGHT_GRAY = (63, 63, 63), (191, 191, 191)
BLOODY_RED = (191, 47, 11)
DARK_GREEN = (0, 127, 0)

# Папка, в которой хранится всё что необходимо для игры: изображения, звуковые эффекты, сам код (nightmare.py) и исполняемый файл,
# который можно запустить даже если питона нет на компьютере (nightmare.exe)
MAIN_FOLDER_PATH = 'parts_of_shooter_game/Game'

# Изображение на заднем фоне (обои игры)
HORROR_GHOST_ICON = pg.image.load(f'{MAIN_FOLDER_PATH}/ghost_icon.ico')

# Размеры объектов на поле, самого поля и экрана (в пикселях, либо в рядах и колоннах)
ROWS, COLUMNS = 15, 23
FIELD_WIDTH, FIELD_HEIGHT = 50 * COLUMNS, 50 * ROWS
WIDTH, HEIGHT = FIELD_WIDTH + 100, FIELD_HEIGHT + 100

# Настройка частоты кадров в секунду (FPS) и создание часов для них
FPS = 100
CYCLES_PER_SECOND = pg.time.Clock()

# Настройка человеческого урона и перечисление всех уровней игры
HUMAN_SHOT_DAMAGE = 5
LEVELS = ('тренировочный', 'лёгкий', 'средний', 'сложный', 'безумный', 'невозможный', 'обучающий')

# Создаём параметры окна для игры: само окно, её заголовок и иконку
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))  # создание окна определённого разрешения (WIDTHxHEIGHT пикселей)
pg.display.set_caption('Страшное приключение.')
pg.display.set_icon(HORROR_GHOST_ICON)


class KeyBoardImage:  # Класс который хранит изображения необходимых клавиш
    __folder_path = 'parts_of_shooter_game/Keyboard'  # Папка, где хранятся изображения клавиш

    @classmethod
    def set_class_attributes(cls):  # Функция, которая присваевает переменным (атрибутам) этого класса изображения клавиш
        for attribute in ('wasd', 'arrows', 'enter', 'space'):
            setattr(cls, attribute, pg.image.load(f'{cls.__folder_path}/{attribute}.png').convert())
            getattr(cls, attribute).set_colorkey('yellow')


KeyBoardImage.set_class_attributes()  # Вызов функции, которая присвоет переменным изображения клавиш


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Все объекты игры, которые движутся и не движутся
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Obj:  # Класс, который работает с координатами каждого объекта в этой игре
    __slots__ = ('x', 'y')  # Допускаем только координаты x и y

    def __init__(self, coords):  # Функция, создающая объект в определённых координатах
        self.x, self.y = coords

    @property
    def coords(self):  # Функция для получения координат объекта
        return self.x, self.y


    @property
    def center(self): # Функция, которая получит координаты центра любого объекта
        x, y, width, height = self.image_rect
        return x + width / 2, y + height / 2

    def __eq__(self, other):  # Функция, которая заставит сравнивать недвигающиеся объекты не полностью, а лишь по их координатам
        type_tuple = (Creature, Shot, Field)
        if (isinstance(self, type_tuple) and isinstance(other, type_tuple)) or other is None:
            return super().__eq__(other)
        return self.coords == other.coords

    @property
    def image_rect(self) -> pg.Rect:  # Фукнция, которая получит координатный прямоугольник объекта
        return self.image.get_rect(topleft=self.coords)

    @staticmethod
    def generate_random_coords():  # Функия, которая сгенерирует случайные координаты появления объекта
        return (random.randrange(COLUMNS) + 1) * 50, (random.randrange(ROWS) + 1) * 50


#  --------------------------------------------------------------------------------------------
#  магия и выстрелы
#  --------------------------------------------------------------------------------------------


class MagicHelp(Obj):  # Класс, с помощью которого создаётся магическая помощь, которая поможет пройти игру
    __slots__ = ('time',)
    time_lying_on_the_field = 14  # Если не успеешь собрать магическую помощь в течение этого времени, она исчезнет
    __folder_path = 'parts_of_shooter_game/MagicHelp'  # Папка, в которой хранится все изображения магических помощей

    def __init__(self, coords):  # Создание магической помощи и получение его времени появления
        super().__init__(coords)
        self.time = time.time()

    @classmethod  # Минимальное и максимальное значения, которое может быть между появлениями магических помощей на игровом поле
    def set_time_range_between_appearances(cls, min_time_in_deciseconds: int):
        cls.time_range_between_appearances = (min_time_in_deciseconds, min_time_in_deciseconds + 60)

    @classmethod
    def set_class_attributes(cls):
        # Получения изображений и звуковых эффектов магической помощи из папки
        cls.image = pg.image.load(f'{cls.__folder_path}/image/{cls.__name__}.png').convert()
        cls.sound_when_collected = pg.mixer.Sound(f'{cls.__folder_path}/sound_when_collected/{cls.__name__}.mp3')

        # Список диапазонов цифр, которые должны быть сгенерированы для появления магической помощи каждого типа (ускорителя, целителя, боеприпасника)
        spawn_numbers = cls._spawn_numbers_on_level[Level.chosen] 
        if spawn_numbers != 'None':
            split_spawn_numbers = spawn_numbers.split('-')
            cls.spawn_numbers = range(int(split_spawn_numbers[0]), int(split_spawn_numbers[1]) + 1)
        else:
            cls.spawn_numbers = None,

    # получение время между спавнами, если измерять в секундах
    @classmethod
    def get_time_between_appearances(cls):
        return random.randrange(*cls.time_range_between_appearances) / 10


# Виды магической помощи
class Healer(MagicHelp):  # целитель здоровья
    __slots__ = ()
    _spawn_numbers_on_level = dict(zip(LEVELS, ('66-99', '80-99', '80-99', '80-99', '86-99', 'None', 'None')))
    health = 50  # Насколько увеличивается здоровье при сборе


class ShotsRestorer(MagicHelp):  # Боеприпасника
    __slots__ = ()
    _spawn_numbers_on_level = dict(zip(LEVELS, ('0-55', '0-69', '0-69', '0-69', '0-71', '0-99', 'None')))
    amount_of_shots = 20  # Насколько больше становится патронов при сборе


class SpeedIncreaser(MagicHelp):  # Временный ускоритель
    __slots__ = ()
    _spawn_numbers_on_level = dict(zip(LEVELS, ('56-65', '70-79', '70-79', '70-79', '72-85', 'None', 'None')))
    time_that_speed_stays_increased = 15  # В течени какого времени действует эффект ускоренного движения
    multiplier = 2  # Во сколько раз возрастает скорость


class Shot(Obj):  # Класс пуля (патрон, выстрел)
    __slots__ = ('x_shift_per_frame', 'y_shift_per_frame', 'axial_speed', 'radius')
    __folder_path = 'parts_of_shooter_game/Shot'

    def __init__(self, coords, coords_shift):  # Создание пули
        super().__init__(coords)
        
        # Установка смещения выстрелов по оси x и y и потом вычисляние скоростей в осях x и y используя следствие Теоремы Пифагора
        x_shift, y_shift = coords_shift
        self.axial_speed = (self.speed / FPS, self.speed / FPS * 0.5 ** 0.5)[x_shift != 0 and y_shift != 0]
        self.x_shift_per_frame, self.y_shift_per_frame = x_shift * self.axial_speed, y_shift * self.axial_speed

    def move(self) -> None:  # Перемещение пули по оси x и y
        self.x += self.x_shift_per_frame
        self.y += self.y_shift_per_frame

    def block_type_object_touches_shot_type_object(self, block_center):  # Проверка выстрела и блока на столковение, сделано с целью оптимизации
        x, y = block_center
        center_x, center_y = self.center
        return abs(center_x - x) < 50 // 2 + self.radius and abs(center_y - y) < 50 // 2 + self.radius

    @property
    def no_smash_in_field_and_its_objects(self):  # Проверка касания пули игрового поля, но при этом неприкосновения пулей любого неживого объекта игрового поля (блока)
        min_coord = 50 - 2 * self.radius

        shot_touches_field = min_coord < self.x < 50 + FIELD_WIDTH and min_coord < self.y < 50 + FIELD_HEIGHT
        shot_touches_bricks = [None for center in Field.bricks_centers
                               if self.block_type_object_touches_shot_type_object(block_center=center)]

        return shot_touches_field and not shot_touches_bricks

    @classmethod
    def destroy_monsters_in_touch(cls, shots, monsters):  # Нанести урон монстрам, коснувшимся пули и убить их если их здоровья не хватает на урон
        # Если нету пуль на поле, то смысл запускать алгоритм, обрабатывающий столкновения пуль
        if not (monsters and shots):
            return shots, monsters

        # Проверка каждой пули на столкновение с каждым монстром
        for index, shot in enumerate(shots):
            for monster in monsters:
                if not (shot.image_rect.colliderect(monster.image_rect)):
                    continue
                if monster.health > shot.damage:
                    monster.health -= shot.damage
                else:
                    monsters.remove(monster)
                shots.remove(shot)
                cls.destruction_sound.play()
                
                # Некоторые выстрелы и монстры могут быть убиты, поэтому неправильно будет работать со старыми данными, поэтому мы должны сделать тоже самое с новыми данными, пока не останется ни одного столкновения
                checked_shots_in_next_function, monsters = cls.destroy_monsters_in_touch(shots[index:], monsters)
                return shots[:index] + checked_shots_in_next_function, monsters

        # Так как больше нет ни единого столкновения между пулею и монстром, то можно закончить функцию обработки столкновения монстров с выстрелами
        return shots, monsters

    # Создание изображений и звуков пуль, выпущенных человеком или осьминогом
    @classmethod
    def set_class_attributes(cls):
        cls.image = pg.image.load(f'{cls.__folder_path}/image/{cls.__name__}.png')
        if cls.__name__ == 'ElectricSphere':
            cls.image.set_colorkey('white')
        cls.radius = cls.image.get_rect()[2] // 2

        cls.creation_sound = pg.mixer.Sound(f'{cls.__folder_path}/creation_sound/{cls.__name__}.mp3')
        cls.destruction_sound = pg.mixer.Sound(f'{cls.__folder_path}/destruction_sound/{cls.__name__}.mp3')
        return cls


class FireBall(Shot):  # Огненный шар - пуля юноши
    __slots__ = ()
    damage = HUMAN_SHOT_DAMAGE
    speed = 1_000


class IceStar(Shot):  # Ледяная звезда - пуля девушки
    __slots__ = ()
    damage = HUMAN_SHOT_DAMAGE
    speed = 1_000


class ElectricSphere(Shot):  # Электрическая сфера (шаровая молния) - пуля осьминога
    __slots__ = ()
    damage = 20
    speed = 500


#  --------------------------------------------------------------------------------------------
#  Живые существа (те что ходят куда-либо)
#  --------------------------------------------------------------------------------------------


class Creature(Obj):  # Класс, представляющий логику работы всех живых существ в игре
    __slots__ = ()

    @staticmethod
    def distance(first_coords, second_coords):  # Функция, считающая расстояния между объектами по координатной теормеме Пифагора
        x1, y1 = first_coords
        x2, y2 = second_coords
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def move(self, aim_coords=None) -> None:  # Функция, заставляющая живых существ двигаться с оглядкой на скорость, стены и игровое поле
        distance_passed = 0
        x_step = y_step = None
        x_aim_coord, y_aim_coord = aim_coords

        speed = self.speed

        # Ускорение в 2 раза, если живое существо является человеком и находится под эффектом ускорителя
        if isinstance(self, Human):
            if time.time() - self.time_speed_increased < SpeedIncreaser.time_that_speed_stays_increased:
                speed *= SpeedIncreaser.multiplier

        # Увеличение скорости в 1.5 раза, если существо находится на льду
        if self.image_rect.collidelist(Field.ice_blocks_rects) != -1:
            speed *= 1.5 if isinstance(self, Monster) else 2

        # Само перемещение объекта с учётом окружающих стен
        while distance_passed < speed and not (x_step == y_step == 0):
            speed_minus_distance = speed - distance_passed
            axis_speed_step = 2 if speed_minus_distance > 2.8 else (0.5 if speed_minus_distance > 0.7 else 0.125)

            center_x, center_y = self.center
            x_difference, y_difference = x_aim_coord - center_x, y_aim_coord - center_y

            # Сделать смещения по x и y так, чтобы объект стал ближе к цели передвижения
            x_step = axis_speed_step * ((x_difference >= axis_speed_step) - (x_difference <= -axis_speed_step))
            y_step = axis_speed_step * ((y_difference >= axis_speed_step) - (y_difference <= -axis_speed_step))

            # Проверка способности существа двигаться по оси x
            self.x += x_step

            if type(self) is not Ghost and (self.body_rect.collidelist(Field.bricks_and_glass_blocks_rects) != -1 or
                                            self.body_rect.collidelist(Field.borders) != -1):
                self.x -= x_step
                x_step = 0

            # Проверка способности существа двигаться по оси y
            self.y += y_step

            if type(self) is not Ghost and (self.body_rect.collidelist(Field.bricks_and_glass_blocks_rects) != -1 or
                                            self.body_rect.collidelist(Field.borders) != -1):
                self.y -= y_step
                y_step = 0

            # Вычисление расстояния, которое монстр смог пройти за одну работу функции
            distance_passed += self.distance(first_coords=(0, 0), second_coords=(x_step, y_step))


class Human(Creature):  # Класс человек (выживальщики срели монстров ночью)
    __slots__ = ('shots', 'health', 'amount_of_shots') + ('left', 'right', 'up', 'down') + ('body_width', 'body_height') + ('time_speed_increased',)

    # Скорость и количество патронов человека
    speed = 140 / FPS
    spawn_with_amount_of_shots = 20

    @property
    def image_rect(self) -> pg.Rect:  # Представление размеров изображения объекта с помощью координат, длины и ширины
        return pg.Rect(self.x + 10, self.y + 2, 20, 35)

    @property
    def body_rect(self):  # Представление размеры тела объекта с помощью координат, длины и ширины, это будет нужно позже для проверки столкновений с другими объектами (монстрами, магическими помощами)
        return pg.Rect(self.x + 11, self.y + 9, 18, 22)

    @property
    def center(self):  # Получение координта центра человеческого изображения
        return self.x + 20, self.y + 20

    def __init__(self, health: int, coords: tuple):  # Создание человека со своими параметрами (здоровье, количество патронов и так далее)
        super().__init__(coords)
        self.health = health
        self.shots = []
        self.amount_of_shots = self.spawn_with_amount_of_shots
        self.up = self.down = self.left = self.right = 0
        self.body_width, self.body_height = self.image_rect[2:]
        self.time_speed_increased = 0

    def manage_all_shot_events(self, shot_type, other_person):  # Управленние всеми событиями, связанными с пулями
        # Разрушение выстрелов, тронувших хотя бы один объект поля или вышедших за пределы поля
        shots = [shot for shot in self.shots if shot.no_smash_in_field_and_its_objects]

        body_rect_of_other_person = other_person.image_rect

        # Обработка всех столкновений пуль с человеком
        shots_after_damage = [shot for shot in shots if not shot.image_rect.colliderect(body_rect_of_other_person)]
        other_person.health -= shot_type.damage * (len(shots) - len(shots_after_damage))

        if other_person.health <= 0:
            shot_type.destruction_sound.play()
            return

        # Проигрыш звука разрашения, если пуля уничтожилась
        if len(self.shots) != len(shots_after_damage):
            shot_type.destruction_sound.play()
            self.shots = shots_after_damage

        # Обработка всех столкновений пуль с монстрами
        self.shots, Monster.monsters = shot_type.destroy_monsters_in_touch(self.shots, Monster.monsters)

        # Перемещение каждой пули
        [shot.move() for shot in self.shots]

        return other_person


class Boy(Human):  # Класс юноша
    __slots__ = ()
    shot = FireBall.set_class_attributes()


class Girl(Human):  # Класс девушка
    __slots__ = ()
    shot = IceStar.set_class_attributes()


class Monster(Creature):  # Класс, представляющий всех монстров (они атакуют людей)
    __slots__ = ('health',)
    __folder_path = 'parts_of_shooter_game/Monster'

    def __init__(self, coords: tuple[(int, float), (int, float)]):
        super().__init__(coords)
        self.health = self.spawn_with_health

    @classmethod
    def add_monster_if_time_has_come(cls, person1, person2, monster_type=None):  # Создать монстра, если прошло достаточно времени с момента прошлого создания
        if time.time() - cls.time_of_last_spawn < cls.next_time_between_appearances:
            return

        # Получение времени появления монстра и времени между их появлениями
        cls.time_of_last_spawn = time.time()
        cls.next_time_between_appearances = cls.get_time_between_appearances()

        # Выбор типа монстра, который будет создан
        if monster_type is None:
            random_number = random.randrange(100)

            for monster_type in (Octopus, BloodyMary, Death, Spider, Ghost):
                if random_number in monster_type.spawn_numbers:
                    break

        # Установка координат появления монстра, с учётом того, что они не могут появиться слишком близко к человеку или на недвижущихся объектах поля (стенах)
        min_distance = (150, 250)[monster_type is Octopus]
        monster = monster_type(coords=cls.generate_random_coords())
        while (cls.distance(monster.center, person1.center) < min_distance or  # Недалеко от первого человека
               cls.distance(monster.center, person2.center) < min_distance or  # Недалеко от второго человека
               monster in Field.objects):  # Монстр появился на объекте
            monster = monster_type(coords=cls.generate_random_coords())
        cls.monsters.append(monster)

    @classmethod
    def move_every_monster_on_the_field(cls, person1, person2, allow_sound):
        for monster_index, monster in enumerate(cls.monsters):
            # Расстояние от монстров до людей
            distance_from_person1 = cls.distance(monster.center, person1.center)
            distance_from_person2 = cls.distance(monster.center, person2.center)

            # Кровавая мэри распростаняет кровь, которая при касании высасывает здоровье людей
            if type(monster) is BloodyMary:
                if distance_from_person1 < monster.blood_radius:
                    person1.health = monster.calculate_damage(person1, allow_sound)
                    allow_sound = False
                if distance_from_person2 < monster.blood_radius:
                    person2.health = monster.calculate_damage(person2, allow_sound)
                monster.move()
                continue

            # Осьминог стреляет, если у него прошло время перезарядки с предыдущего выстрела и он при выстреле сможет попасть в недвижущегося человека
            if type(monster) is Octopus:
                monster.shoot_if_it_is_allowed_to(person1=person1, person2=person2)

            
            if monster.image_rect.colliderect(person1.image_rect):
                person1.health = monster.calculate_damage(person1, allow_sound)
                allow_sound = False
            if monster.image_rect.colliderect(person2.image_rect):
                person2.health = monster.calculate_damage(person2, allow_sound)

            # Монстр выбирает за каким человеком побежать, основываясь на том, кто из людей ближе
            person = (person1, person2)[distance_from_person2 <= distance_from_person1]
            monster.move(aim_coords=person.center)

    # Функция rect возвращает более маленький прямоугольник, чем функция image_rect, потому что иначе из-за слишком большого прямоугольника монстры не смогут протискиваться между стенами

    @property
    def body_rect(self):  # Получает координатный прямоугольник тела монстра, который можно будет использовать при анализе его столкновений с другими недвижущими объектами
        x, y, width, height = self.image_rect
        return pg.Rect(x + width // 4, y + height // 4, width // 2, height // 2)

    @classmethod
    def create_image(cls):
        # Создание изображения монстра с определённым уровнем прозрачности (невидимости)
        monster_image = pg.image.load(f'{cls.__folder_path}/image/{cls.__name__}.png').convert_alpha()
        if cls.__name__ == 'BloodyMary':
            monster_image.set_colorkey('white')
        monster_image.set_alpha(cls._image_transparency_on_level[Level.chosen])
        return monster_image

    def calculate_damage(self, person, allow_sound):
        if allow_sound:
            self.bite_sound.play()
        return person.health - self.damage if person.health > self.damage else 0

    @classmethod
    def get_time_between_appearances(cls):  # Получить рандомное время между появлениями (созданиями) в децисекундах
        return random.randrange(*cls.__time_between_appearances) / 10

    # Функция, которая получит максимальное и минимальное время между появлениями в децисекундах
    @classmethod
    def set_time_range_between_appearances(cls, min_time_in_deciseconds: int):
        cls.__time_between_appearances = (min_time_in_deciseconds, min_time_in_deciseconds + 20)
        cls.next_time_between_appearances = cls.get_time_between_appearances()

    @classmethod
    def set_class_attributes(cls): # Установка параметров, с которыми будут созданы монстры
        cls.speed = cls._speed_in_pixels_per_second_on_level[Level.chosen] / FPS
        
        spawn_numbers = cls._spawn_numbers_on_level[Level.chosen]  # Классовый аттрибут, который указывает при каких рандомно сгенерированных чисел, какие монстры заспавнятся
        if spawn_numbers != 'None':
            split_spawn_numbers = spawn_numbers.split('-')
            cls.spawn_numbers = range(int(split_spawn_numbers[0]), int(split_spawn_numbers[1]) + 1)
        else:
            cls.spawn_numbers = (None,)

        cls.image = cls.create_image()
        cls.body_width, cls.body_height = cls.image.get_rect()[2:]

        cls.bite_sound = pg.mixer.Sound(f'{cls.__folder_path}/bite_sound/{cls.__name__}.mp3')


# Виды монстров
class Ghost(Monster):  # Класс привидение
    __slots__ = ()
    spawn_with_health = 3 * HUMAN_SHOT_DAMAGE
    damage = 20 / FPS

    _spawn_numbers_on_level = dict(zip(LEVELS, ('None', '0-99', '0-82', '0-69', '0-63', '0-55', 'None')))
    _speed_in_pixels_per_second_on_level = dict(zip(LEVELS, (0, 60, 60, 60, 80, 100, 60)))
    _image_transparency_on_level = dict(zip(LEVELS, (255, 127, 127, 127, 31, 15, 255)))


class Spider(Monster):  # Класс паук
    __slots__ = ()
    spawn_with_health = 5 * HUMAN_SHOT_DAMAGE
    damage = 60 / FPS

    _spawn_numbers_on_level = dict(zip(LEVELS, ('None', 'None', '83-96', '70-86', '64-82', '56-79', 'None')))
    _speed_in_pixels_per_second_on_level = dict(zip(LEVELS, (0, 20, 20, 20, 40, 60, 20)))
    _image_transparency_on_level = dict(zip(LEVELS, (255, 191, 191, 191, 63, 31, 255)))


class Death(Monster):  # Класс смерть
    __slots__ = ()
    spawn_with_health = 1 * HUMAN_SHOT_DAMAGE
    damage = 200 / FPS

    _spawn_numbers_on_level = dict(zip(LEVELS, ('None', 'None', '97-99', '87-93', '83-90', '80-88', 'None')))
    _speed_in_pixels_per_second_on_level = dict(zip(LEVELS, (0, 100, 100, 100, 120, 140, 100)))
    _image_transparency_on_level = dict(zip(LEVELS, (255, 127, 127, 127, 47, 23, 255)))


class BloodyMary(Monster):  # Класс кровавая Мэри
    __slots__ = ('blood_radius',)
    spawn_with_health = 1 * HUMAN_SHOT_DAMAGE
    damage = 20 / FPS

    _spawn_numbers_on_level = dict(zip(LEVELS, ('None', 'None', 'None', '93-95', '91-94', '89-93', 'None')))
    _speed_in_pixels_per_second_on_level = dict(zip(LEVELS, (0, 30, 30, 30, 40, 50, 30)))
    _image_transparency_on_level = dict(zip(LEVELS, (255, 255, 255, 255, 79, 39, 255)))

    def __init__(self, coords):
        super().__init__(coords)
        self.blood_radius = 0

    def move(self, *args, **kwargs) -> None:  # Распростанение крови Мэри (увеличение радиуса пятна крови)
        self.blood_radius += self.speed


class Octopus(Monster):  # Класс Осьминог
    __slots__ = ('last_time_shot_was_made',)
    shot = ElectricSphere.set_class_attributes()
    spawn_with_health = 3 * HUMAN_SHOT_DAMAGE
    damage = 40 / FPS

    _spawn_numbers_on_level = dict(zip(LEVELS, ('None', 'None', 'None', '96-99', '95-99', '94-99', 'None')))
    _speed_in_pixels_per_second_on_level = dict(zip(LEVELS, (0, 40, 40, 40, 60, 80, 40)))
    _image_transparency_on_level = dict(zip(LEVELS, (255, 127, 127, 127, 47, 23, 255)))

    def __init__(self, coords):
        super().__init__(coords)
        self.last_time_shot_was_made = time.time()

    @classmethod
    def manage_all_shot_events(cls, shot_type, people: tuple):
        # Разрушение пуль осьминога, коснувшихся любых стен поля или вышедшего
        shots = [shot for shot in cls.shots if shot.no_smash_in_field_and_its_objects]

        for person in people:
            # Разрушение пуль осьминога, коснувшихся любого человека и нанесение урона человеку пулей, коснувшейся его
            shots_after_damage = [shot for shot in shots if not shot.image_rect.colliderect(person.image_rect)]
            person.health -= shot_type.damage * (len(shots) - len(shots_after_damage))
            shots = shots_after_damage

            # Проишрыш звука уничтожения пули, если пуля исчезла
            if len(cls.shots) != len(shots_after_damage):
                shot_type.destruction_sound.play()
                cls.shots = shots_after_damage

        people = [None if person.health <= 0 else person.health for person in people]

        # Передвижение каждой пули
        [shot.move() for shot in cls.shots]

        return people

    def get_axis_directions_of_the_shot(self, person):   # Проверка, в каких случаях осьминог выстрелит и попадёт человека
        if self.shot.image.get_rect(center=self.center).collidelist(Field.bricks_rects) != -1:
            return 0, 0

        person_center_x, person_center_y = person.center
        octopus_center_x, octopus_center_y = self.center
        distance_from_person = self.distance(self.center, person.center)

        # Без движения пули
        x_shift = y_shift = 0
        shot_radius = self.shot.radius

        # При движении по диагонали
        if abs(abs(octopus_center_y - person_center_y) - abs(octopus_center_x - person_center_x)) < \
                person.body_width // 2 + person.body_height // 2 + 2 * shot_radius - 1:
            x_shift = (-1, 1)[person_center_x - octopus_center_x > 0]
            y_shift = (-1, 1)[person_center_y - octopus_center_y > 0]

            # Проверка на то, что пуля врежется в стену прежде чем успеет попасть в человека
            for brick_center_x, brick_center_y in Field.bricks_centers:
                if abs(abs(octopus_center_y - brick_center_y) - abs(octopus_center_x - brick_center_x)) > \
                        50 + 2 * shot_radius + 2:
                    continue

                # Врежется ли пуля в стены рядом с осьминогом
                if (brick_center_x - octopus_center_x > 0) == (x_shift > 0) or \
                        (brick_center_y - octopus_center_y > 0) == (y_shift > 0):
                    if abs(brick_center_x - octopus_center_x) + abs(brick_center_y - octopus_center_y) <= \
                            50 + 2 * shot_radius + 2:
                        x_shift = y_shift = 0
                        break

                # Врежется ли пуля в стены, находящиеся в том же направлении от осьминога, что и человек
                if (person_center_x - octopus_center_x > 0) != (brick_center_x - octopus_center_x > 0):
                    continue
                if (person_center_y - octopus_center_y > 0) != (brick_center_y - octopus_center_y > 0):
                    continue

                # Если при этом стена ближе, чем человек, то есть закрывает человека
                if distance_from_person > self.distance(self.center, (brick_center_x, brick_center_y)):
                    x_shift = y_shift = 0
                    break

        # При движении по вертикали
        if abs(person_center_x - octopus_center_x) < person.body_width // 2 + shot_radius - 1:
            y_shift = (-1, 1)[person_center_y - octopus_center_y > 0]
            x_shift = 0

            # Проверка пули на её разрушение об стену прежде, чем она доберётся до человека
            for brick_center_x, brick_center_y in Field.bricks_centers:
                # Если выстрел не врежится ни в какую стену
                if abs(octopus_center_x - brick_center_x) > 25 + shot_radius + 2:
                    continue

                # Врежется ли пуля в стены, находящиеся в том же направлении от осьминога, что и человек
                if (person_center_y - octopus_center_y > 0) != (brick_center_y - octopus_center_y > 0):
                    continue

                # Если при этом стена ближе, чем человек, то есть закрывает человека
                if distance_from_person > self.distance(self.center, (brick_center_x, brick_center_y)):
                    y_shift = 0
                    break

        # При движении по горизонтали
        if abs(person_center_y - octopus_center_y) < person.body_height // 2 + shot_radius - 1:
            x_shift = (-1, 1)[person_center_x - octopus_center_x > 0]
            y_shift = 0

            # Проверка пули на её разрушение об стену прежде, чем она доберётся до человека
            for brick_center_x, brick_center_y in Field.bricks_centers:
                # Если выстрел не врежится ни в какую стену
                if abs(octopus_center_y - brick_center_y) > 25 + shot_radius + 2:
                    continue

                # Врежется ли пуля в стены, находящиеся в том же направлении от осьминога, что и человек
                if (person_center_x - octopus_center_x > 0) != (brick_center_x - octopus_center_x > 0):
                    continue

                # Если при этом стена ближе, чем человек, то есть закрывает человека
                if distance_from_person > self.distance(self.center, (brick_center_x, brick_center_y)):
                    x_shift = 0
                    break

        return x_shift, y_shift

    def shoot_if_it_is_allowed_to(self, person1, person2):  # Функция "выстрели, если можно"
        # Не нужно осьминогу стрелять в человека, если он уже его кусает
        if self.image_rect.colliderect(person1.image_rect) or self.image_rect.colliderect(person2.image_rect):
            return

        # Слишком рано стрелять
        if time.time() - self.last_time_shot_was_made < 1:
            return

        x_shift1, y_shift1 = self.get_axis_directions_of_the_shot(person1)
        x_shift2, y_shift2 = self.get_axis_directions_of_the_shot(person2)

        # Не нужно стрелять пулей, которая не будет двигаться
        if x_shift1 == x_shift2 == y_shift1 == y_shift2 == 0:
            return

        distance_from_person1 = self.distance(self.center, person1.center)
        distance_from_person2 = self.distance(self.center, person2.center)

        # Осьминог выбирает, в кого из людей стрельнуть
        if x_shift1 == y_shift1 == 0 or distance_from_person2 < distance_from_person1 and \
                not (x_shift2 == y_shift2 == 0):
            x_shift, y_shift = x_shift2, y_shift2
        else:
            x_shift, y_shift = x_shift1, y_shift1

        self.last_time_shot_was_made = time.time()

        octopus_center_x, octopus_center_y = self.center
        shot_radius = self.shot.radius

        self.shots.append(self.shot(coords=(octopus_center_x - shot_radius, octopus_center_y - shot_radius),
                                    coords_shift=(x_shift, y_shift)))
        self.shot.creation_sound.play()
        
        
#  --------------------------------------------------------------------------------------------
#  Анимация
#  --------------------------------------------------------------------------------------------


LOAD_IMAGE = pg.image.load
male_sprite_path = 'parts_of_shooter_game/boy_spritesheet/boy_'
female_sprite_path = 'parts_of_shooter_game/girl_spritesheet/girl_'


class SpriteSheet:  # Класс, представляющий анимацию
    class Male:
        # Установить направления взгляда юноши и начальный кадр юноши прежде, чем игра начнётся
        @classmethod
        def set_class_attributes(cls):
            cls.frame_number = 0
            cls.direction = 'down'

        # Анимация движения юноши в каждом направленнии
        down = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(1, 5)]
        left = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(5, 9)]
        right = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(9, 13)]
        up = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(13, 17)]
        down_right = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(17, 21)]
        down_left = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(21, 25)]
        up_left = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(25, 29)]
        up_right = [LOAD_IMAGE(f'{male_sprite_path}{frame}.png') for frame in range(29, 33)]

    class Female:
        # Установить направления взгляда девушки и начальный кадр девушки прежде, чем игра начнётся
        @classmethod
        def set_class_attributes(cls):
            cls.frame_number = 0
            cls.direction = 'up'

        # Анимация движения девушки в каждом направленнии
        down = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(1, 5)]
        left = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(5, 9)]
        right = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(9, 13)]
        up = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(13, 17)]
        down_right = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(17, 21)]
        down_left = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(21, 25)]
        up_left = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(25, 29)]
        up_right = [LOAD_IMAGE(f'{female_sprite_path}{frame}.png') for frame in range(29, 33)]

    @classmethod
    def change_direction(cls, is_male, up, down, left, right):  # Функция, меняющая направление для передвижения человека и анимирования этого передвижения
        x_direction, y_direction = right - left, down - up
        person = cls.Male if is_male else cls.Female
        if x_direction == y_direction == 0:
            person.frame_number = 0
        else:
            axis_directions = [('up', '', 'down')[y_direction + 1], ('left', '', 'right')[x_direction + 1]]
            person.direction = '_'.join(axis_directions).strip('_')
        return getattr(person, person.direction)[int(person.frame_number)]


#  --------------------------------------------------------------------------------------------
#  Класс для группировки частей анимации (создано исключительно для оптимизации работы кода)
#  --------------------------------------------------------------------------------------------


class Chunk:  # Класс для группировки, чтобы можно было отрисовать несколько объектов сразу а не по отдельности, что в несколько раз ускоряет работу программы
    # Функция convert ускоряет отрисовку объектов на экране в несколько раз!
    horror_background = pg.image.load(f'{MAIN_FOLDER_PATH}/horror_background.png').convert()

    @classmethod
    def place_every_static_object_on_surface(cls):
        # Создание пустых поверхностей
        cls.bushes = pg.Surface((50 * (COLUMNS + 2), 50 * (ROWS + 2)))
        cls.bushes.fill('Yellow')
        cls.bushes.set_colorkey('Yellow')

        cls.other_static_field_objects = pg.Surface((50 * (COLUMNS + 2), 50 * (ROWS + 2)))
        cls.other_static_field_objects.set_colorkey('Yellow')
        cls.other_static_field_objects.fill('Yellow')

        # Функция convert ускоряет отрисовку объектов на экране в несколько раз!
        cls.background = pg.Surface((50 * (COLUMNS + 2), 50 * (ROWS + 2))).convert()

        # Отрисовка изображения фона и игрового поля на созданной поверхности
        cls.background.blit(cls.horror_background, (0, 0))
        cls.background.blit(Field.field, (50, 50))

        # Отрисовка каждого недвижущегося объекта на созданной поверхности
        for obj in Field.objects:
            if type(obj) is Bush:
                cls.bushes.blit(obj.image, obj.coords)
            else:
                cls.other_static_field_objects.blit(obj.image, obj.coords)

        # Написании информации об уровне
        level_name_label = GameFont.render(size=35, text=Level.chosen, foreground='white')
        cls.other_static_field_objects.blit(level_name_label, (950, 5))

        # Написание "xp человека" and отрисовка шкалы здоровья на экране
        boy_health_label = GameFont.render(size=20, text='xp юноши', foreground='green', background=DARK_GRAY)
        girl_health_label = GameFont.render(size=20, text='xp девушки', foreground='red', background=DARK_GRAY)

        cls.other_static_field_objects.blit(boy_health_label, (18, 5))
        cls.other_static_field_objects.blit(girl_health_label, (5, 25))

        pg.draw.rect(cls.other_static_field_objects, 'Gray', (100, 10, 400, 15))
        pg.draw.rect(cls.other_static_field_objects, 'Gray', (100, 30, 400, 15))

    @classmethod
    def change_field_color_and_time(cls, color, text_hours):  # Эффект наступления темноты, либо рассвета
        Field.field.fill(color)
        cls.background.blit(cls.horror_background, (0, 0))
        cls.background.blit(Field.field, (50, 50))
        game_hours_label = GameFont.render(size=35, text=text_hours, foreground='white', is_smoothy=True)
        cls.background.blit(game_hours_label, (670, 5))


#  --------------------------------------------------------------------------------------------
#  Шрифт текста в игре
#  --------------------------------------------------------------------------------------------


class GameFont:  # Класс дя создания текстовых наклеек в шрифте Arial
    @classmethod
    def render(cls, size: int, text: str, foreground: tuple[str, tuple], background=None, is_smoothy=False):
        text_font = pg.font.Font('parts_of_shooter_game/horror_font/creepster.otf', size=size)
        if background is None:
            return text_font.render(text, is_smoothy, foreground)
        return text_font.render(text, is_smoothy, foreground, background)


#  --------------------------------------------------------------------------------------------
#  Неживые объекты (ограждения)
#  --------------------------------------------------------------------------------------------


class Block(Obj):  # Класс, представляющий неживые объекты игрового поля
    __slots__ = ()
    __folder_path = 'parts_of_shooter_game/Block'

    @classmethod
    def create_image(cls):
        # Создание изображений неживых объектов
        image = pg.image.load(f'{cls.__folder_path}/image/{cls.__name__}.png').convert()
        if cls.__name__ == 'Glass':
            image.set_colorkey('black')
        return image

    @classmethod
    def set_class_attributes(cls, spawn_numbers: str):
        cls.image = cls.create_image()

        split_spawn_numbers = spawn_numbers.split('-')
        cls.spawn_numbers = range(int(split_spawn_numbers[0]), int(split_spawn_numbers[1]) + 1)


# Типы неживых объектов, которым достались все переменные и команды от базового класс Block
class Glass(Block):  # Класс стеклянный блок
    pass


class Bush(Block):  # Класс куст
    pass


class Brick(Block):  # Класс кирпичная стена
    pass


class Ice(Block):  # Класс лёдяной квадрат
    pass


#  --------------------------------------------------------------------------------------------
#  Поле, со всеми его объектами
#  --------------------------------------------------------------------------------------------


class Field(Obj):  # Класс поля со всеми его недвижущимися объектами
    # creating field and getting its rectangle and rects of its borders
    field = pg.Surface((50 * COLUMNS, 50 * ROWS)).convert()  # Создание поля
    borders = [pg.Rect(48, 48, WIDTH - 48 * 2, 2), pg.Rect(48, 50, 2, HEIGHT - 48 * 2), pg.Rect(48, HEIGHT - 50, WIDTH - 48 * 2, 2), pg.Rect(WIDTH - 50, 50, 2, HEIGHT - 48 * 2)]  # Создание невидимых границ поля

    @classmethod
    def init(cls):
        # Создание поля с границами
        cls.objects = []
        cls.bricks_and_glass_blocks = []
        cls.magic_helps = []
        cls.create_borders()

    @classmethod
    def create_borders(cls):  # Создать стеклянные границы
        for x in range(0, 50 * (COLUMNS + 2), 50):
            for y in (0, 50 * (ROWS + 1)):
                cls.add_object(Glass(coords=(x, y)))

        for y in range(50, 50 * (ROWS + 1), 50):
            for x in (0, 50 * (COLUMNS + 1)):
                cls.add_object(Glass(coords=(x, y)))

    @classmethod
    def remove_borders(cls):  # Убрать стеклянные границы
        for x in range(0, 50 * (COLUMNS + 2), 50):
            for y in (0, 50 * (ROWS + 1)):
                cls.pop_object(Glass(coords=(x, y)))

        for y in range(50, 50 * (ROWS + 1), 50):
            for x in (0, 50 * (COLUMNS + 1)):
                cls.pop_object(Glass(coords=(x, y)))

    @classmethod
    def add_magic_help_if_time_has_come(cls, magic_help_type=None):  # Создать магическую помощь, если прошло достаточно времени с предыдущего создания магической помощи
        random_number = random.randrange(1, 101)
        if time.time() - MagicHelp.time_of_last_spawn < MagicHelp.get_time_between_appearances():
            return

        if magic_help_type is None:
            for magic_help_type in (SpeedIncreaser, Healer, ShotsRestorer):
                if random_number in magic_help_type.spawn_numbers:
                    break

        magic_help = None
        while magic_help is None or magic_help in cls.objects:
            magic_help = magic_help_type(coords=cls.generate_random_coords())

        cls.magic_helps.append(magic_help)
        MagicHelp.time_of_last_spawn = time.time()

    @classmethod
    def remove_magic_if_there_is_a_reason(cls, person, magic_helps=None):
        if magic_helps is None:
            magic_helps = cls.magic_helps
        # Исчезновение магической помощи с игрового поля
        for magic_help in magic_helps:
            # Если человек коснулся магической помощи, добавить здоровья или патронов или скорости
            if magic_help.image_rect.colliderect(person.image_rect):
                if type(magic_help) is Healer:
                    person.health = min(200, person.health + magic_help.health)
                elif type(magic_help) is SpeedIncreaser:
                    person.time_speed_increased = time.time()
                else:
                    person.amount_of_shots += magic_help.amount_of_shots
                magic_helps.remove(magic_help)
                magic_help.sound_when_collected.play()
                return cls.remove_magic_if_there_is_a_reason(person=person, magic_helps=magic_helps)

            # Если магическая помощь лежала на поле слишком долго, она исчезнет
            if time.time() - magic_help.time > magic_help.time_lying_on_the_field:
                magic_helps.remove(magic_help)
                return cls.remove_magic_if_there_is_a_reason(person=person, magic_helps=magic_helps)
        return magic_helps

    @classmethod
    def add_object(cls, obj):
        # Добавить недвижущийся объект на поле туда, куда надо
        if obj in cls.objects:
            return
        cls.objects.append(obj)
        if obj.__class__.__name__ in ('Glass', 'Brick'):
            cls.bricks_and_glass_blocks.append(obj)

    @classmethod
    def pop_object(cls, obj):
        # Убрать недвижущийся объект из списка недвижущихся объектов
        cls.objects.remove(obj)
        if obj.__class__.__name__ in ('Glass', 'Brick'):
            cls.bricks_and_glass_blocks.remove(obj)
        return obj

    @classmethod
    def create_lists_for_types_of_static_objects_except_magic_helps(cls):  # Создание этих списков важны для оптимизации работы кода (а именно, чтобы он работал быстрее)
        cls.glass_blocks = [obj for obj in cls.objects if obj.__class__.__name__ == 'Glass']
        cls.bushes = [obj for obj in cls.objects if obj.__class__.__name__ == 'Bush']
        cls.ice_blocks = [obj for obj in cls.objects if obj.__class__.__name__ == 'Ice']
        cls.bricks = [obj for obj in cls.objects if obj.__class__.__name__ == 'Brick']

        cls.bricks_and_glass_blocks_rects = [obj.image_rect for obj in cls.bricks_and_glass_blocks]
        cls.glass_blocks_rects = [obj.image_rect for obj in cls.glass_blocks]
        cls.bushes_rects = [obj.image_rect for obj in cls.bushes]
        cls.ice_blocks_rects = [obj.image_rect for obj in cls.ice_blocks]
        cls.bricks_rects = [obj.image_rect for obj in cls.bricks]

        cls.glass_blocks_centers = [obj.center for obj in cls.glass_blocks]
        cls.bushes_centers = [obj.center for obj in cls.bushes]
        cls.ice_blocks_centers = [obj.center for obj in cls.ice_blocks]
        cls.bricks_centers = [obj.center for obj in cls.bricks]

    @classmethod
    def there_is_closed_space_in_it(cls, obj, possible_new_object, checked_objects=None):  # Проверка, есть ли на карте замкнутые или слишком длинные цепочки стен
        if checked_objects is None:
            checked_objects = []
        neighbour_coord_list = []

        # Проверка каждого соседней клетки по диагонали вертикали или горизонтали
        for x in (obj.x - 50, obj.x, obj.x + 50):
            for y in (obj.y - 50, obj.y, obj.y + 50):
                neighbor_object = Block(coords=(x, y))
                if neighbor_object == obj:
                    continue

                # Бесполезно проверять кусты или ледяные клетки, потому что люди и монстры могут ходить по таким клеткам
                if neighbor_object not in cls.bricks_and_glass_blocks:
                    continue

                # Мне не нужны слишком длинные цепи стен, либо замкнутые пространства
                if len(checked_objects) > 5:
                    return 1

                # Если количество проверенных объектов менее 4-х замкнутое пространство (пространство, в котором застрянешь, и из которого нельзя будет выбраться) не возникнет
                if len(checked_objects) >= 3 and neighbor_object == possible_new_object:
                    return 1

                # Если уже соседний объект был проверен, то зачем нам его опять проверять?
                if neighbor_object in checked_objects:
                    continue

                checked_objects.append(neighbor_object)

                # Проверка каждого соседа этого блока на замыкание цепочек из кирпичных стен и стекольных блоков
                neighbour_coord_list.append(cls.there_is_closed_space_in_it(neighbor_object, possible_new_object, checked_objects[:]))

        if neighbour_coord_list:
            return any(neighbour_coord_list)
        else:
            return 0

    @classmethod
    def place_all_not_moving_objects(cls):  # Создание недвижущихся объектов, за исключением магических помощей, на игровом поле
        cls.init()
        amount_of_objects_now = 0
        future_amount_of_objects = random.randrange(ROWS * COLUMNS // 3 * 2 - 15, ROWS * COLUMNS // 3 * 2 + 16)

        # Создание определённого количества объектов
        while amount_of_objects_now < future_amount_of_objects:
            # Создание недвижимого объекта, так что он не расположен на другом недвижущемся объекте
            the_object = Block(coords=cls.generate_random_coords())
            if the_object in cls.objects:
                continue

            # Объекты не должны быть по углам, чтобы там мог заспавниться человек в начале игры
            if the_object.x in (50, 100, (COLUMNS - 1) * 50, COLUMNS * 50):
                if the_object.y in (50, 100, (ROWS - 1) * 50, ROWS * 50):
                    continue

            random_not_moving_object_appender = random.randrange(100)
            if random_not_moving_object_appender in Ice.spawn_numbers:
                # Добавка ледяных блоков и создание соседних ледяные блоки по горизонтали, чтобы монстры и люди могли
                # быстрее по горизонтали, потому что поле по горизонтали длиннее, и люди должны добраться до магических подсказок, прежде чем они исчезнут.

                cls.add_object(Ice(coords=the_object.coords))
                saved_the_object = Block(coords=the_object.coords)
                ice_on_side_counter = 0
                while the_object not in cls.objects and the_object.x >= 50 and ice_on_side_counter < 2:
                    cls.add_object(Ice(coords=the_object.coords))
                    the_object.x -= 50
                    ice_on_side_counter += 1
                    amount_of_objects_now += 1
                the_object.x = saved_the_object.x + 50
                ice_on_side_counter = 0
                while the_object not in cls.objects and the_object.x <= COLUMNS * 50 and ice_on_side_counter < 2:
                    cls.add_object(Ice(coords=the_object.coords))
                    the_object.x += 50
                    ice_on_side_counter += 1
                    amount_of_objects_now += 1
                amount_of_objects_now += 1
            elif random_not_moving_object_appender in Bush.spawn_numbers:
                # Добавка кустов и создание соседних кустов по вертикали, чтобы высоких монстров и дюлей было не видно при проходе через них, что усложняет геймплей 
                cls.add_object(Bush(coords=the_object.coords))
                amount_of_objects_now += 1
                if Block(coords=(the_object.x, the_object.y - 50)) not in cls.objects and the_object.y >= 50:
                    cls.add_object(Bush(coords=(the_object.x, the_object.y - 50)))
                    amount_of_objects_now += 1
                if Block(coords=(the_object.x, the_object.y + 50)) not in cls.objects and the_object.y <= ROWS * 50:
                    cls.add_object(Bush(coords=(the_object.x, the_object.y + 50)))
                    amount_of_objects_now += 1
            elif random_not_moving_object_appender in Glass.spawn_numbers:
                # Создание стеклянного блока на поле, если в результате создания не будет замкнутого пространств, через которое не пройдёт человек
                glass_obj = Glass(coords=the_object.coords)
                cls.add_object(glass_obj)
                if cls.there_is_closed_space_in_it(obj=glass_obj, possible_new_object=glass_obj):
                    cls.pop_object(glass_obj)
                else:
                    amount_of_objects_now += 1
            else:
                # Создание кирпичной стены на поле, если в результате создания не будет замкнутого пространств, через которое не пройдёт человек
                brick_obj = Brick(coords=the_object.coords)
                cls.add_object(brick_obj)
                if cls.there_is_closed_space_in_it(obj=brick_obj, possible_new_object=brick_obj):
                    cls.pop_object(brick_obj)
                else:
                    amount_of_objects_now += 1

        cls.remove_borders()
        cls.create_lists_for_types_of_static_objects_except_magic_helps()
        Chunk.place_every_static_object_on_surface()


#  --------------------------------------------------------------------------------------------
#  Остальные части игры
#  --------------------------------------------------------------------------------------------


class Game:  # Класс, работающий со временем, запуском и остановкой игры, описаниями
    # Функция, которая остановит игру и покажет результат игры (победа или поражение)
    @staticmethod
    def show_result(result_text):
        SCREEN.fill(DARK_GRAY)
        result_label = GameFont.render(size=120, text=result_text,
                                       foreground=('red', 'green')[result_text == 'Вы выжили!'])

        SCREEN.blit(result_label, result_label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pg.display.update()
        pg.time.wait(3000)
        pg.mixer.music.stop()
        game_intro()
        return

    @classmethod
    def set_chunks(cls):
        [cls.bushes.blit(obj.image, obj.coords) for obj in Field.bushes]
        [cls.other_static_field_objects.blit(obj.image, obj.coords)
         for obj in Field.objects if obj.__class__.__name__ != 'Bush']


class Level:  # Класс, представляющий описание каждого из уровней
    chosen = 'тренировочный'

    # Информация для каждого уровня игры
    info = {
        'тренировочный': ['Ночь очень коротка.',
                          'Никакие монстры не появятся.',
                          'Но не забывайте, что вы можете',
                          'убивать друг в друга.',
                          'Удачи в убийствах!'],
        'лёгкий': ['Ночь коротка.',
                   'Иногда вас будут атаковаить привидения.',
                   'Привидения могут проходить сквозь стены.',
                   'Легко найти магическую помощь.',
                   'Не так легко, как кажется!'],
        'средний': ['Ночь немного дольше, чем на лёгком уровне.',
                   'привидения, пауки и смерти будут атаковать',
                   'вас. Пауки убивают быстрее, чем привидения',
                   'и пауков трудно убить.',
                   'Смерть убивает сумашедше быстро.',
                   'Также смерть очень быстро бегает.',
                   'Будьте осторожны!'],
        'сложный': ['Ночь довольно длинна. Привидения, пауки,',
                    'смерти, кровавые Мэри и осьминоги будут',
                    'атаковать вас. Кровавые Мэри',
                    'не двигаются, но они могут убить вас,',
                    'распространяя свою кровь. Осьминоги',
                    'могут стрелять в вас элестрической магией.',
                    'Бу-у-у! Не испугайтесь его могущества!'],
        'безумный': ['Ночь длится очень долго.',
                    'Монстры начинают появляться чаще.',
                    'Их тяжелее увидеть.',
                    'Монстры и кровь Мэри двигаются',
                    'очень быстро.',
                    'Экстремальной ночи!'],
        'невозможный': ['Ночь безумно длинная.',
                       'Монстры появляются очень часто и',
                       'их практически невозможно увидеть.',
                       'Невозможно найти целитель и',
                       'ускоритель. Монстры и кровь Мэри',
                       'двигаются чрезвычайно быстро!',
                       'Легенда гласит: никто не выжил!'],
        'обучающий': ['Этот уровень поможет вам научиться',
                      'играть в эту игру.',
                      'Предлагаем попробовать!']
    }

    class TextStyle:
        # Размер и цветовой параметр текста для названия каждого уровня
        size = 60
        text_size = 40
        fg_level = (95, 23, 5)

        # Большой цветной текст для каждого уровня
        name = {'тренировочный': GameFont.render(size=size, text='тренировочный', foreground=BLOODY_RED, background=DARK_GRAY),
                'лёгкий': GameFont.render(size=size, text='лёгкий', foreground=fg_level),
                'средний': GameFont.render(size=size, text='средний', foreground=fg_level),
                'сложный': GameFont.render(size=size, text='сложный', foreground=fg_level),
                'безумный': GameFont.render(size=size, text='безумный', foreground=fg_level),
                'невозможный': GameFont.render(size=size, text='невозможный', foreground=fg_level),
                'обучающий': GameFont.render(size=size, text='обучающий', foreground=fg_level)}


class LevelChunk:  # Этот класс оптимизирует отображение основного меню игры
    # Создание прозрачных чанки (невидимых поверхностей для отображения тектса) для уровней
    level_surfaces = {level_name: pg.Surface((820, 670)) for level_name in LEVELS}
    for level_name in LEVELS:
        level_surfaces[level_name].set_colorkey('black')

    # Отобразить информацию об уровне на экране
    font_size = Level.TextStyle.text_size
    for level_name, level_surface in level_surfaces.items():
        y_blit_coord = 10
        for level_string_info in Level.info[level_name]:
            level_info_label = GameFont.render(size=font_size, text=level_string_info, foreground=BLOODY_RED)
            level_surface.blit(level_info_label, (10, y_blit_coord))
            y_blit_coord += font_size


def game_intro():
    # Музыка на основном меню
    pg.mixer.music.load(f'{MAIN_FOLDER_PATH}/horror_intro_music.mp3')
    pg.mixer.music.play(-1)
    
    level_button_click = pg.mixer.Sound(f'{MAIN_FOLDER_PATH}/level_button_click.mp3')  # Звук при нажатии на кнопки в главном меню игры
    
    play_button = GameFont.render(size=60, text='Начать ночь!', foreground='brown', background=DARK_GRAY)
    level_info_keys = ('practice', 'easy', 'normal', 'hard', 'extreme', 'impossible', 'learn')
    level_info_keys_rus = list(Level.info.keys())

    while True:
        # Отображенние на экране фона игры с надписью "Твоя цель — выжить этой ночью..."
        SCREEN.blit(Chunk.horror_background, (0, 0))
        rule_label = GameFont.render(size=60, text='Твоя цель — выжить этой ночью...', foreground=LIGHT_GRAY)
        SCREEN.blit(rule_label, (170, 30))

        # Отображенние названий всех уровней на экране
        for level_name in level_info_keys_rus:
            level_index = level_info_keys_rus.index(level_name)
            y_coord = 120 + ((ROWS + 2) * 50 - 200) // (len(level_info_keys_rus) - 1) * level_index
            SCREEN.blit(Level.TextStyle.name[level_info_keys_rus[level_index]], (40, y_coord))

        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()  # закрыть окно с игрой
                return

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_coords = pg.mouse.get_pos()

                # Запуск игры, если кнопка "начать" нажата
                if play_button.get_rect(topleft=(880, (ROWS + 2) * 50 - 100)).collidepoint(mouse_coords):
                    level_button_click.play()
                    pg.mixer.music.stop()
                    shooter_game() if Level.chosen != 'обучающий' else game_help()
                    return

                # Выбор уровня по ннажатию мышкой на название уровня в меню
                for level_name in level_info_keys_rus:
                    level_index = level_info_keys_rus.index(level_name)
                    y_coord = 120 + ((ROWS + 2) * 50 - 200) // (len(level_info_keys_rus) - 1) * level_index

                    if Level.TextStyle.name[level_info_keys_rus[level_index]].get_rect(topleft=(40, y_coord)).collidepoint(mouse_coords):
                        if Level.chosen != level_name:
                            level_button_click.play()
                        Level.chosen = level_name

                # Создание фона для текста выбранного уровня
                for level_name in level_info_keys_rus:
                    text_size = Level.TextStyle.size
                    bg = (None, DARK_GRAY)[Level.chosen == level_name]
                    fg = (Level.TextStyle.fg_level, BLOODY_RED)[Level.chosen == level_name]
                    Level.TextStyle.name[level_name] = GameFont.render(size=text_size, text=level_name, foreground=fg, background=bg)

        SCREEN.blit(LevelChunk.level_surfaces[Level.chosen], (500, 100))

        # Отрисовка кнопки начала игры
        SCREEN.blit(play_button, (880, (ROWS + 2) * 50 - 100))

        pg.display.update()
        CYCLES_PER_SECOND.tick(FPS)


def shooter_game():
    # Музыка в игре
    pg.mixer.music.load(f'{MAIN_FOLDER_PATH}/horror_game_music.mp3')
    pg.mixer.music.play(-1)

    frames_passed_since_game_started = 0

    level_index = LEVELS.index(Level.chosen)

    # Создание людей и их направления движения
    human_health = 100 - 10 * level_index
    boy = Boy(health=human_health, coords=(55, 55))
    girl = Girl(health=human_health, coords=(50 * (COLUMNS + 1) - 45, 50 * (ROWS + 1) - 45))

    boy.down = girl.up = 1
    SpriteSheet.Male.set_class_attributes()
    SpriteSheet.Female.set_class_attributes()

    # Создание всех недвижущихся объектов кроме магической помощи

    objects_spawn_numbers = ('0-11', '12-61', '62-76', '77-99')  # Чисда, которые должны случайно сгенерироваться, чтобы получился лёд, стекло, куст или кирпичная стена
    object_types = (Ice, Glass, Bush, Brick)

    for spawn_numbers, field_object in zip(objects_spawn_numbers, object_types):
        field_object.set_class_attributes(spawn_numbers=spawn_numbers)

    Field.place_all_not_moving_objects()

    # Установка параметров типов монстров
    for monster_class in (Ghost, Spider, Death, BloodyMary, Octopus):
        monster_class.set_class_attributes()

    # 10 в степени 100 означает, что монстр никогда не заспавнится, ибо вселенная задолюбается ждать
    Monster.set_time_range_between_appearances(min_time_in_deciseconds=(10 ** 100, 50, 50, 50, 40, 30)[level_index])
    MagicHelp.set_time_range_between_appearances(min_time_in_deciseconds=(140, 160, 180, 200, 180, 160)[level_index])

    # Устаановка вероятности появления магической помощи
    for magic_help_class in (ShotsRestorer, SpeedIncreaser, Healer):
        magic_help_class.set_class_attributes()

    # Старт анимации людей
    SpriteSheet.Male.set_class_attributes()
    SpriteSheet.Female.set_class_attributes()

    # В начале игры ещё нет монстров
    Monster.monsters = []
    Octopus.shots = []

    # setting start time
    Monster.time_of_last_spawn = MagicHelp.time_of_last_spawn = time.time()

    while True:
        allow_sounds_to_be_played = frames_passed_since_game_started % (FPS // 5 if FPS > 5 else 1)
        for event in pg.event.get():
            # Выйти из игры по нажатию крестика окна или клавиши 'Esc'
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()  # закрыть окно с игрой
                return

            if event.type != pg.KEYDOWN:
                continue

            # Выстрел юноши по нажатию клавиши
            if event.key == pg.K_SPACE and boy.amount_of_shots > 0:
                male_direction = SpriteSheet.Male.direction
                x_shift = ('right' in male_direction) - ('left' in male_direction)
                y_shift = ('down' in male_direction) - ('up' in male_direction)

                shot_radius = boy.shot.radius
                center_x, center_y = boy.center
                shot_x, shot_y = center_x - shot_radius + 5 * x_shift, center_y - shot_radius + 5 * y_shift
                boy.shots.append(boy.shot(coords=(shot_x, shot_y), coords_shift=(x_shift, y_shift)))
                boy.amount_of_shots -= 1
                boy.shot.creation_sound.play()
            
            # Выстрел девушки по нажатию клавиши
            if event.key == pg.K_RETURN and girl.amount_of_shots > 0:
                female_direction = SpriteSheet.Female.direction
                x_shift = ('right' in female_direction) - ('left' in female_direction)
                y_shift = ('down' in female_direction) - ('up' in female_direction)

                shot_radius = girl.shot.radius
                center_x, center_y = girl.center
                shot_x, shot_y = center_x - shot_radius + 5 * x_shift, center_y - shot_radius + 5 * y_shift
                girl.shots.append(girl.shot(coords=(shot_x, shot_y), coords_shift=(x_shift, y_shift)))
                girl.amount_of_shots -= 1
                girl.shot.creation_sound.play()

        key = pg.key.get_pressed()

        # Спавн магической помощи и монстров
        Field.add_magic_help_if_time_has_come()
        Monster.add_monster_if_time_has_come(person1=boy, person2=girl)

        SCREEN.blit(Chunk.background, (0, 0))

        # Отрисовка крови кровавой Мэри
        for monster in Monster.monsters:
            if type(monster) is BloodyMary:
                pg.draw.circle(SCREEN, color=(220, 20, 60), center=monster.center, radius=monster.blood_radius)

        # Отрисовка всех недвижимых объектов кроме кустов и магической помощи (кусты рисоваться будут поверх всего)
        SCREEN.blit(Chunk.other_static_field_objects, (0, 0))

        # Создание и отрисовка количества часов в игре
        game_hours_after_the_game_started = frames_passed_since_game_started / (FPS * (20 + level_index * 10))
        game_hours = int((game_hours_after_the_game_started - 3) % 12)

        if game_hours_after_the_game_started > 9.1:
            return Game.show_result(result_text='Вы выжили!')
        if game_hours == 0:
            game_hours = 12
        if frames_passed_since_game_started % (FPS * (20 + level_index * 10)) == 0:
            color_brightness = 21 * (int(game_hours) if game_hours in range(1, 7) else 12 - int(game_hours))  # яркость поля имитирующая время суток (от вечера до утра)
            writing_hour_format = f'{game_hours} часов ' if int(game_hours) in (9, 10, 11, 12, 5, 6) else 'час ' if game_hours == 1 else f'{game_hours} часа '
            game_hours_text = f'{writing_hour_format}{('вечера' if 9 <= game_hours <= 11 else 'ночи' if game_hours == 12 or game_hours <= 4  else 'утра')}'  # текст времени для часов
            Chunk.change_field_color_and_time(color=(color_brightness,) * 3, text_hours=game_hours_text)

        # Отрисовка количества патронов
        boy_shots_amount_label = GameFont.render(size=20, text=f"{boy.amount_of_shots} патронов", foreground='green', is_smoothy=True, background=DARK_GRAY)
        girl_shots_amount_label = GameFont.render(size=20, text=f"{girl.amount_of_shots} патронов", foreground='red', is_smoothy=True, background=DARK_GRAY)

        SCREEN.blit(boy_shots_amount_label, (510, 5))
        SCREEN.blit(girl_shots_amount_label, (510, 25))

        # Изменение номера кадра анимации на следующий номер кадра
        if frames_passed_since_game_started % (FPS // 4 if FPS > 4 else 1) == 0:
            SpriteSheet.Female.frame_number = (SpriteSheet.Female.frame_number + 1) % 4
            SpriteSheet.Male.frame_number = (SpriteSheet.Male.frame_number + 1) % 4

        # Определение в какую сторону идти девушке (к каким координатам), основываясь на нажатых клавишах для движения
        girl.up, girl.down, girl.left, girl.right = key[pg.K_UP], key[pg.K_DOWN], key[pg.K_LEFT], key[pg.K_RIGHT]
        center_x, center_y = girl.center
        x_aim, y_aim = center_x + (girl.right - girl.left) * 10_000, center_y + (girl.down - girl.up) * 10_000
        girl.move(aim_coords=(x_aim, y_aim))

        # Определение в какую сторону идти юноше (к каким координатам), основываясь на нажатых клавишах для движения
        boy.up, boy.down, boy.left, boy.right = key[pg.K_w], key[pg.K_s], key[pg.K_a], key[pg.K_d]
        center_x, center_y = boy.center
        x_aim, y_aim = center_x + (boy.right - boy.left) * 10_000, center_y + (boy.down - boy.up) * 10_000
        boy.move(aim_coords=(x_aim, y_aim))

        # Установка анимации направления движения длля людей
        female_image = SpriteSheet.change_direction(is_male=False, up=girl.up, down=girl.down, left=girl.left, right=girl.right)
        male_image = SpriteSheet.change_direction(is_male=True, up=boy.up, down=boy.down, left=boy.left, right=boy.right)

        Monster.move_every_monster_on_the_field(person1=boy, person2=girl, allow_sound=allow_sounds_to_be_played)  # Перемещение каждого монстра на игровом поле

        # Разрушение определённых пуль при столкновение и перемещение всех пуль
        _boy = girl.manage_all_shot_events(shot_type=girl.shot, other_person=boy)
        _girl = boy.manage_all_shot_events(shot_type=boy.shot, other_person=girl)
        if _boy is not None and _girl is not None:
            _boy, _girl = Octopus.manage_all_shot_events(shot_type=Octopus.shot, people=(_boy, _girl))

        # Остановка игры, если у юноши или девушки закончилось здоровье (жизни)
        if _boy is None or _girl is None:
            death_index = (_boy is None) + (_girl is None) * 2 - 1
            return Game.show_result(('Юноша', 'Девушка', 'Оба')[death_index] + f' умер{('', 'ла', 'ли')[death_index]}!')

        # Отрисовка всех пуль на поле
        [SCREEN.blit(shot.image, shot.coords) for shot in boy.shots]
        [SCREEN.blit(shot.image, shot.coords) for shot in girl.shots]
        [SCREEN.blit(shot.image, shot.coords) for shot in Octopus.shots]

        # Остановка игры, если у юноши или девушки закончилось здоровье (жизни)
        if boy.health <= 0 or girl.health <= 0:
            death_index = (not boy.health) + (not girl.health) * 2 - 1
            return Game.show_result(('Юноша', 'Девушка', 'Оба')[death_index] + f' умер{('', 'ла', 'ли')[death_index]}!')

        # Обработка любых событий связанных с магической помощью: сбор или исчезновение по причине слишком долгого лежания на поле
        Field.magic_helps = Field.remove_magic_if_there_is_a_reason(person=boy)
        Field.magic_helps = Field.remove_magic_if_there_is_a_reason(person=girl)

        # Отображение шкалы здороья людей, предварительно округлив количество здоровья в большую сторону
        pg.draw.rect(SCREEN, color='Green', rect=(100, 10, 2 * ceil(boy.health), 15))
        pg.draw.rect(SCREEN, color='Red', rect=(100, 30, 2 * ceil(girl.health), 15))

        # Отображение всех монстров, людей, магической помощи, кустов
        SCREEN.blit(male_image, boy.coords)
        SCREEN.blit(female_image, girl.coords)

        [SCREEN.blit(monster.image, monster.coords) for monster in Monster.monsters]
        [SCREEN.blit(magic_help.image, magic_help.coords) for magic_help in Field.magic_helps]

        SCREEN.blit(Chunk.bushes, (0, 0))

        frames_passed_since_game_started += 1

        pg.display.update()

        CYCLES_PER_SECOND.tick(FPS)


def game_help():  # Функция, которая научит играть в игру
    # Начальная музыка обучающего уровня
    # pg.mixer.music.load(f'{MAIN_FOLDER_PATH}/peaceful_learn_music.mp3')
    # pg.mixer.music.play(-1)

    frames_passed_since_game_started = 0

    # Создание людей и направления их движения
    human_health = 100
    boy = Boy(health=human_health, coords=(55 + 25, 55 + 25))
    girl = Girl(health=human_health, coords=(50 * (COLUMNS + 1) - 45 - 25, 50 * (ROWS + 1) - 45 - 25))
    boy.amount_of_shots = girl.amount_of_shots = 200

    boy.down = girl.up = 1
    SpriteSheet.Male.set_class_attributes()
    SpriteSheet.Female.set_class_attributes()

    # Создание всех стен на поле
    objects_spawn_numbers = ('0-11', '12-61', '62-76', '77-99')  # Числа случайной генерации для созданния льда, стекла, куста, кирпичной стены
    object_types = (Ice, Glass, Bush, Brick)

    for spawn_numbers, field_object in zip(objects_spawn_numbers, object_types):
        field_object.set_class_attributes(spawn_numbers=spawn_numbers)

    Field.place_all_not_moving_objects()

    # Установка параметров каждого вида монстра
    for monster_class in (Ghost, Spider, Death, BloodyMary, Octopus):
        monster_class.set_class_attributes()

    # Установка времени между появленниями монстров
    Monster.set_time_range_between_appearances(min_time_in_deciseconds=0)
    MagicHelp.set_time_range_between_appearances(min_time_in_deciseconds=0)

    # Установка вероятности появления магической помощи
    ShotsRestorer.set_class_attributes()
    SpeedIncreaser.set_class_attributes()
    Healer.set_class_attributes()

    # Начало анимации для юноши и девушки
    SpriteSheet.Male.set_class_attributes()
    SpriteSheet.Female.set_class_attributes()

    # В начале обучающего уровня монстров быть не должно
    Monster.monsters = []
    Octopus.shots = []

    # Время последнего спавна монстра и появления магической помощи пусть отмеряется от времени начала обучающего уровня
    Monster.time_of_last_spawn = MagicHelp.time_of_last_spawn = time.time()

    # Обучающий текст
    lessons = ('Зажми "w" на клавиатуре, чтобы юноша стал двигаться вверх',
               'Зажми "s" на клавиатуре, чтобы юноша стал двигаться вниз',
               'Зажми "a" на клавиатуре, чтобы юноша стал двигаться влево',
               'Зажми "d" на клавиатуре, чтобы юноша стал двигаться вправо',
               'Зажми "up" на клавиатуре, чтобы девушка стала двигаться вверх',
               'Зажми "down" на клавиатуре, чтобы девушка стала двигаться вниз',
               'Зажми "left" на клавиатуре, чтобы девушка стала двигаться влево',
               'Зажми "right" на клавиатуре, чтобы девушка стала двигаться вправо',
               'Нажми клавишу "Пробел", чтобы юноша выстрелил',
               'Нажми клавишу "Enter", чтобы девушка выстрелила',
               'Посмотрите на количество патронов наверху экрана. Вот сколько вы можете стрелять',
               'Посмотри на шкалу здоровья вверху экрана. Не допусти, чтобы хотя бы одна из них стала серой!',
               'Сейчас мы изучим карту',
               'Это кирпичные стены, ничто не может пройти через них, кроме привидений',
               'Это кусты, они спрячут всё что находится там от ваших глаз, но от монстров не спрячут',
               'А сейчас выстрели в стекло, чтобы увидеть, как твоя пуля может проходить сквозь стекло',
               'А теперь прогуляйся по льду и ты увидишь, что ты быстрее бегаешь по льду',
               'Сейчас мы будет собирать магическую помощь',
               'Магическая помощь исчезнет, если будет лежать на поле слишком долго!',
               'Собери "ускоритель", чтобы удвоить свою скорость на 15 секунд',
               'Теперь ты бежишь в два раза быстрее!',
               'Собери "восстановитель" чтобы восстановить своё здоровье на четверть индикатора',
               'Взгляни на индикатор здоровья, теперь у тебя больше здоровья от сбора "восстановителя"!',
               'Собери "боеприпасник" чтобы получить 20 магических патронов',
               'Взгляни на количество выстрелов, теперь у тебя больше магических патронов!',
               'Сейчас мы научимся побеждать монстров и не умирать сами',
               'Выстрели в привидение 3 раза, чтобы убить его. Привидение может двигаться сквозь стены!',
               'Выстрели в паука 5 раз, чтобы убить его. Да, паук очень крепкий',
               'Выстрели в смерть, чтобы убить её. Смерть двигается и убивает очень быстро!',
               'Выстрели в кровавую Мэри, чтобы убить её. Боже упаси, не трогай кровь Мэри!',
               'Выстрели в осьминога 3 раза, чтобы убить его. Осьминог может стрелять в тебя тоже!',
               'Чтобы узнать, сколько времени, посмотри на часы сверху',
               'Юноша и девушка должны играть в команде, если хотя бы один из вас погибает, проигрываете оба',
               'Вы выживете, если ни один из вас не погибнет раньше 6,1 часов утра')

    lesson_index = 30  # Глава урока
    the_time_label_started_to_show_itself = time.time()
    watch_learning_label_duration = 9  # Длительность урока

    monster_launched = False

    who_touched_magic_help = None

    game_hours_label = GameFont.render(size=35, text='12 часов ночи', foreground='white', is_smoothy=True)

    while True:
        allow_sounds_to_be_played = frames_passed_since_game_started % (FPS // 5 if FPS > 5 else 1)
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()  # закрыть окно с игрой
                return

            if event.type != pg.KEYDOWN:
                continue

            if event.key == pg.K_SPACE and boy.amount_of_shots > 0:  # Выстрел юноши, если нажата клавиша пробела и есть патроны
                if lesson_index == 8:
                    # Юноша учится стрелять
                    lesson_index += 1
                male_direction = SpriteSheet.Male.direction
                x_shift = ('right' in male_direction) - ('left' in male_direction)
                y_shift = ('down' in male_direction) - ('up' in male_direction)

                shot_radius = boy.shot.radius
                center_x, center_y = boy.center
                shot_x, shot_y = center_x - shot_radius + 5 * x_shift, center_y - shot_radius + 5 * y_shift
                boy.shots.append(boy.shot(coords=(shot_x, shot_y), coords_shift=(x_shift, y_shift)))
                boy.amount_of_shots -= 1
                boy.shot.creation_sound.play()

            if event.key == pg.K_RETURN and girl.amount_of_shots > 0:  # Выстрел девушки, если нажата клавиша Enter и есть патроны
                if lesson_index == 9:
                    # Девушка учится стрелять
                    lesson_index += 1
                    the_time_label_started_to_show_itself = time.time()
                female_direction = SpriteSheet.Female.direction
                x_shift = ('right' in female_direction) - ('left' in female_direction)
                y_shift = ('down' in female_direction) - ('up' in female_direction)

                shot_radius = girl.shot.radius
                center_x, center_y = girl.center
                shot_x, shot_y = center_x - shot_radius + 5 * x_shift, center_y - shot_radius + 5 * y_shift
                girl.shots.append(girl.shot(coords=(shot_x, shot_y), coords_shift=(x_shift, y_shift)))
                girl.amount_of_shots -= 1
                girl.shot.creation_sound.play()

        key = pg.key.get_pressed()

        # Направление движения людей по нажатию клавиш
        girl.up, girl.down, girl.left, girl.right = key[pg.K_UP], key[pg.K_DOWN], key[pg.K_LEFT], key[pg.K_RIGHT]
        center_x, center_y = girl.center
        x_aim, y_aim = center_x + (girl.right - girl.left) * 10_000, center_y + (girl.down - girl.up) * 10_000
        girl.move(aim_coords=(x_aim, y_aim))

        boy.up, boy.down, boy.left, boy.right = key[pg.K_w], key[pg.K_s], key[pg.K_a], key[pg.K_d]
        center_x, center_y = boy.center
        x_aim, y_aim = center_x + (boy.right - boy.left) * 10_000, center_y + (boy.down - boy.up) * 10_000
        boy.move(aim_coords=(x_aim, y_aim))

        SCREEN.blit(Chunk.background, (0, 0))

        # Обучение как играть в игру
        lesson_index_before = lesson_index
        if lesson_index in range(8):
            # Учимся двигаться
            if key[(pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT)[lesson_index]]:
                lesson_index += 1

        elif lesson_index in (10, 11, 12, 13, 14, 17, 18, 20, 22, 24, 25, 31, 32, 33):
            # Просто читаем информацию внизу экрана и таким образом учимся
            if time.time() - the_time_label_started_to_show_itself > watch_learning_label_duration:
                lesson_index += 1

        elif lesson_index == 15:
            # Узнаём, что выстрел может проходить сквозь стекло, стрельнув в стекло
            distance = 50 // 2
            for shot in boy.shots:
                shot_center_x, shot_center_y = shot.center
                if [None for center_x, center_y in Field.glass_blocks_centers
                        if abs(center_x - shot_center_x) < distance and abs(center_y - shot_center_y) < distance]:
                    lesson_index += 1
                    break

            if lesson_index == 15:
                for shot in girl.shots:
                    shot_center_x, shot_center_y = shot.center
                    if [None for center_x, center_y in Field.glass_blocks_centers
                            if abs(center_x - shot_center_x) < distance and abs(center_y - shot_center_y) < distance]:
                        lesson_index += 1
                        break

        elif lesson_index == 16:
            # Узнаём, что можем быстро двигаться по льду, походив по нему
            distance = 50 // 2
            girl_center_x, girl_center_y = girl.center
            boy_center_x, boy_center_y = boy.center
            girl_on_ice = [None for center_x, center_y in Field.ice_blocks_centers
                           if abs(center_x - girl_center_x) < distance and abs(center_y - girl_center_y) < distance]
            boy_on_ice = [None for center_x, center_y in Field.ice_blocks_centers
                          if abs(center_x - boy_center_x) < distance and abs(center_y - boy_center_y) < distance]
            girl_is_walking = any((girl.up, girl.down, girl.left, girl.right))
            boy_is_walking = any((boy.up, boy.down, boy.left, boy.right))
            if any((girl_on_ice and girl_is_walking, boy_on_ice and boy_is_walking)):
                lesson_index += 1

        elif lesson_index in range(19, 25, 2):
            # Учимся распознавать и собирать магическую помощь
            if not Field.magic_helps:
                Field.add_magic_help_if_time_has_come(magic_help_type=(SpeedIncreaser, Healer, ShotsRestorer)[(lesson_index - 19) // 2])
            elif any((boy.image_rect.colliderect(Field.magic_helps[0].image_rect),
                      girl.image_rect.colliderect(Field.magic_helps[0].image_rect))):
                who_touched_magic_help = boy if boy.image_rect.colliderect(Field.magic_helps[0].image_rect) else girl
                lesson_index += 1

        elif lesson_index in range(26, 31):
            # Учимся распознавать и стрелять в монстров
            if not Monster.monsters and time.time() - the_time_label_started_to_show_itself > 5:
                if not monster_launched:
                    Monster.add_monster_if_time_has_come(
                        person1=boy, person2=girl,
                        monster_type=(Ghost, Spider, Death, BloodyMary, Octopus)[lesson_index - 26])
                else:
                    lesson_index += 1
                monster_launched = not monster_launched

        # Обучение окончено!
        if lesson_index == len(lessons):
            return Game.show_result(result_text='Вы выжили!')

        if lesson_index_before != lesson_index:
            the_time_label_started_to_show_itself = time.time()

        SCREEN.blit(game_hours_label, (670, 5))

        # Отрисовка крови Мэри
        for monster in Monster.monsters:
            if type(monster) is BloodyMary:
                pg.draw.circle(SCREEN, color=(220, 20, 60), center=monster.center, radius=monster.blood_radius)

        # Отображения текста внизу экрана, который поможет научиться играть
        instruction_font = GameFont.render(size=30, foreground='black', background='white', text=lessons[lesson_index])
        SCREEN.blit(instruction_font, (5, HEIGHT - 40))

        # Рисование каждого недвигающегося объекта, заисключением кустов и магическоих помощей
        SCREEN.blit(Chunk.other_static_field_objects, (0, 0))

        # Отображение количества патронов
        boy_shots_amount_label = GameFont.render(size=20, text=f"{boy.amount_of_shots} патронов", foreground='green', is_smoothy=True, background=DARK_GRAY)
        girl_shots_amount_label = GameFont.render(size=20, text=f"{girl.amount_of_shots} патронов", foreground='red', is_smoothy=True, background=DARK_GRAY)
        SCREEN.blit(boy_shots_amount_label, (510, 5))
        SCREEN.blit(girl_shots_amount_label, (510, 25))

        # Изменение номера кадра анимации на следующий номер кадра
        if frames_passed_since_game_started % (FPS // 4 if FPS > 4 else 1) == 0:
            SpriteSheet.Female.frame_number = (SpriteSheet.Female.frame_number + 1) % 4
            SpriteSheet.Male.frame_number = (SpriteSheet.Male.frame_number + 1) % 4

        # Установка направления движения для анимирования людей
        female_image = SpriteSheet.change_direction(is_male=False, up=girl.up, down=girl.down, left=girl.left, right=girl.right)
        male_image = SpriteSheet.change_direction(is_male=True, up=boy.up, down=boy.down, left=boy.left, right=boy.right)

        # Перемещение каждого монстра на игровом поле
        Monster.move_every_monster_on_the_field(person1=boy, person2=girl, allow_sound=allow_sounds_to_be_played)

        # Исчезновение пуль при столкновении и передвижение всех пуль
        _boy = girl.manage_all_shot_events(shot_type=girl.shot, other_person=boy)
        _girl = boy.manage_all_shot_events(shot_type=boy.shot, other_person=girl)
        if _boy is not None and _girl is not None:
            _boy, _girl = Octopus.manage_all_shot_events(shot_type=Octopus.shot, people=(_boy, _girl))

        # Игра заканчивается если здоровья нет у юноши, либо девушки
        if _boy is None or _girl is None:
            death_index = (_boy is None) + (_girl is None) * 2 - 1
            return Game.show_result(('Юноша', 'Девушка', 'Оба')[death_index] + f' умер{('', 'ла', 'ли')[death_index]}!')

        # Отрисовка всех выстрелов
        [SCREEN.blit(shot.image, shot.coords) for shot in boy.shots]
        [SCREEN.blit(shot.image, shot.coords) for shot in girl.shots]
        [SCREEN.blit(shot.image, shot.coords) for shot in Octopus.shots]

        # Игра заканчивается если здоровья нет у юноши, либо девушки
        if boy.health <= 0 or girl.health <= 0:
            death_index = (not boy.health) + (not girl.health) * 2 - 1
            return Game.show_result(('Юноша', 'Девушка', 'Оба')[death_index] + f' умер{('', 'ла', 'ли')[death_index]}!')

        # Исчезновение магической помощи если её собрали или она лежала слишком долго
        Field.magic_helps = Field.remove_magic_if_there_is_a_reason(person=boy)
        Field.magic_helps = Field.remove_magic_if_there_is_a_reason(person=girl)

        # Рисование шкалы здоровья на экране округляя здоровье до целого число в большую сторону
        pg.draw.rect(SCREEN, color='Green', rect=(100, 10, 2 * ceil(boy.health), 15))
        pg.draw.rect(SCREEN, color='Red', rect=(100, 30, 2 * ceil(girl.health), 15))

        # Отрисовка всех монстров людей магической помощи и кустов
        SCREEN.blit(male_image, boy.coords)
        SCREEN.blit(female_image, girl.coords)

        [SCREEN.blit(monster.image, monster.coords) for monster in Monster.monsters]
        [SCREEN.blit(magic_help.image, magic_help.coords) for magic_help in Field.magic_helps]

        SCREEN.blit(Chunk.bushes, (0, 0))

        # Рисование графических подсказок при обучении
        if lesson_index in range(8):
            x, y = (boy.center, girl.center)[lesson_index > 3]
            color = ('green', BLOODY_RED)[lesson_index > 3]

            # Наричовать стрелки для указания, куда идти
            if lesson_index % 4 == 0:
                pg.draw.rect(SCREEN, rect=(x - 5, y - 40, 10, 20), color=color)
                pg.draw.polygon(SCREEN, points=((x - 10, y - 40), (x + 10, y - 40), (x, y - 60)), color=color)
            elif lesson_index % 4 == 1:
                pg.draw.rect(SCREEN, rect=(x - 5, y + 20, 10, 20), color=color)
                pg.draw.polygon(SCREEN, points=((x - 10, y + 40), (x + 10, y + 40), (x, y + 60)), color=color)
            elif lesson_index % 4 == 2:
                pg.draw.rect(SCREEN, rect=(x - 30, y - 5, 20, 10), color=color)
                pg.draw.polygon(SCREEN, points=((x - 30, y - 10), (x - 30, y + 10), (x - 50, y)), color=color)
            else:
                pg.draw.rect(SCREEN, rect=(x + 10, y - 5, 20, 10), color=color)
                pg.draw.polygon(SCREEN, points=((x + 30, y - 10), (x + 30, y + 10), (x + 50, y)), color=color)

            key_image = (KeyBoardImage.wasd, KeyBoardImage.arrows)[lesson_index > 3]
            x_shift = (1, -1)[lesson_index > 3]
            image_rect = key_image.get_rect(center=(x + 100 * x_shift, y))
            SCREEN.blit(key_image, image_rect)
            x_image_shift = (1, 1, 0, 2)[lesson_index % 4]
            y_image_shift = (1, 0)[lesson_index % 4 == 0]

            # Нарисовать клавиши клавиатуры
            if lesson_index > 3:
                pg.draw.rect(SCREEN, rect=(x - 154 + x_image_shift * 36, y - 37 + y_image_shift * 36, 40, 40),
                             color=color, width=3, border_radius=10)
            else:
                pg.draw.rect(SCREEN, rect=(x + 45 + x_image_shift * 36, y - 37 + y_image_shift * 36, 40, 40),
                             color=color, width=3, border_radius=10)

        elif lesson_index in range(8, 10):
            # Нарисовать клавиши для выстрела
            key_image = KeyBoardImage.space if lesson_index == 8 else KeyBoardImage.enter
            x_shift = (-1, 1)[lesson_index == 8]
            x, y = (girl.center, boy.center)[lesson_index == 8]
            color = (BLOODY_RED, 'green')[lesson_index == 8]
            image_rect = key_image.get_rect(center=(x + 100 * x_shift, y))
            SCREEN.blit(key_image, image_rect)
            pg.draw.rect(SCREEN, rect=(image_rect[0] - 3, image_rect[1] - 3, image_rect[2] + 6, image_rect[3] + 6),
                         color=color, width=3, border_radius=10)

        elif lesson_index in range(10, 12):
            # Нарисовать стрелку показыающую на количество выстрелов или шкалу здоровья
            x_shift = 0 if lesson_index == 10 else -300
            pg.draw.rect(SCREEN, rect=(530 + x_shift, 135, 60, 120), color='yellow')
            pg.draw.polygon(SCREEN, points=((560 + x_shift, 55), (500 + x_shift, 135), (620 + x_shift, 135)), color='yellow')

        elif lesson_index in range(13, 17):
            # Подсветить стёкла или ледяные поля
            centers_of_the_blocks_to_highlight = (Field.bricks_centers,
                                                  Field.bushes_centers,
                                                  Field.glass_blocks_centers,
                                                  Field.ice_blocks_centers)[lesson_index - 13]
            coords_to_draw_rects = [(x - 27, y - 27) for x, y in centers_of_the_blocks_to_highlight]
            for x, y in coords_to_draw_rects:
                pg.draw.rect(SCREEN, rect=(x, y, 54, 54), color='yellow', width=2, border_radius=10)

        elif lesson_index in range(19, 25, 2) and Field.magic_helps:
            # Нарисовать круг, показывающий, где магическая помощь
            pg.draw.circle(SCREEN, color='green', center=Field.magic_helps[0].center, radius=50, width=5)

        if lesson_index in range(20, 26, 2):
            # Демонстрация эффектов магической помощи
            x, y = who_touched_magic_help.center
            if lesson_index == 20:
                SCREEN.blit(GameFont.render(size=40, text='x2',
                                            foreground=(BLOODY_RED, DARK_GREEN)[who_touched_magic_help is boy],
                                            is_smoothy=True, background='yellow'), (x - 50, y - 20))
            elif lesson_index == 22:
                y_coord = (28, 8)[who_touched_magic_help is boy]
                x_coord = (98 - 100 + 2 * (girl, boy)[who_touched_magic_help is boy].health)
                pg.draw.rect(SCREEN, rect=(x_coord, y_coord, 104, 19), color='yellow', width=2, border_radius=5)
            else:
                y_coord = (25, 5)[who_touched_magic_help is boy]
                SCREEN.blit(GameFont.render(size=20, text='(+20)', foreground='yellow', is_smoothy=True), (616, y_coord))
                

        elif lesson_index in range(26, 31) and Monster.monsters:
            # Рисование кругов вокруг монстров и подпись около них, сколько выстрелов нужно, чтобы убить их
            monster = Monster.monsters[0]
            x, y = monster.center
            shots_left_to_kill = monster.health // HUMAN_SHOT_DAMAGE
            total_shots_to_kill = monster.spawn_with_health // HUMAN_SHOT_DAMAGE
            SCREEN.blit(GameFont.render(size=30,
                                        text=f'{shots_left_to_kill}/{total_shots_to_kill}',
                                        foreground=BLOODY_RED), (x - 20, y - 90))
            pg.draw.circle(SCREEN, color=BLOODY_RED, center=(x, y), radius=50, width=5)

        elif lesson_index == 31:
            # Выделение игрового времени (икс часов утра или ночи) в прямоугольную рамку
            pg.draw.rect(SCREEN, rect=pg.Rect((662, 7, 200, 38)), color='green', width=5, border_radius=10)

        frames_passed_since_game_started += 1

        pg.display.update()

        CYCLES_PER_SECOND.tick(FPS)


img = pg.image.load(f'{MAIN_FOLDER_PATH}/scary_adventure.png').convert_alpha()   # картинка "страшное приключение" в начале игры
sound1 = pg.mixer.Sound('parts_of_shooter_game\Shot\creation_sound\ElectricSphere.mp3')  # звук выстрела осьминога
sound2 = pg.mixer.Sound('parts_of_shooter_game\Shot\destruction_sound\ElectricSphere.mp3')  # звук разрушения пули осьминога


def animate():
    fps = 0
    
    while fps <= FPS * 4:
        
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()  # закрыть окно с игрой
                return
        
        SCREEN.fill((0, 0, 0))
        fps += 1
        img.set_alpha(min(fps, FPS * 4 - fps))  # изменение прозрачности изображения
        SCREEN.blit(img, (135, 380))
        pg.display.update()
        CYCLES_PER_SECOND.tick(FPS)
        
        if fps == FPS:
            Octopus.shot.creation_sound.play()  # звук выстрела осьминога
        if fps == 7 * FPS // 2:
            Octopus.shot.destruction_sound.play()  # звук разрушения пули осьминога
    game_intro()

animate()