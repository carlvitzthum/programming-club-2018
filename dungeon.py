#!/usr/bin/env python
# -*- coding: utf-8 -*-

# You have to run this code!
import random
import time
import copy
from PIL import Image
import os

monsters = []
cards = []
starting_cards = []

class Player(object):
    def __init__(self, bonus=0):
        self.hp = 100
        self.wins = 0
        self.magic = 20
        self.hand = []
        self.deck = []
        self.status = []
        self.max_hand = 3
        self.bonus = bonus
        self.init_deck(self.bonus)
        for i in range(self.max_hand):
            self.draw()
        self.enemy = new_enemy(self.wins)
        print('You start by facing a %s' % self.enemy.name)

    def add_to_deck(self):
        lbound = self.wins
        ubound = self.wins + 1
        possibilities = [c for c in cards if (c.level <= ubound and c.level >= lbound)]
        if not possibilities:
            possibilities = cards
        card = copy.deepcopy(random.choice(possibilities))
        self.deck.append(card)
        return card

    def init_deck(self, bonus):
        for start in starting_cards:
            card = copy.deepcopy(start)
            self.deck.append(card)
        ### bonus point cards
        if bonus == 0:
            reward = Card('bronze blade', 10, 3, 0, ['heal:10', 'charge:10'])
        elif bonus == 1:
            reward = Card('silver blade', 15, 4, 0, ['heal:12', 'charge:12'])
        elif bonus == 2:
            reward = Card('gold blade', 20, 5, 0, ['heal:15', 'charge:15']),
        elif bonus >= 3:
            reward = Card('platinum blade', 25, 6, 0, ['heal:17', 'charge:17'])
        else:
            return
        print('BONUS: a %s has been added to your deck!' % reward.name)
        self.deck.append(reward)

    def draw(self):
        random.shuffle(self.deck)
        draw = self.deck.pop(0)
        self.hand.append(draw)
        return draw

    def play(self, idx):
        # win on completion of level 25
        if self.wins == 26:
            return self.win()
        if 'poison' in self.status:
            p_dmg = random.randint(3,16)
            self.hp -= p_dmg
            print('You take %s damage from poison!' % p_dmg)
        if 'burn' in self.status:
            b_dmg = int(self.hp / 10) + 2
            self.hp -= b_dmg
            print('You are burning and take %s damage!' % b_dmg)
        if self.hp <= 0:
                return self.die()
        if 'freeze' in self.status:
            f_dmg = random.randint(5,10)
            m_dmg = random.randint(5,10)
            self.hp -= f_dmg
            self.magic = 0 if self.magic - m_dmg < 0 else self.magic - m_dmg
            if self.hp <= 0:
                return self.die()
            print('You are frozen! You take %s damage and lose %s magic. Also you cannot move this turn!' % (f_dmg, m_dmg))
            self.status.remove('freeze')
        elif 'stun' in self.status:
            print('You are stunned and cannot move this turn!')
            self.status.remove('stun')
        elif idx.lower() == 'x':
            print('You charged magic by 5 points')
            self.magic += 5
            time.sleep(0.3)
        else:
            try:
                idx = int(idx)
            except:
                print('Bad input!')
                return
            idx -= 1  # from 1,2,3,4 to 0,1,2,3
            if idx > len(self.hand) - 1 or idx < 0:
                print('Bad input!')
                return
            if not self.enemy:
                return
            card = self.hand.pop(idx)
            card_name, power, cost, effect = card.name, card.power, card.cost, card.effect
            if card.cost > self.magic:
                print('Not enough magic! Use a different card.')
                time.sleep(0.3)
                self.hand.insert(idx, card)
                return
            self.deck.append(card)
            self.enemy.hp -= power
            self.magic -= cost
            print('You use %s!' % (card_name))
            for eff in effect:
                if 'heal:' in eff:
                    amt = int(eff.split(':')[1])
                    self.hp += amt
                    print('You healed %s hp!' % amt)
                elif 'charge:' in eff:
                    amt = int(eff.split(':')[1])
                    self.magic += amt
                    print('You charged magic by %s points!' % amt)
                elif eff == 'block':
                    if 'block' not in self.status:
                        self.status.append('block')
                elif eff not in self.enemy.status:
                    self.enemy.status.append(eff)
                    print('You %s the enemy!' % eff)
            time.sleep(0.3)
        for status in ['poison', 'burn']:
            if status in self.status:
                if random.randint(1,2) == 2:
                    self.status.remove(status)
                    print('You are no longer affected by %s.' % status)
        ## enemy effects
        if 'poison' in self.enemy.status:
            p_dmg = random.randint(3,16)
            self.enemy.hp -= p_dmg
            print('The enemy takes %s damage from poison!' % p_dmg)
        if 'burn' in self.enemy.status:
            b_dmg = int(self.enemy.hp / 10)
            self.enemy.hp -= b_dmg
            print('The enemy is burning and takes %s damage!' % b_dmg)
        if 'freeze' in self.enemy.status:
            f_dmg = random.randint(5,10)
            self.enemy.hp -= f_dmg
            print('The enemy is frozen and takes %s damage. It also cannot move this turn!' % f_dmg)
        if self.enemy.hp <= 0:
            self.wins += 1
            new_card = self.add_to_deck()
            print('Nice! You defeated the %s.\nYou learned a new move: %s\n' % (self.enemy.name, new_card.name))
            time.sleep(0.3)
            self.enemy = new_enemy(self.wins)
            randy = random.randint(1,3)
            if randy == 1:
                print('You found a wild %s. Prepare to fight!' % (self.enemy.name))
            elif randy == 2:
                print('You turn the corner and an angry %s stands before you!' % (self.enemy.name))
            else:
                print('You hear a noise. An evil %s attacks!' % (self.enemy.name))
            # open image
            if os.path.isfile('./' + self.enemy.name + '.jpg'):
                img = Image.open('./' + self.enemy.name + '.jpg')
                img.show()
            time.sleep(0.3)
        else:
            if 'stun' in self.enemy.status:
                self.enemy.status.remove('stun')
                print('The enemy is stunned and cannot move this turn!')
            elif 'freeze' in self.enemy.status:
                self.enemy.status.remove('freeze')
            else:
                attack_name, damage, effect = self.enemy.attack()
                if 'block' in self.status:
                    self.status.remove('block')
                    print('The enemy attacks using %s but you block it!' % attack_name)
                else:
                    print('The %s attacks using %s! You take %s damage.' % (self.enemy.name, attack_name, damage))
                    self.hp -= damage
                for eff in effect:
                    if eff not in self.status:
                        self.status.append(eff)
                        print('The enemy affected you with %s!' % eff)
                time.sleep(0.3)
            for status in ['poison', 'burn']:
                if status in self.enemy.status:
                    if random.randint(1,2) == 2:
                        self.enemy.status.remove(status)
                        print('The enemy is no longer affected by %s.' % status)
            if self.hp <= 0:
                return self.die()
        if len(self.hand) < self.max_hand:
            draw = self.draw()
        # self.deck.extend(self.hand)
        # self.hand = []
        # for i in range(self.max_hand):
        #     self.draw()
        return self

    def win(self):
        print("""
            ────────────────────────────────────────
            ────────────────────────────────────────
            ───────────████──███────────────────────
            ──────────█████─████────────────────────
            ────────███───███───████──███───────────
            ────────███───███───██████████──────────
            ────────███─────███───████──██──────────
            ─────────████───████───███──██──────────
            ──────────███─────██────██──██──────────
            ──────██████████────██──██──██──────────
            ─────████████████───██──██──██──────────
            ────███────────███──██──██──██──────────
            ────███─████───███──██──██──██──────────
            ───████─█████───██──██──██──██──────────
            ───██████───██──────██──────██──────────
            ─████████───██──────██─────███──────────
            ─██────██───██─────────────███──────────
            ─██─────███─██─────────────███──────────
            ─████───██████─────────────███──────────
            ───██───█████──────────────███──────────
            ────███──███───────────────███──────────
            ────███────────────────────███──────────
            ────███───────────────────███───────────
            ─────████────────────────███────────────
            ──────███────────────────███────────────
            ────────███─────────────███─────────────
            ────────████────────────██──────────────
            ──────────███───────────██──────────────
            ──────────████████████████──────────────
            ──────────████████████████──────────────
            ────────────────────────────────────────
            ────────────────────────────────────────

            ===== CONGRATULATIONS! =====
            You have cleared the dungeon
            ============================
            Starting new game in 5 seconds...
            ============================
        """)
        time.sleep(3)
        return 'new game'


    def die(self):
        print('\nYou die to the %s! You defeated %s monsters...' % (self.enemy.name, self.wins))
        print('''
            ███████████████████████████
            ███████▀▀▀░░░░░░░▀▀▀███████
            ████▀░░░░░░░░░░░░░░░░░▀████
            ███│░░░░░░░░░░░░░░░░░░░│███
            ██▌│░░░░░░░░░░░░░░░░░░░│▐██
            ██░└┐░░░░░░░░░░░░░░░░░┌┘░██
            ██░░└┐░░░░░░░░░░░░░░░┌┘░░██
            ██░░┌┘▄▄▄▄▄░░░░░▄▄▄▄▄└┐░░██
            ██▌░│██████▌░░░▐██████│░▐██
            ███░│▐███▀▀░░▄░░▀▀███▌│░███
            ██▀─┘░░░░░░░▐█▌░░░░░░░└─▀██
            ██▄░░░▄▄▄▓░░▀█▀░░▓▄▄▄░░░▄██
            ████▄─┘██▌░░░░░░░▐██└─▄████
            █████░░▐█─┬┬┬┬┬┬┬─█▌░░█████
            ████▌░░░▀┬┼┼┼┼┼┼┼┬▀░░░▐████
            █████▄░░░└┴┴┴┴┴┴┴┘░░░▄█████
            ███████▄░░░░░░░░░░░▄███████
            ██████████▄▄▄▄▄▄▄██████████
            ███████████████████████████
        ''')
        time.sleep(3)
        return 'new game'

    def see_hand(self):
        print('\n===== LEVEL %s ========================' % self.wins)
        print('Enemy: %s. HP: %s. | %s' % (self.enemy.name, self.enemy.hp, ', '.join(self.enemy.status)))
        print('===================')
        print('\n------ You ------')
        print('HP: %s. Magic: %s. | : %s' % (self.hp, self.magic, ', '.join(self.status)))
        print('--- Your hand ---')
        for i, card in enumerate(self.hand):
            print('-  %s: %s. Power: %s. Cost: %s. %s' % (i + 1, card.name, card.power, card.cost, ', '.join(card.effect)))
        print('-  x: charge up your magic by 5 points.')
        print('--- ----------- ---')
        print('======================================\n\n\n\n')


class Card(object):
    def __init__(self, name, power, cost, level, effect=[]):
        self.name = name
        self.power = power
        self.cost = cost
        self.level = level
        self.effect = effect

    def add(self):
        cards.append(self)

    def start(self):
        starting_cards.append(self)


class Monster(object):
    def __init__(self, name, hp, level=0):
        self.name = name
        self.hp = hp
        # in form name, power
        self.attacks = []
        self.level = level
        self.status = []

    def uses(self, name, power, effect):
        if not isinstance(name ,str):
            print('Attack name must be a string!')
        elif not isinstance(power, int):
            print('Attack power must be an int!')
        elif not isinstance(effect, list):
            print('Effect must be a list!')
        else:
            self.attacks.append((name, power, effect))

    def attack(self):
        if not self.attacks:
            return ('flop around', 0, [])
        else:
            return random.choice(self.attacks)

    def add(self):
        monsters.append(self)


def new_enemy(wins):
    # testing
    lbound = wins
    ubound = wins
    # lbound = wins - 1 if wins > 0 else 0
    # ubound = wins + 1
    possibilities = [enemy for enemy in monsters if (enemy.level <= ubound and enemy.level >= lbound)]
    if not possibilities:
        possibilities = monsters
    enemy = copy.deepcopy(random.choice(possibilities))
    return enemy


def play_game(bonus=3):
    if not cards or not monsters or not starting_cards:
        print('We need to make monsters and cards!')
        return
    print('\n\n\n\n\n\n================\nWelcome to the dungeon! Defeat as many monsters as you can...\n================\n')
    print('--- Exit to stop, New game to start over. ---\n')
    player = Player(bonus=bonus)
    while True:
        player.see_hand()
        time.sleep(0.5)
        move = raw_input('>> ')
        if move.lower() == 'exit':
            break
        if move.lower() == 'new game':
            print('New game! You defeated %s monsters.' % (player.wins))
            result = Player(bonus=bonus)
        else:
            result = player.play(move)
        if result == 'new game':
            result = Player(bonus=bonus)
        if result:
            player = result


### Here is a basic card and monster
monsters = []
cards = []
starting_cards = []
### Make some starting cards
custom_starting = [
    ['punch', 7, 0, 0, []],
    ['spirit flame', 10, 3, 0, ['heal:10']],
    ['spark', 9, 1, 0, ['charge:2']],
    ['magic dagger', 9, 1, 0, ['charge:2']],
]

for starter in custom_starting:
    Card(starter[0], starter[1], starter[2], starter[3], starter[4]).start()

### Make some cards to play with
custom_cards = [
    ['slash', 9, 0, 1, []],
    ['lesser charge', 5, 0, 1, ['charge:10']],
    ['lesser guardian', 0, 2, 1, ['heal:25', 'block']],
    ['defend', 0, 0, 1, ['block']],
    ['magic blast', 10, 3, 2, ['burn']],
    ['sword spin', 12, 1, 2, []],
    ['poison', 6, 2, 2, ['poison']],
    ['freeze', 6, 3, 2, ['freeze']],
    ['magic missle', 18, 3, 2, []],
    ['ninja star', 14, 0, 3, []],
    ['shock', 9, 3, 3, ['stun']],
    ['powerful kick', 7, 0, 3, ['stun']],
    ['fireball', 15, 4, 3, ['burn']],
    ['overdrive', 5, 0, 3, ['charge:10', 'stun']],
    ['lightning', 12, 5, 4, ['stun']],
    ['typhoon wave', 18, 6, 4, ['freeze']],
    ['hammer smash', 13, 0, 4, []],
    ['shield slam', 9, 0, 4, ['block']],
    ['flame lance', 17, 5, 5, ['burn']],
    ['medium charge', 5, 0, 5, ['charge:20']],
    ['medium heal', 0, 4, 5, ['heal:45']],
    ['magic bomb', 30, 4, 6, []],
    ['fart', 25, 3, 6, ['poison']],
    ['doom', 15, 7, 6, ['burn', 'poison', 'freeze']],
    ['blade dance', 21, 0, 7, []],
    ['revive', 0, 0, 7, ['heal:20']],
    ['dark ritual', 0, 15, 7, ['heal:30', 'charge:30']],
    ['demon fire', 25, 10, 8, ['burn', 'stun']],
    ['guardian', 0, 6, 8, ['heal:45', 'block']],
    ['lightning blade', 30, 5, 9, ['stun']],
    ['flame blade', 30, 5, 9, ['burn']],
    ['ice blade', 30, 5, 9, ['freeze']],
    ['mega slash', 30, 0, 10, []],
    ['blood rage', 35, 1, 10, []],
    ['toxic wave', 35, 4, 10, ['poison']],
    ['major heal', 0, 8, 11, ['heal:65']],
    ['major charge', 5, 0, 11, ['charge:30']],
    ['execute', 36, 0, 12, []],
    ['magic nova', 45, 9, 12, []],
    ['bubble gun', 50, 11 , 13, ['freeze']],
    ['great guardian', 0, 8, 13, ['heal:55', 'block']],
    ['dark sword', 40, 0, 14, ['charge:10']],
    ['excalibur', 100, 25, 14, ['stun', 'block', 'heal:10']],
    ['vampire bite', 40, 0, 15, ['heal:40']],
    ['arm cannon', 120, 30, 15, ['burn', 'stun']],
    ['deadly poison', 50, 5, 16, ['poison']],
    ['cosmic blast', 65, 10, 16, []],
    ['siphon magic', 25, 0, 17, ['charge:40']],
    ['killing strike', 60, 0, 17, []],
    ['assassinate', 150, 30, 17, []],
    ['magic explosion', 70, 12, 18, []],
    ['solar strike', 65, 10, 18, ['burn']],
    ['glacier', 70, 15, 19, ['freeze']],
    ['thunder strike', 65, 10, 19, ['stun']],
    ['onslaught', 75, 0, 20, []],
    ['vampire strike', 55, 0, 20, ['heal:55']],
    ['sacred ritual', 0, 0, 21, ['heal:60', 'charge:40']],
    ['unbreakable guardian', 0, 10, 21, ['heal:80', 'block']],
    ['elemental destruction', 60, 10, 22, ['burn', 'freeze', 'stun', 'poison']],
    ['spiked shield', 50, 0, 22, ['block']],
    ['master strike', 80, 0, 23, []],
    ['sword flurry', 90, 3, 23, []],
    ['mega magic blast', 120, 15, 24, []],
    ['divine strength', 0, 10, 24, ['heal:100, charge:50']],
    ['obliterate', 1000, 1, 25, []],
]

for card in custom_cards:
    Card(card[0], card[1], card[2], card[3], card[4]).add()

### Make some monsters
custom_monsters = [
    ['chicken', 5, 0, ['scratch', 1, []], ['egg shot', 3, []], ['peck', 2, []]],
    ['goblin runt', 8, 1, ['punch', 2, []], ['goblin hammer', 5, []]],
    ['serpent', 6, 1, ['bite', 6, []], ['venom', 4, ['poison']]],
    ['baby cave troll', 15, 2, ['club smash', 8, []], ['powerful kick', 6, ['stun']]],
    ['goblin warrior', 18, 2, ['goblin hammer', 5, []], ['smash', 10, []]],
    ['grunt', 14, 2, ['plasma pistol', 2, []], ['charged plasma pistol', 3, ['stun']]],
    ['crawler', 20, 3, ['scratch', 6, []], ['bolt shot', 9, []]],
    ['ghost', 18, 3, ['possess bite', 7, []], ['chill', 4, ['freeze']]],
    ['corrupt knight', 30, 4, ['dark sword', 8, []], ['demon slash', 4, ['burn']]],
    ['goblin shaman', 25, 4, ['magic burst', 10, []], ['summon flame', 3, ['burn']], ['summon ice', 3, ['freeze']]],
    ['siren', 40, 5, ['dark slash', 12, []], ['lava blast', 8, ['burn']]],
    ['warlock', 30, 5, ['magic missle', 15, []], ['toxic blast', 6, ['poison']], ['dragonfire', 8, ['burn']]],
    ['skull hunter', 35, 6, ['rage', 12, []], ['fire skull', 10, ['burn']]],
    ['dread goblin', 40, 6, ['spit poison', 5, ['poison']], ['6 pack attack', 12, []], ['wind attack', 15, []]],
    ['monika', 45, 7, ['death stare', 10, []], ['karate chop', 15, []], ['piano music', 6, ['stun']]],
    ['soldier', 50, 7, ['suppressor', 16, []], ['explosive shot', 5, ['burn']]],
    ['giant mech', 55, 8, ['scarab gun', 18, []]],
    ['goblin mage', 40, 8, ['magic blast', 19, []], ['elemental strike', 5, ['burn', 'poison']]],
    ['shocker', 50, 9, ['roaring thunder', 22, []], ['acid rain', 10, ['poison']]],
    ['dark knight', 60, 9, ['chaos blade', 20, []]],
    ['undead warrior', 65, 10, ['poison blade', 15, ['poison']], ['onslaught', 20, []]],
    ['cerberus', 70, 11, ['2 headed bite', 25, []], ['hot dog breath', 15, ['poison']]],
    ['goblin chief', 75, 12, ['goblin axe', 25, []], ['call reinforcements', 15, []]],
    ['super ninja', 55, 13, ['ninja stars', 25, []], ['stealthy death', 30, []]],
    ['cave troll', 80, 14, ['club smash', 22, []], ['mega kick', 8, ['stun']]],
    ['undead warlord', 85, 15, ['dark blade', 25, []], ['icy grip', 5, ['freeze']]],
    ['king cobra', 70, 16, ['venom', 15, ['poison']], ['mega bite', 35, []]],
    ['master warlock', 75, 17, ['lightning burst', 20, ['stun']], ['magic explosion', 30, []], ['doom', 40, []]],
    ['demon sentinel', 100, 18, ['demonfire', 15, ['burn']], ['massive strike', 20, []]],
    ['skeleton warlord', 90, 19, ['dark blade', 27, []]],
    ['giant cave troll', 150, 20, ['club smash', 22, []], ['ultra kick', 15, ['stun']]],
    ['master of darkness', 100, 21, ['death nova', 40, []], ['toxic wave', 25, ['poison']], ['icy shadow', 20, ['freeze']]],
    ['ancient ghost', 110, 22, ['nightmare', 45, []],['spectral fire', 35, ['burn']], ['haunt', 40, []]],
    ['evil archmage', 125, 23, ['arcane sword', 45, []], ['cosmic blast', 50, []], ['shadow word', 10, ['burn', 'freeze', 'poison']]],
    ['skeleton king', 150, 24, ['cleave', 45, []], ['killing strike', 50, ['poison']], ['thunder blade', 20, ['stun']]],
    ['lord of the dungeon', 180, 25, ['breath of frost', 25, ['freeze']], ['electric scythe', 40, ['stun']], ['shadow bolt', 50, []], ['ultimate stike', 60, []]],
]
for mon in custom_monsters:
    monster = Monster(mon[0], mon[1], mon[2])
    for i in range(len(mon) - 3):
        monster.uses(mon[i+3][0], mon[i+3][1], mon[i+3][2])
    monster.add()

import sys
def main(argv):
    try:
        bonus = int(argv[1])
    except:
        print("Bad bonus input! Should be an integer from 0 to 3.")
        sys.exit()
    play_game(bonus)

### Make sure to type 'exit' when you're done
if __name__ == "__main__":
    main(sys.argv)
