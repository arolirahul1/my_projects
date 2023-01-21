import random, time, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path # this will get you the path variable
import itertools
class Possibility:
    def __init__(self, id, list_moves):
        self.id = id
        self.list_moves = list_moves
        self.places = sum(list_moves)
        self.can_move = self.can_takeout = self.can_hit_target = self.already_occupied = self.safe = False
        self.rank =0
    def __str__(self):
        return f'can_move:{self.can_move}, can_takeout:{self.can_takeout}, can_hit_target:{self.can_hit_target}, safe:{self.safe}, already_occupied:{self.already_occupied}, rank:{self.rank}'
class Dice:
    def __init__(self, id):
        if id == 5:
            self.vals = [1,2,3,4,8]
            self.len = len(self.vals)
        elif id == 7:
            self.vals = [1,2,3,4,5,6,12]
            self.len = len(self.vals)
    def toss(self):
        index= random.randint(1,self.len)
        return self.vals[index-1]
class Player:
    def get_last(self):
        return self.last_house if self.got_entry else self.level1_last
    def __init__(self, id, path, board, level1_last):
        self.id = id
        self.path  = path
        self.last_house = path [-1]
        self.level1_last = level1_last
        self.board = board
        self.index = [0] * self.board.pieces_count
        self.positions = [path[i] for i in self.index]
        self.got_entry = False
    
    def is_done(self):
        #Is game over?
        if self.positions == [self.last_house]*self.board.pieces_count:
            return True
    def move(self, vals):
        move = self.move_piece(vals)
        if move.can_move:
            self.index[move.id] = self.index[move.id] + move.places
            self.positions[move.id] = self.path[self.index[move.id]]
        print (f"Player {self.id} rolled dice to get {move.places}, moved: {move.can_move},  positions: {self.positions}, takeout: {move.can_takeout}")
        if move.can_takeout:
            self.got_entry = True
            index = self.opponent.positions.index(move.target_pos)
            self.opponent.index[index] = 0
            self.opponent.positions[index] = self.opponent.path[0]
        return move
    def get_combinations(self, l) -> list:
        combinations = []
        for i in range(1, len(l)+1):
            for item in itertools.combinations(l, i):
                combinations.append(list(item))
        return combinations
    def move_piece(self, vals):
        possibilities = []
        combinations = self.get_combinations(vals)
        for combination in combinations:
            for i in range(len(self.index)):
                pos = Possibility(i, combination)
                target =self.index[i] + pos.places
                target_pos = -1
                currently_safe = True if self.path[self.index[i]] in self.board.safe else False
                if target <= self.get_last():
                    pos.can_move = True
                    target_pos = self.path[target]
                if target_pos in self.board.safe:
                    pos.safe = True
                if target == len(self.path)-1:
                    pos.can_hit_target = True
                if not pos.safe and target_pos in self.positions :
                    pos.already_occupied = True
                if not pos.safe and target_pos in self.opponent.positions:
                    pos.can_takeout = True
                pos.rank = (1 if pos.can_move else -200) + (110 if pos.can_takeout and not self.got_entry else 0) + (10 if pos.can_takeout and self.got_entry else 0) + (10 if pos.can_hit_target else 0) + (100 if self.got_entry and not currently_safe and pos.safe else 0) + (-200 if pos.already_occupied else 0)
                pos.target_pos = target_pos
                possibilities.append(pos)
        possibilities.sort(key=lambda x: x.rank, reverse=True)
        return possibilities[0]
class board_config:
    def __init__(self, width, players_count):
        #Calculate safe houses
        player_symbols = ['x', 'o', '@', '%']
        if width == 5:
            self.pieces_count = 4
            self.safe = [3, 11, 23, 15, 13]
            self.circumferences =[
                [1, 6, 11, 16, 21, 22, 23, 24, 25, 20, 15, 10, 5, 4, 3, 2], 
                [7, 8, 9, 14, 19, 18, 17, 12],
                [13]]
            self.entries = [[3, 9, 13], [23, 17, 13], [11, 7, 13], [15, 19, 13]]
            self.repeat_chance= [4, 8]
            self.life= {4: 2, 8: 4}
        elif width == 7:
            self.pieces_count = 6
            self.safe = [4, 9, 13, 22, 25, 28, 37, 41, 46]
            self.circumferences =[
                [1, 8, 15, 22, 29, 36, 43, 44, 45, 46, 47, 48, 49, 42, 35, 28, 21, 14, 7, 6, 5, 4, 3, 2],
                [9, 10, 11, 12, 13, 20, 27, 34, 41, 40, 39, 38, 37, 30, 23, 16],
                [17, 18, 19, 26, 33, 32, 31, 24],
                [25]]
            self.entries = [[4, 13, 19, 25], [46, 37, 31, 25], [22, 9, 17, 25], [28, 41, 33, 25]]
            self.home = [4, 46, 22, 28]
            self.repeat_chance= [1, 5, 6, 12]
            self.life=  {1: 1, 5: 2, 6: 3, 12: 6}
        self.players = []
        for i in range(players_count):
            #calculate path
            path = []
            last_house = 0
            for j in range(len(self.circumferences)):
                entry = self.entries[i][j]
                length = len(self.circumferences[j])
                loopthrough = self.circumferences[j] * 2
                index = loopthrough.index(entry)
                loopthrough = loopthrough[index:index+length]
                path = path + loopthrough[:length]
                if j ==0:
                    last_house = path[-1]
            player = Player(i, path, self, last_house)
            player.symbol = player_symbols[i]
            self.players.append(player)
        for i in range(players_count):
            self.players[i].opponent = self.players[(i+1)%players_count]
class astachamma:
    def __init__(self) -> None:
        self.config = {'board_id': 7, 'players': 4, 'home': 'out', }
        self.dice = Dice(self.config['board_id'])
        self.html = Html(self)
        self.board : board_config = board_config(self.config['board_id'], self.config['players'])
        self.players = self.board.players
    def roll_dice(self):
        vals  = [self.dice.toss()]
        while vals[-1] in self.board.repeat_chance:
            vals.append(self.dice.toss())
        print(vals)
        return vals
    def run (self, player):
        vals = self.roll_dice()
        while len(vals) > 0:
            move = player.move(vals)
            context = {'p1_toss': vals, 'p2_toss': vals}
            self.html.update_html(context)
            time.sleep(3)
            if move.can_takeout:
                vals.extend(self.roll_dice())
            #Remove the values that are already used
            vals = [i for i in vals if not i in move.list_moves or move.list_moves.remove(i)]
    def run_continuously(self):
        for i in range(100):
            for player in self.board.players:
                self.run(player)
                if player.is_done():
                    print (f"Player {player.id} won")
                    return
class Html:
    def __init__(self, ashtachamma):
        self.ashtachamma = ashtachamma
        self.file = os.getcwd() + '/result.html' # fileutil.getTempfile('.html')
        self.service = Service('chromedriver.exe')
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get(self.file)
        self.house_count = self.ashtachamma.config['board_id'] ** 2
    def update_html(self, context):
        if astachamma().config['board_id']==5:
            html = open("abc.html", "r").read() #read default html 
        else:
            html = open("abc1.html", "r").read() #read default html 
        html = self.render_html(html, context)
        print(html, file=open(self.file, 'w'))
        self.driver.refresh()
    def render_html(self, html, context):
        keys = [f"[[i{i}]]" for i in range(1,self.house_count + 1)]
        d = dict(zip(keys,  ['']*self.house_count, ))
        players = self.ashtachamma.players 
        for p in players:
            for position in p.positions:
                d[f"[[i{position}]]"] += p.symbol
        for k in d:
            html = html.replace(k, d[k])
        html = html.replace('[[p1]]', f'Entry: {players[0].got_entry}, rolled in: {context["p1_toss"]}')
        html = html.replace('[[p2]]', f'Entry: {players[1].got_entry}, rolled in: {context["p2_toss"]}')
        return html
if __name__ == '__main__':
    a = astachamma()
    a.run_continuously()
