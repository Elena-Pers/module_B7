from random import randint

import os

SIZE = 6    # размер поля


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __init__(self, text):
        self.txt = text


class BoardUsedException(BoardException):
    def __init__(self, text):
        self.txt = text




class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f'({self.x},{self.y})'


class Ship:
    def __init__(self, dot, ln, dot_):
        self.dt = dot
        self.length = ln
        self.direction = dot_
        self.life = ln

    def dots(self):
        if self.direction:
            return [Dot(x, self.dt.y) for x in range(self.dt.x, self.dt.x + self.length)]
        else:
            return [Dot(self.dt.x, y) for y in range(self.dt.y, self.dt.y + self.length)]

class Color:
    yellow = '\033[93m'
    red = '\033[91m'
    blue = '\033[94m'
    green = '\033[92m'
    black = '\033[30m'


    shapes = {
        0: blue + '•' + black,
        1: green + '■' + black,
        2: blue + '•' + black,
        10: red + '•' + black,
        11: yellow + '■' + black,
        21: red + '■' + black
    }


class Board:
    def __init__(self, h, size=SIZE):
        self.ships = []
        self.x_ships = 0
        self.hide = h
        self.size = size
        self.f = [[0] * self.size for _ in range(0, self.size)]

    @staticmethod
    def contour(c_ship):
        set_ = set()

        def add_dot(x1, y1):
            try:
                set_.add(Dot(x1, y1))
            except IndexError:
                pass

        for dot in c_ship.dots():
            add_dot(dot.x + 1, dot.y)
            add_dot(dot.x + 1, dot.y + 1)
            add_dot(dot.x, dot.y + 1)
            add_dot(dot.x - 1, dot.y + 1)
            add_dot(dot.x - 1, dot.y)
            add_dot(dot.x - 1, dot.y - 1)
            add_dot(dot.x, dot.y - 1)
            add_dot(dot.x + 1, dot.y - 1)
        return set_.difference(c_ship.dots())

    @staticmethod
    def out(dot):
        return (dot.x < 0) or (dot.x >= SIZE) or (dot.y < 0) or (dot.y >= SIZE)

    def add_ship(self, add_s):
        try:
            for dot in add_s.dots():
                if self.out(dot):
                    raise BoardOutException('')
                if self.f[dot.x][dot.y] != 0:
                    raise BoardUsedException('')
                for i in self.ships:
                    if dot in self.contour(i):
                        raise BoardUsedException('')
        except (BoardOutException, BoardUsedException):
            return False
        else:
            for dot in add_s.dots():
                self.f[dot.x][dot.y] = 1
            self.ships.append(add_s)
            self.x_ships += 1
            return True

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException(f'{dot.x + 1} {dot.y + 1} - {Color.blue}Вы стреляете за пределы игрового поля')
        if self.f[dot.x][dot.y] >= 10:
            raise BoardUsedException(f'{dot.x + 1} {dot.y + 1} - {Color.blue} Эти координаты уже заняты')

        self.f[dot.x][dot.y] += 10
        if self.f[dot.x][dot.y] == 11:
            for s in self.ships:
                if dot in s.dots():
                    s.life -= 1
                    if not s.life:
                        for dot_ in s.dots():
                            self.f[dot_.x][dot_.y] += 10
                        for dot_ in self.contour(s):
                            if not self.out(dot_):
                                if self.f[dot_.x][dot_.y] < 10:
                                    self.f[dot_.x][dot_.y] += 10
                        self.x_ships -= 1
        return self.f[dot.x][dot.y]

    def random_board(self):
        size_bord = self.size
        count = 0
        for q in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                x = randint(0, size_bord - 1)
                y = randint(0, size_bord - 1)
                dot = randint(0, 1)
                if self.add_ship(Ship(Dot(x, y), q, dot)):
                    break
                else:
                    count += 1
                if count > 2000:
                    return False
        return True


class Player:
    def __init__(self, bd_):
        self.board = bd_
        self.last_shot_dot = []
        self.last_shot_value = 0

    def ask(self):
        x, y = 0, 0
        return Dot(x, y)

    def move(self, other):
        try:
            Game.check = 0
            dot_ = self.ask()
            shot_value = other.board.shot(dot_)
            if shot_value > 10:
                self.last_shot_dot.append(dot_)
                self.last_shot_value = shot_value
                if shot_value > 20:
                    print(f'{dot_.x + 1} {dot_.y + 1} - {Color.red}Убил{Color.red}')
                    self.last_shot_dot.clear()
                    Game.check += 1
                else:
                    print(f'{dot_.x + 1} {dot_.y + 1} - {Color.red}Ранил{Color.red}')
                    Game.check += 1
                if other.board.x_ships:
                    return True
                else:
                    self.board.hide = False
                    return False
            else:
                print(f'{dot_.x + 1} {dot_.y + 1} - {Color.red}Мимо{Color.red}')
                return False
        except (BoardOutException, BoardUsedException) as e:
            if type(self) is User:
                print(e.txt)
            return True


class User(Player):
    def ask(self):
        while True:
            ent_list = input(f"\n Введите координаты: {Color.red}").split()
            if len(ent_list) != 2:
                print(f"{Color.red}Введите две координаты{Color.red}")
                continue
            x, y = ent_list
            if not (x.isdigit()) or not (y.isdigit()):
                print(f"{Color.red}Введите числа!{Color.red}")
                continue
            x = int(ent_list[0]) - 1
            y = int(ent_list[1]) - 1
            return Dot(x, y)


class Comp(Player):
    def ask(self):
        if self.last_shot_value == 11:
            if len(self.last_shot_dot) == 1:
                dot_ = self.last_shot_dot[0]
                t = randint(1, 4)
                if t == 1:
                    return Dot(dot_.x, dot_.y - 1)
                elif t == 2:
                    return Dot(dot_.x + 1, dot_.y)
                elif t == 3:
                    return Dot(dot_.x, dot_.y + 1)
                elif t == 4:
                    return Dot(dot_.x - 1, dot_.y)
            else:
                t = randint(0, 1)
                if self.last_shot_dot[0].x == self.last_shot_dot[1].x:
                    miny = self.last_shot_dot[0].y
                    maxy = miny
                    for dot_ in self.last_shot_dot:
                        if miny > dot_.y:
                            miny = dot_.y
                        if maxy < dot_.y:
                            maxy = dot_.y
                    if t:
                        return Dot(self.last_shot_dot[0].x, miny - 1)
                    else:
                        return Dot(self.last_shot_dot[0].x, maxy + 1)
                else:
                    minx = self.last_shot_dot[0].x
                    maxx = minx
                    for dot_ in self.last_shot_dot:
                        if minx > dot_.x:
                            minx = dot_.x
                        if maxx < dot_.x:
                            maxx = dot_.x
                    if t:
                        return Dot(minx - 1, self.last_shot_dot[0].y)
                    else:
                        return Dot(maxx + 1, self.last_shot_dot[0].y)
        else:
            x = randint(0, 5)
            y = randint(0, 5)
            return Dot(x, y)


class Game(Color):
    check = 0

    def __init__(self, size):
        self.size = size
        bd_us = Board(False, size=self.size)
        bd_comp = Board(True, size=self.size)
        while not bd_us.random_board():
            bd_us = Board(False)
        while not bd_comp.random_board():
            bd_comp = Board(True)
        self.board_us = bd_us
        self.board_comp = bd_comp
        self.us = User(bd_us)
        self.comp = Comp(bd_comp)

    def print_board(self):
        size = self.size

        def get_row(bd):
            if bd.hide:
                return '   '.join(self.shapes[bd.f[i][j] if bd.f[i][j] >= 10 else 2] for j in range(0, size))
            else:
                return '   '.join(self.shapes[bd.f[i][j]] for j in range(0, size))

        print(f'\n{self.black}Поле игрока :{"":27}Поле компьютера:')
        print(f'{self.black}{"_" * 29}{"":10}{"_" * 29}')
        coord_numbers = '│ '.join(f'{str(s + 1):2}' for s in range(0, size))
        print(
            f'│ {self.black} {self.black} │ {coord_numbers}│{"":10}│ {self.black} {self.black} │ {coord_numbers}│')
        print(f'│{"–––│" * 7}{"":10}│{"–––│" * 7}')
        for i in range(0, size):
            print(f'│ {str(i + 1):2}│ {get_row(self.board_us)} │{"":10}│ {str(i + 1):2}│ {get_row(self.board_comp)} │')
        print(f'|___|{"_" * 23}|{"":10}|___|{"_" * 23}|')

    def loop(self, user_move):
        if user_move:
            while True:
                self.print_board()
                if self.us.move(self.comp):
                    continue
                else:
                    self.print_board()
                    break
        else:
            print('\nХод компьютера: ')
            while True:
                if Game.check == 1:
                    self.print_board()
                    print('\nХод компьютера: ')
                if self.comp.move(self.us):
                    continue
                else:
                    break

    def start(self):
        user_move = True
        print(f'{self.blue}{"*" * 100}{self.blue}')
        while True:
            self.loop(user_move)
            user_move = not user_move
            if not self.board_us.x_ships:
                self.print_board()
                print(f'{self.blue}\n Победил компьютер!\n{self.blue}')
                break
            if not self.board_comp.x_ships:
                self.print_board()
                print(f'{self.red}\n ВЫ ПОБЕДИЛИ !!!\n{self.red}')
                break
        return False


class Greet:
    @staticmethod
    def greet():
        print(f'{Game.blue}')
        print(f'{Game.blue}{"*" * 100}\n')
        print(f' {Game.blue} ПРИВЕТСТВУЕМ ВАС В ИГРЕ "Морской бой" \n')
        print(f' {Game.blue} ФОРМАТ ВВОДА X Y ')
        print(f' {Game.blue} X - номер строки')
        print(f' {Game.blue} Y - номер столбца \n')
        print(f'{Game.blue}{"*" * 100}')


clear = lambda: os.system('cls')
clear()
Greet.greet()
while True:
    g = Game(size=SIZE)
    if g.start():
        breakfrom
        random
        import randint
