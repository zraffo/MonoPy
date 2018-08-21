import json
import random
import cmd
from random import shuffle

rules_file = open("rules.json")
rules_str = rules_file.read()
RULES = json.loads(rules_str)
TILES = []
CCDECK = []
CHDECK = []
CCNUM = 0
CHNUM = 0
PLAYERS = []
random.seed(42069)

class Game():
    global TILES, CCDECK, CHDECK, PLAYERS
    #List of Player Names
    def __init__(self, players):
        self.tiles = Tile().loadTiles()
        self.ccdeck, self.chdeck = Cards().loadCards()
        self.players = []
        for p in players:
            self.players.append(Player.from_rules(p))
        self.numPlayers = len(self.players)
        self.turnNum = 0
        self.activePlayer = self.players[0]

    def start(self):
        while True:
            i = 0
            for i in range(0, self.numPlayers):
                self.activePlayer = self.players[i]
                print("==============================================")
                print("It's " + self.activePlayer.id + "'s turn!")
                print("==============================================")
                self.activePlayer.turn()
            #i = 0
            self.turnNum = self.turnNum + 1

    def allPay(self, credit, target):
        for p in self.players:
            p.pay(credit, target)

class Tile():
    #TODO CLEAN THIS MESS UP
    tiles = []

    def loadTiles(self):
        tiles_file = open("tiles.json")
        tiles_str = tiles_file.read()
        tiles = json.loads(tiles_str)["tiles"]
        event_tiles = tiles[0]["events"]
        rr_tiles = tiles[1]["railroads"]
        util_tiles = tiles[2]["utilities"]
        prop_tiles = tiles[3]["properties"]
        for t in event_tiles:
            self.tiles.append(EventTile.from_dict(t))
        for t in rr_tiles:
            self.tiles.append(TrainTile.from_dict(t))
        for t in util_tiles:
            self.tiles.append(UtilTile.from_dict(t))
        for t in prop_tiles:
            self.tiles.append(PropTile.from_dict(t))
        self.tiles = sorted(self.tiles, key=lambda x: x.position)
        return self.tiles

    def isUtility(self):
        return False

class PropTile(Tile):
    def __init__(self, name, price, house, rent0, rent1, rent2, rent3, rent4, rentH, mortgage, position, canBuild=False):
        self.name = name
        self.price = price
        self.house = house
        self.rent0 = rent0
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.rentH = rentH
        self.mortgage = mortgage
        self.position = position
        #self.owned = False
        self.owner = None
        self.curRent = 0
        self.canBuild = canBuild

    @classmethod
    def from_dict(cls, args):
        if isinstance(args, dict):
            name, price, house, rent0, rent1, rent2, rent3, rent4, rentH, mortgage, position = args["name"], args["price"], args["house"], args["rent0"], args["rent1"], args["rent2"], args["rent3"], args["rent4"], args["rentH"], args["mortgage"], args["position"]
            return cls(name, price, house, rent0, rent1, rent2, rent3, rent4, rentH, mortgage, position)

    def doAction(self, player):
        if self.isOwned():
            print("You must pay " + self.owner.id + " $" + str(self.curRent) + ".")
            player.pay(-1 * self.curRent, self.owner)
        else:
            playerAction = str.lower(input("Buy (B), Auction (A), or Info (I)?: "))
            if playerAction == "b":
                self.buy(player)
            if playerAction == "a":
                self.auction()
            if playerAction == "i":
                print(self.name)
                print("Rent: $" + str(self.rent0))
                print("Rent with 1 house: $" + str(self.rent1))
                print("Rent with 2 houses: $" + str(self.rent2))
                print("Rent with 3 houses: $" + str(self.rent3))
                print("Rent with 4 houses: $" + str(self.rent4))
                print("Rent with a hotel: $" + str(self.rentH))
                print("House price: $" + str(self.house))
                print("Mortgage value: $" + str(self.mortgage))
                self.doAction(player)


    def buy(self, player):
        if player.money < self.price:
            print("You don't have enough money! You are missing $" + str(self.price - player.money) + ".")
        else:
            print("You bought " + self.name + " for $" + str(self.price))
            player.money = player.money - self.price
            self.curRent = self.rent0
            self.owner = player

    def isOwned(self):
        return self.owner != None

class TrainTile(Tile):
    def __init__(self, name, price, rent, rent2, rent3, rent4, mortgage, position):
        self.name = name
        self.price = price
        self.rent = rent
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.mortgage = mortgage
        self.position = position
        self.owner = None
        self.curRent = 0

    @classmethod
    def from_dict(cls, args):
        if isinstance(args, dict):
            name, price, rent, rent2, rent3, rent4, mortgage, position = args["name"], args["price"], args["rent"], args["rent2"], args["rent3"], args["rent4"], args["mortgage"], args["position"]
            return cls(name, price, rent, rent2, rent3, rent4, mortgage, position)

    def doAction(self, player):
        if self.isOwned():
            print("You must pay " + self.owner.id + " $" + str(self.curRent) + ".")
            player.pay(-1 * self.curRent, self.owner)
        else:
            playerAction = str.lower(input("Buy (B), Auction (A), or Info (I)?: "))
            if playerAction == "b":
                self.buy(player)
            if playerAction == "a":
                self.auction()
            if playerAction == "i":
                print(self.name)
                print("Rent: $" + str(self.rent))
                print("Rent with 2 railroads: $" + str(self.rent2))
                print("Rent with 3 railroads: $" + str(self.rent3))
                print("Rent with 4 railroads: $" + str(self.rent4))
                print("Mortgage value: $" + str(self.mortgage))
                self.doAction(player)

    def buy(self, player):
        if player.money < self.price:
            print("You don't have enough money! You are missing $" + str(self.price - player.money) + ".")
        else:
            print("You bought " + self.name + " for $" + str(self.price))
            player.money = player.money - self.price
            self.owner = player

    def isOwned(self):
        return self.owner != None


class UtilTile(Tile):
    def __init__(self, name, price, rent, rent2, mortgage, position):
        self.name = name
        self.price = price
        self.rent = rent
        self.rent2 = rent2
        self.mortgage = mortgage
        self.owner = None
        self.position = position
        self.curRent = 0

    @classmethod
    def from_dict(cls, args):
        if isinstance(args, dict):
            name, price, rent, rent2, mortgage, position = args["name"], args["price"], args["rent"], args["rent2"], args["mortgage"], args["position"]
            return cls(name, price, rent, rent2, mortgage, position)

    def doAction(self, player, roll):
        if self.isOwned():
            print("You must pay " + self.owner.id + " $" + str(self.curRent) + ".")
            player.pay(-1 * self.curRent * roll, self.owner)
        else:
            playerAction = str.lower(input("Buy (B), Auction (A), or Info (I)?: "))
            if playerAction == "b":
                self.buy(player)
            if playerAction == "a":
                self.auction()
            if playerAction == "i":
                print(self.name)
                print("Rent: " + str(self.rent) + "x dice roll.")
                print("Rent with 2 utilities: " + str(self.rent2) + "x dice roll.")
                print("Mortgage value: $" + str(self.mortgage))
                self.doAction(player)

    def buy(self, player):
        if player.money < self.price:
            print("You don't have enough money! You are missing $" + str(self.price - player.money) + ".")
        else:
            print("You bought " + self.name + " for $" + str(self.price))
            player.money = player.money - self.price
            self.owner = player

    def isUtility(self):
        return True

    def isOwned(self):
        return self.owner != None

class EventTile(Tile):
    def __init__(self, name, action, position):
        self.name = name
        self.action = action
        self.position = position

    @classmethod
    def from_dict(cls, args):
        if isinstance(args, dict):
            name, action, position = args["name"], args["action"], args["position"]
            return cls(name, action, position)

    def doAction(self, player):
        if self.action == "go":
            player.passGo()
        if self.action == "comm_chest":
            player.ccDraw()
        if self.action == "chance":
            player.chDraw()
        if self.action == "inc_tax":
            player.incTax()
        if self.action == "none":
            player.doNothing()
        if self.action == "to_jail":
            player.goToJail()
        if self.action == "lux_tax":
            player.luxTax()

class Cards():
    ccDeck = []
    chDeck = []

    def loadCards(self):
        cards_file = open("cards.json")
        cards_str = cards_file.read()
        cards = json.loads(cards_str)["cards"]
        cc_cards = cards[0]["community_chest"]
        chance_cards = cards[1]["chance"]
        for c in cc_cards:
            self.ccDeck.append(self.Card.from_dict(c))
        for c in chance_cards:
            self.chDeck.append(self.Card.from_dict(c))
        shuffle(self.ccDeck)
        shuffle(self.chDeck)
        return self.ccDeck, self.chDeck

    class Card():
        def __init__(self, text, credit, action):
            self.text = text
            self.credit = credit
            self.action = action

        @classmethod
        def from_dict(cls, args):
            if isinstance(args, dict):
                text, credit, action = args["text"], args["credit"], args["action"]
                return cls(text, credit, action)

        def doAction(self, player):
            if self.action == "to_go":
                player.toGo()
            if self.action == "bank":
                player.bank(self.credit)
            if self.action == "get_out":
                player.jailCard()
            if self.action == "m_player":
                player.allPay(self.credit)
            if self.action == "repairs":
                player.repair(self.credit)
            if self.action == "to":
                player.goTo(self.credit)
            if self.action == "move_back":
                player.moveBack(self.credit)
            if self.action == "payOthers":
                player.payOthers(self.credit)

TILES = Tile().loadTiles()
CCDECK, CHDECK = Cards().loadCards()

class Player():
    global TILES, CCDECK, CHDECK, CCNUM, CHNUM, PLAYERS
    def __init__(self, id, money, curTile, isTurn, inJail, properties=[], numGetOut=0, numHouses=0, numHotels=0):
        self.id = id
        self.money = money
        self.curTile = curTile
        self.isTurn = isTurn
        self.inJail = inJail
        self.hasRolled = False
        self.numGetOut = numGetOut
        self.numHouses = numHouses
        self.numHotels = numHotels
        self.properties = properties
        self.lastRoll = 0

    @classmethod
    def from_rules(cls, args):
        if isinstance(args, str):
            return cls(args, RULES["start_money"], 0, False, False)

    def roll(self):
        d1 = random.randint(1,6)
        d2 = random.randint(1,6)
        move = d1 + d2
        print("You rolled a " + str(d1) + " and a " + str(d2) + ". Moving " + str(move) + " spaces...")
        doubles = d1 == d2
        if doubles:
            print("You rolled doubles! Roll again!")
        return move, doubles

    def move(self, numTiles):
        self.curTile = self.curTile + numTiles
        if self.curTile >= 40:
            self.passGo()
            self.curTile = self.curTile % 40
        if numTiles != 1:
            print("You have landed on " + TILES[self.curTile].name + ".")

    def action(self, curTile):
        cur = TILES[self.curTile]
        #print(cur)
        if cur.isUtility():
            cur.doAction(self, self.lastRoll)
        else:
            cur.doAction(self)

    def checkMoney(self, amnt):
        if (self.money + amnt) < 0:
            self.liquidate(amnt)
        else:
            pass

    def liquidate(self, amnt):
        print("You do not have enough money, you must mortgage properties, sell houses/hotels, or trade.")
        choice = input("Mortgage (M), Sell (S), or Trade (T)?: ")

    def rollTurn(self):
        move, doubles = self.roll()
        self.lastRoll = move
        self.move(move)
        self.action(self.curTile)
        if doubles:
            self.turn()
        #self.endTurn()

    def pay(self, credit, target):
        self.checkMoney(credit)
        self.money = self.money - credit
        target.money = target.money + credit

    def ccDraw(self):
        global CCNUM, CCDECK
        if CCNUM == len(CCDECK):
            shuffle(CCDECK)
            CCNUM = 0
        curCard = CCDECK[CCNUM]
        CCNUM = CCNUM + 1
        print("You drew: " + "'" + curCard.text + "''")
        curCard.doAction(self)

    def chDraw(self):
        global CHNUM, CHDECK
        if CHNUM == len(CHDECK):
            shuffle(CHDECK)
            CHNUM = 0
        curCard = CHDECK[CHNUM]
        CHNUM = CHNUM + 1
        print("You drew: " + "'" + curCard.text + "''")
        curCard.doAction(self)

    def toGo(self):
        self.curTile = 0
        self.action(self.curTile)

    def passGo(self):
        print("Collect $200 for passing Go!")
        self.money = self.money + 200

    def incTax(self):
        self.checkMoney(-200)
        self.money = self.money - 200

    def luxTax(self):
        self.checkMoney(-75)
        self.money = self.money - 75

    def doNothing(self):
        pass

    def goToJail(self):
        self.curTile=9

    def bank(self, credit):
        self.checkMoney(credit)
        self.money = self.money + credit

    def jailCard(self):
        self.numGetOut = self.numGetOut + 1

    def allPay(self, credit):
        GAME.allPay(credit, self)

    def payOthers(self, credit):
        players = GAME.players
        total = credit * len(players - 1)
        self.checkMoney(total)
        #self.money = self.money - total
        for p in players:
            self.pay(credit, p)

    def repair(self, credit):
        total = (credit[0] * self.numHouses) + (credit[1] * self.numHotels)
        self.checkMoney(total)
        self.bank(total)

    def to(self, location):
        if location == "utility":
            self.closestUtility()
            self.action(self.curTile)
        if location == "rr":
            self.closestRail()
            self.action(self.curTile)
        else:
            self.goTo(location)

    def goTo(self, location):
        onLoc = TILES[self.curTile].name == location
        while not onLoc:
            self.move(1)
            onLoc = (TILES[self.curTile].name == location)
        print("You have landed on " + TILES[self.curTile].name + ".")

    def moveBack(self, spaces):
        self.curTile = self.curTile - 3
        self.action(self.curTile)

    def closestUtility(self):
        onUtility = TILES[self.curTile].isUtility()
        while not onUtility:
            self.curTile = self.curTile + 1
            onUtility = TILES[self.curTile].isUtility()

    def closestRail(self):
        onRR = TILES[self.curTile].isRR()
        while not onRR:
            self.curTile = self.curTile + 1
            onRR = TILES[self.curTile].isRR()

    def turn(self):
        self.hasRolled = False
        self.isTurn = True
        def prompt():
            if self.hasRolled:
                playerAction = str.lower(input("You have $" + str(self.money) + ". Trade (T), Mortgage (M), Build (B), Sell (S), or End Turn (E)?: "))
            else:
                playerAction = str.lower(input("You have $" + str(self.money) + ". Roll (R), Trade (T), Mortgage (M), Build (B), or Sell (S)?: "))
            return playerAction

        while self.isTurn:
            playerAction = prompt()
            move, doubles = 0, False
            if playerAction == "r":
                if self.hasRolled:
                    print("You already rolled!")
                    self.turn()
                self.rollTurn()
                self.hasRolled = True
                #prompt()
            if playerAction == "t":
                targetPlayer = str.lower(input("Which player would you like to trade with?: "))
            if playerAction == "m":
                mortProp = str.lower(input("Which property would you like to mortgage?: "))
            if playerAction == "b":
                targetProp = str.lower(input("Which color would you like to build on?: "))
            if playerAction == "s":
                targetProp = str.lower(input("Which color would you like to sell buildings from?: "))
            if playerAction == "e":
                #break
                if self.hasRolled:
                    self.isTurn = False
                    self.hasRolled = False
                    #break
                else:
                    print("You must roll first!")

    def endTurn(self):
        self.isTurn = False
        GAME.nextTurn()

NUM_PLAYERS = int(input("How many people are playing?: "))
PLAYER_NAMES = []
for i in range(1, NUM_PLAYERS + 1):
    name = input("Player " + str(i) + ": ")
    PLAYER_NAMES.append(name)
print("==============================================")
print("RULES: ")
print("Starting money: $" + str(RULES["start_money"]))
print("Dice: " + str(RULES["dice"]))
print("Max turns in jail: " + str(RULES["jail_turns"]))
print("Max turns: " + str(RULES["turn_limit"]))
print("==============================================")
print("Rolling to see who goes first...")
shuffle(PLAYER_NAMES)
print(PLAYER_NAMES[0] + " will go first!")
print("Generating board...")
GAME = Game(PLAYER_NAMES)
#PLAYERS = GAME.players
GAME.start()
