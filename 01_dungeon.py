# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет только две локации и не будет мобов
# (то есть в коренном json-объекте содержится список, содержащий только два json-объекта и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...
import json
import re
from decimal import *
import logging

remaining_time = '1234567890.0987654321'
# если изначально не писать число в виде строки - теряется точность!
field_names = ['current_location', 'current_experience', 'current_date']


class Gamer:
    def __init__(self):
        self.regular_location = "Location_[1-9B][1-2_][_t][tm][m0-9][0-9.]{,20}"  # ищем сочетания слов, определяющие, что мы в локации
        self.file = "rpg.json"
        with open(self.file, "r") as file:
            self.map = json.load(file)
        self.remaining_time = Decimal(remaining_time)
        self.current_experience = 0
        self.current_hour = 0
        self.current_minute = 0
        self.current_second = 0
        self.current_day = 0
        self.possible_ways = []
        self.possible_ways_keys = []
        self.error = False
        self.enemies = []
        self.fight = False
        self.win = False

    def find_possible_ways(self):
        if not self.fight:
            for key, value in self.map.items():
                self.map = value
                self.current_location = key
        if type(self.map) == dict:
            for key, value in self.map.items():
                self.possible_ways.append(value)
                self.possible_ways_keys.append(key)
        elif type(self.map) == list:
            for elem in self.map:
                if type(elem) == dict:
                    self.possible_ways.append(elem)
                    for key, value in elem.items():
                        self.possible_ways_keys.append(key)
                if not self.fight and type(elem) == str or not self.fight and type(elem) == list:
                    self.enemy = re.findall("[MmBb][o][bSs][_s][a-z0-9_]{,14}", str(elem))
                    self.enemies.append(self.enemy)

    def find_next_location(self):
        self.next_location = re.search(self.regular_location, str(self.possible_ways))
        self.next_location = self.next_location.group()

    def choosing(self):
        if len(self.possible_ways) > 1:
            print("Выберите номер локации из списка:")
            for number, way in enumerate(self.possible_ways_keys):
                print(f"{number+1}. {str(way)}")
            user_step = input(f"Ваш выбор: ")
            if user_step == "1" and len(self.possible_ways_keys) > 0:
                self.possible_ways = [self.possible_ways[0]]
                self.map = self.possible_ways[0]
                self.possible_ways_keys = [self.possible_ways_keys[0]]
            elif user_step == "2" and len(self.possible_ways_keys) > 1:
                self.possible_ways = [self.possible_ways[1]]
                self.map = self.possible_ways[0]
                self.possible_ways_keys = [self.possible_ways_keys[1]]
            elif user_step == "3" and len(self.possible_ways_keys) > 2:
                self.possible_ways = [self.possible_ways[2]]
                self.map = self.possible_ways[0]
                self.possible_ways_keys = [self.possible_ways_keys[2]]
            else:
                print("Неправильно введен символ. Попробуйте еще раз.")
                self.choosing()
        else:
            self.possible_ways = [self.possible_ways[0]]
            self.map = self.possible_ways[0]
            self.possible_ways_keys = [self.possible_ways_keys[0]]

    def action_after_choosing(self, user_step):
        if user_step == "1" and self.enemies:
            self.fighting()
            self.enemies.clear()
            self.possible_ways.clear()
            self.possible_ways_keys.clear()
            return True
        elif user_step == "2" and self.possible_ways:
            self.choosing()
            if "Hatch_tm159.098765432" in self.possible_ways_keys and self.current_experience >= 280:
                print("Поздравляем, вы выиграли!")
                self.win = True
                return False
            elif "Hatch_tm159.098765432" in self.possible_ways_keys and self.current_experience < 280:
                print("Недостаточно очков. Попробуйте еще раз")
                return False
            else:
                self.find_next_location()
                self.go_to_next_location()
                self.possible_ways.clear()
                self.possible_ways_keys.clear()
                self.enemies.clear()
                return True
        elif user_step == "3":
            print("Спасибо за игру! Попробуйте снова.")
            return False
        else:
            print("Неправильно введен символ. Попробуйте еще раз.")
            self.error = True
            return True

    def play(self):
        while True:
            if not self.error:
                self.find_possible_ways()
            self.fight = False
            self.error = False
            if not self.possible_ways and not self.enemies or self.remaining_time < 0:
                print("Вы проиграли! Попробуйте снова")
                break
            elif self.enemies and self.possible_ways:
                print(f"Вы находитесь в {self.current_location}. У вас {self.current_experience} единиц опыта "
                      f"и осталось {self.remaining_time} секунд до наводнения. "
                      f"Прошло времени: {self.current_day} дней, {self.current_hour} часов,"
                      f"{self.current_minute} минут и {self.current_second} секунд. Внутри вы видите:")
                for enemy in self.enemies:
                    print("Монстра", enemy[0])
                for way in self.possible_ways_keys:
                    print("Переход в локацию", way)
                user_step = input(f"Выберите действие: "
                                  f"1 - атаковать, 2 - перейти в другую локацию, 3 - выйти из игры. Ваш выбор: ")
                result = self.action_after_choosing(user_step)
            elif self.possible_ways and not self.enemies:
                print(f"Вы находитесь в {self.current_location}. У вас {self.current_experience} единиц опыта "
                      f"и осталось {self.remaining_time} секунд до наводнения. "
                      f"Прошло времени: {self.current_day} дней, {self.current_hour} часов,"
                      f"{self.current_minute} минут и {self.current_second} секунд. Внутри вы видите:")
                for way in self.possible_ways_keys:
                    print("Переход в локацию", way)
                user_step = input(f"Выберите действие: 2 - перейти в другую локацию, 3 - выйти из игры. Ваш выбор: ")
                result = self.action_after_choosing(user_step)
            elif self.enemies and not self.possible_ways:
                print(f"Вы находитесь в {self.current_location}. У вас {self.current_experience} единиц опыта "
                      f"и осталось {self.remaining_time} секунд до наводнения. "
                      f"Прошло времени: {self.current_day} дней, {self.current_hour} часов, "
                      f"{self.current_minute} минут и {self.current_second} секунд. Внутри вы видите:")
                for enemy in self.enemies:
                    print("Монстра", enemy[0])
                user_step = input(f"Выберите действие: "
                                  f"1 - атаковать, 3 - выйти из игры. Ваш выбор: ")
                result = self.action_after_choosing(user_step)
            if not result and not self.win:
                return False
            elif not result and self.win:
                return True

    def go_to_next_location(self):
        if "." in self.next_location:
            regular_time = "[t][m][0-9.]{,4}"
        else:
            regular_time = "[t][m][0-9.]{,3}"
        self.time_to_reduce = re.findall(regular_time, self.next_location)
        self.time_to_reduce = Decimal(self.time_to_reduce[0][2:6])
        self.remaining_time -= self.time_to_reduce
        self.find_spending_time()
        self.current_location = self.next_location
        logging.info(f"Текущее положение - {self.next_location}. Осталось времени - {self.remaining_time}. "
                     f"Текущий опыт - {self.current_experience}.")

    def find_spending_time(self):
        sec = int(self.time_to_reduce)
        h = sec // 3600
        m = (sec - h * 3600) // 60
        s = sec % 60
        self.current_hour += h
        self.current_minute += m
        self.current_second += s
        if self.current_second >= 60:
            self.current_minute += self.current_second // 60
            self.current_second = self.current_second % 60
            if self.current_minute >= 60:
                self.current_hour += self.current_minute // 60
                self.current_minute = self.current_minute % 60
                if self.current_hour >= 24:
                    self.current_day += self.current_hour // 24
                    self.current_hour = self.current_hour % 60
        logging.info(f"Затрачено дней: {self.current_day}, часов: {self.current_hour}, минут: {self.current_minute} и "
                     f"секунд: {self.current_second}")

    def fighting(self):
        for one_enemy in self.enemies:
            enemy = re.search("[e][x][p][0-9]{,14}", str(one_enemy))
            self.time_to_reduce = re.search("[t][m][0-9]{,14}", str(one_enemy))
            enemy = enemy.group()
            enemy = enemy[3:]
            self.time_to_reduce = self.time_to_reduce.group()
            self.time_to_reduce = int(self.time_to_reduce[2:])
            self.current_experience += int(enemy)
            self.remaining_time -= self.time_to_reduce
            self.find_spending_time()
            logging.info(f"Текущее положение - {self.current_location}. Осталось времени - {self.remaining_time}. "
                         f"Текущий опыт - {self.current_experience}")
        self.fight = True

    def logging(self):
        logging.basicConfig(
            level=logging.INFO,
            handlers=[logging.FileHandler('play_log.csv', 'w', 'utf-8')],
        )


while True:
    gamer = Gamer()
    gamer.logging()
    winner = gamer.play()
    if winner:
        break
