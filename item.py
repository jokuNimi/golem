# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 20:48:19 2022

@author: SurrealPartisan
"""

from collections import namedtuple
import numpy as np

import utils

Attack = namedtuple('Attack', ['name', 'verb2nd', 'verb3rd', 'post2nd', 'post3rd', 'hitprobability', 'time', 'mindamage', 'maxdamage', 'bane', 'special'])

class Item():
    def __init__(self, owner, x, y, name, char, color):
        self.owner = owner  # A list, such as inventory or list of map items
        self.owner.append(self)
        self.x = x
        self.y = y
        self.name = name
        self.char = char
        self.color = color
        self.maxhp = np.inf
        self.damagetaken = 0
        self.weight = 0
        self.carryingcapacity = 0
        self.consumable = False
        self.edible = False
        self.cure = False
        self.wieldable = False
        self.weapon = False
        self.bodypart = False
        self.wearable = False
        self.isarmor = False

    def hp(self):
        return self.maxhp - self.damagetaken

    def destroyed(self):
        return self.damagetaken >= self.maxhp

    def attackslist(self):
        return []

    def minespeed(self):
        return 0

class Food(Item):
    def __init__(self, owner, x, y, name, char, color, maxhp, material, weight):
        super().__init__(owner, x, y, name, char, color)
        self.maxhp = maxhp
        self.material = material
        self.weight = weight
        self.basename = name
        self.consumable = True
        self.edible = True

    def consume(self, user, efficiency):
        if int(self.hp()*efficiency) > user.hunger:
            self.damagetaken += int(user.hunger/efficiency)
            user.hunger = 0
            user.log().append('You ate some of the ' + self.name + '.')
            user.log().append('You are satiated.')
            if self.damagetaken < 0.4*self.maxhp:
                self.name = 'partially eaten ' + self.basename
            elif self.damagetaken < 0.6*self.maxhp:
                self.name = 'half-eaten ' + self.basename
            else:
                self.name = 'mostly eaten ' + self.basename
        else:
            user.hunger -= int(self.hp()*efficiency)
            self.damagetaken = self.maxhp
            self.owner.remove(self)
            user.log().append('You ate the ' + self.name + '.')
            if user.hunger == 0:
                user.log().append('You are satiated.')

def randomfood(owner, x, y):
    i = np.random.randint(2)
    if i == 0:
        return Food(owner, x, y, 'hamburger', '*', (250, 220, 196), 20, 'cooked meat', 250)
    elif i == 1:
        return Food(owner, x, y, 'veggie burger', '*', (250, 220, 196), 20, 'vegetables', 250)

CureType = namedtuple('CureType', ['curedmaterial', 'name', 'hpgiven_base', 'dosage'])

class Cure(Item):
    def __init__(self, owner, x, y, curetype, level):
        if curetype.curedmaterial == 'living flesh':
            color = (255, 0, 0)
            name = 'dose of medication labeled "' + curetype.name + ', ' + repr(curetype.dosage*level) + ' mg"'
        elif curetype.curedmaterial == 'undead flesh':
            color = (0, 255, 0)
            name = 'vial of ectoplasmic infusion labeled "' + curetype.name + ', ' + repr(curetype.dosage*level) + ' mmol/l"'
        super().__init__(owner, x, y, name, '!', color)
        self.consumable = True
        self.cure = True
        self.curetype = curetype
        self.curedmaterial = curetype.curedmaterial
        self._hpgiven = curetype.hpgiven_base * level
        self.weight = 100
    
    def hpgiven(self):
        return self._hpgiven
    
    def consume(self, user):
        partlist = [part for part in user.bodyparts if part.material == self.curedmaterial and not part.destroyed()]
        if len(partlist) > 0:
            part = max(partlist, key=lambda part : part.damagetaken)
            user.heal(part, self.hpgiven())
        else:
            user.log().append('You were unaffected.')
        self.owner.remove(self)

class Dagger(Item):
    def __init__(self, owner, x, y, material, enchantment, bane):
        if enchantment == 0:
            enchaname = ''
        elif enchantment > 0:
            enchaname = '+' + repr(enchantment) + ' '
        banename = ''
        for b in bane:
            banename += b + '-bane '
        name = enchaname + banename + material + ' dagger'
        if material == 'bone': color = (255, 255, 204)
        if material == 'chitin': color = (0, 102, 0)
        if material == 'bronze': color = (150,116,68)
        if material == 'iron': color = (200, 200, 200)
        if material == 'steel': color = (210, 210, 210)
        if material == 'elven steel': color = (210, 210, 210)
        if material == 'dwarven steel': color = (210, 210, 210)
        if material == 'nanotube': color = (51, 0, 0)
        if material == 'adamantine': color = (51, 51, 0)
        super().__init__(owner, x, y, name, '/', color)
        self.wieldable = True
        self.weapon = True
        self.bane = bane
        if material == 'bone':
            self.mindamage = 1 + enchantment
            self.maxdamage = 15 + enchantment
            density = 20
        if material == 'chitin':
            self.mindamage = 1 + enchantment
            self.maxdamage = 15 + enchantment
            density = 20
        if material == 'bronze':
            self.mindamage = 1 + enchantment
            self.maxdamage = 20 + enchantment
            density = 75
        if material == 'iron':
            self.mindamage = 1 + enchantment
            self.maxdamage = 25 + enchantment
            density = 79
        if material == 'steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 30 + enchantment
            density = 79
        if material == 'elven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 30 + enchantment
            density = 60
        if material == 'dwarven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 32 + enchantment
            density = 80
        if material == 'nanotube':
            self.mindamage = 1 + enchantment
            self.maxdamage = 40 + enchantment
            density = 10
        if material == 'adamantine':
            self.mindamage = 1 + enchantment
            self.maxdamage = 40 + enchantment
            density = 100
        self.weight = 6*density

    def attackslist(self):
        return[Attack(self.name, 'stabbed', 'stabbed', '', '', 0.8, 1, self.mindamage, self.maxdamage, self.bane, [('bleed', 0.2)])]

def randomdagger(owner, x, y):
    enchantment = 0
    while np.random.rand() < 0.5:
        enchantment += 1
    bane = []
    if np.random.rand() < 0.1:
        bane = [np.random.choice(utils.enemyfactions)]
    return Dagger(owner, x, y, np.random.choice(['bone', 'chitin', 'bronze', 'iron', 'steel', 'elven steel', 'dwarven steel', 'nanotube', 'adamantine'], p=[0.15, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05, 0.02, 0.03]), enchantment, bane)

class Spear(Item):
    def __init__(self, owner, x, y, material, enchantment, bane):
        if enchantment == 0:
            enchaname = ''
        elif enchantment > 0:
            enchaname = '+' + repr(enchantment) + ' '
        banename = ''
        for b in bane:
            banename += b + '-bane '
        name = enchaname + banename + material + ' spear'
        if material == 'bone': color = (255, 255, 204)
        if material == 'chitin': color = (0, 102, 0)
        if material == 'bronze': color = (150,116,68)
        if material == 'iron': color = (200, 200, 200)
        if material == 'steel': color = (210, 210, 210)
        if material == 'elven steel': color = (210, 210, 210)
        if material == 'dwarven steel': color = (210, 210, 210)
        if material == 'nanotube': color = (51, 0, 0)
        if material == 'adamantine': color = (51, 51, 0)
        super().__init__(owner, x, y, name, '/', color)
        self.wieldable = True
        self.weapon = True
        self.bane = bane
        if material == 'bone':
            self.mindamage = 1 + enchantment
            self.maxdamage = 15 + enchantment
            density = 20
        if material == 'chitin':
            self.mindamage = 1 + enchantment
            self.maxdamage = 15 + enchantment
            density = 20
        if material == 'bronze':
            self.mindamage = 1 + enchantment
            self.maxdamage = 20 + enchantment
            density = 75
        if material == 'iron':
            self.mindamage = 1 + enchantment
            self.maxdamage = 25 + enchantment
            density = 79
        if material == 'steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 30 + enchantment
            density = 79
        if material == 'elven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 30 + enchantment
            density = 60
        if material == 'dwarven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 32 + enchantment
            density = 80
        if material == 'nanotube':
            self.mindamage = 1 + enchantment
            self.maxdamage = 40 + enchantment
            density = 10
        if material == 'adamantine':
            self.mindamage = 1 + enchantment
            self.maxdamage = 40 + enchantment
            density = 100
        self.weight = 6*density + 2000

    def attackslist(self):
        if len([part for part in self.owner.owner.owner if part.capableofwielding and len(part.wielded) == 0]) > 0:  # looking for free hands or other appendages capable of wielding.
            return[Attack(self.name, 'thrust', 'thrust', ' with a ' + self.name, ' with a ' + self.name, 0.8, 1, self.mindamage, self.maxdamage, self.bane, [('charge',)])]
        else:
            return[Attack(self.name, 'thrust', 'thrust', ' with a ' + self.name, ' with a ' + self.name, 0.6, 1, self.mindamage, int(self.maxdamage*0.75), self.bane, [('charge',)])]

def randomspear(owner, x, y):
    enchantment = 0
    while np.random.rand() < 0.5:
        enchantment += 1
    bane = []
    if np.random.rand() < 0.1:
        bane = [np.random.choice(utils.enemyfactions)]
    return Spear(owner, x, y, np.random.choice(['bone', 'chitin', 'bronze', 'iron', 'steel', 'elven steel', 'dwarven steel', 'nanotube', 'adamantine'], p=[0.15, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05, 0.02, 0.03]), enchantment, bane)

class Mace(Item):
    def __init__(self, owner, x, y, material, enchantment, bane):
        if enchantment == 0:
            enchaname = ''
        elif enchantment > 0:
            enchaname = '+' + repr(enchantment) + ' '
        banename = ''
        for b in bane:
            banename += b + '-bane '
        name = enchaname + banename + material + ' mace'
        if material == 'bone': color = (255, 255, 204)
        if material == 'chitin': color = (0, 102, 0)
        if material == 'bronze': color = (150,116,68)
        if material == 'iron': color = (200, 200, 200)
        if material == 'steel': color = (210, 210, 210)
        if material == 'elven steel': color = (210, 210, 210)
        if material == 'dwarven steel': color = (210, 210, 210)
        if material == 'nanotube': color = (51, 0, 0)
        if material == 'adamantine': color = (51, 51, 0)
        super().__init__(owner, x, y, name, '/', color)
        self.wieldable = True
        self.weapon = True
        self.bane = bane
        if material == 'bone':
            self.mindamage = 1 + enchantment
            self.maxdamage = 18 + enchantment
            density = 20
        if material == 'chitin':
            self.mindamage = 1 + enchantment
            self.maxdamage = 18 + enchantment
            density = 20
        if material == 'bronze':
            self.mindamage = 1 + enchantment
            self.maxdamage = 24 + enchantment
            density = 75
        if material == 'iron':
            self.mindamage = 1 + enchantment
            self.maxdamage = 30 + enchantment
            density = 79
        if material == 'steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 36 + enchantment
            density = 79
        if material == 'elven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 36 + enchantment
            density = 60
        if material == 'dwarven steel':
            self.mindamage = 1 + enchantment
            self.maxdamage = 37 + enchantment
            density = 80
        if material == 'nanotube':
            self.mindamage = 1 + enchantment
            self.maxdamage = 48 + enchantment
            density = 10
        if material == 'adamantine':
            self.mindamage = 1 + enchantment
            self.maxdamage = 48 + enchantment
            density = 100
        self.weight = 50*density

    def attackslist(self):
        if len([part for part in self.owner.owner.owner if part.capableofwielding and len(part.wielded) == 0]) > 0:  # looking for free hands or other appendages capable of wielding.
            return[Attack(self.name, 'hit', 'hit', ' with a ' + self.name, ' with a ' + self.name, 0.8, 1, self.mindamage, self.maxdamage, self.bane, [('knockback', 0.2)])]
        else:
            return[Attack(self.name, 'hit', 'hit', ' with a ' + self.name, ' with a ' + self.name, 0.6, 1, self.mindamage, int(self.maxdamage*0.75), self.bane, [('knockback', 0.1)])]

def randommace(owner, x, y):
    enchantment = 0
    while np.random.rand() < 0.5:
        enchantment += 1
    bane = []
    if np.random.rand() < 0.1:
        bane = [np.random.choice(utils.enemyfactions)]
    return Mace(owner, x, y, np.random.choice(['bone', 'chitin', 'bronze', 'iron', 'steel', 'elven steel', 'dwarven steel', 'nanotube', 'adamantine'], p=[0.15, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05, 0.02, 0.03]), enchantment, bane)

class LightPick(Item):
    def __init__(self, owner, x, y):
        super().__init__(owner, x, y, 'light pick', '\\', (186, 100, 13))
        self.wieldable = True
        self.weapon = True
        self.weight = 1500

    def attackslist(self):
        return[Attack('light pick', 'hit', 'hit', ' with a light pick', ' with a light pick', 0.6, 1.5, 1, 20, [], [])]

    def minespeed(self):
        return 0.25

class HeavyPick(Item):
    def __init__(self, owner, x, y):
        super().__init__(owner, x, y, 'heavy pick', '\\', (186, 100, 13))
        self.wieldable = True
        self.weapon = True
        self.weight = 3000

    def attackslist(self):
        if len([part for part in self.owner.owner.owner if part.capableofwielding and len(part.wielded) == 0]) > 0:  # looking for free hands or other appendages capable of wielding.
            return[Attack('heavy pick', 'hit', 'hit', ' with a heavy pick', ' with a heavy pick', 0.6, 1.5, 1, 30, [], [])]
        else:
            return[Attack('heavy pick', 'hit', 'hit', ' with a heavy pick', ' with a heavy pick', 0.4, 2, 1, 20, [], [])]

    def minespeed(self):
        if len([part for part in self.owner.owner.owner if part.capableofwielding and len(part.wielded) == 0]) > 0:  # looking for free hands or other appendages capable of wielding.
            return 0.33
        else:
            return 0.2

def randomweapon(owner, x, y):
    return np.random.choice([HeavyPick, LightPick, randomdagger, randomspear, randommace], p=[0.125, 0.125, 0.25, 0.25, 0.25])(owner, x, y)

class PieceOfArmor(Item):
    def __init__(self, owner, x, y, wearcategory, material, enchantment):
        if enchantment == 0:
            enchaname = ''
        elif enchantment > 0:
            enchaname = '+' + repr(enchantment) + ' '
        name = enchaname + material + ' ' + wearcategory
        if material == 'leather': color = (186, 100, 13)
        if material == 'bone': color = (255, 255, 204)
        if material == 'chitin': color = (0, 102, 0)
        if material == 'bronze': color = (150,116,68)
        if material == 'iron': color = (200, 200, 200)
        if material == 'steel': color = (210, 210, 210)
        if material == 'elven steel': color = (210, 210, 210)
        if material == 'dwarven steel': color = (210, 210, 210)
        if material == 'nanotube': color = (51, 0, 0)
        if material == 'adamantine': color = (51, 51, 0)
        super().__init__(owner, x, y, name, '[', color)
        self.wearcategory = wearcategory
        self.wearable = True
        self.isarmor = True
        if material == 'leather':
            self.maxhp = 100
            self.mindamage = 0 + enchantment
            self.maxdamage = 5 + enchantment
            density = 4
        if material == 'bone':
            self.maxhp = 100
            self.mindamage = 0 + enchantment
            self.maxdamage = 10 + enchantment
            density = 20
        if material == 'chitin':
            self.maxhp = 150
            self.mindamage = 0 + enchantment
            self.maxdamage = 10 + enchantment
            density = 20
        if material == 'bronze':
            self.maxhp = 200
            self.mindamage = 0 + enchantment
            self.maxdamage = 10 + enchantment
            density = 75
        if material == 'iron':
            self.maxhp = 300
            self.mindamage = 0 + enchantment
            self.maxdamage = 15 + enchantment
            density = 79
        if material == 'steel':
            self.maxhp = 400
            self.mindamage = 0 + enchantment
            self.maxdamage = 20 + enchantment
            density = 79
        if material == 'elven steel':
            self.maxhp = 400
            self.mindamage = 0 + enchantment
            self.maxdamage = 20 + enchantment
            density = 60
        if material == 'dwarven steel':
            self.maxhp = 440
            self.mindamage = 0 + enchantment
            self.maxdamage = 22 + enchantment
            density = 80
        if material == 'nanotube':
            self.maxhp = 400
            self.mindamage = 0 + enchantment
            self.maxdamage = 20 + enchantment
            density = 10
        if material == 'adamantine':
            self.maxhp = 800
            self.mindamage = 0 + enchantment
            self.maxdamage = 40 + enchantment
            density = 100

        if wearcategory == 'chest armor':
            self.weight = 200*density
        if wearcategory == 'barding':
            self.weight = 200*density
        if wearcategory == 'gauntlet':
            self.weight = 10*density
        if wearcategory == 'leg armor':
            self.weight = 50*density
        if wearcategory == 'wheel cover':
            self.weight = 50*density
        if wearcategory == 'helmet':
            self.weight = 20*density
        if wearcategory == 'tentacle armor':
            self.weight = 20*density

def randomarmor(owner, x, y):
    enchantment = 0
    while np.random.rand() > 0.5:
        enchantment += 1
    return PieceOfArmor(owner, x, y, np.random.choice(['chest armor', 'barding', 'gauntlet', 'leg armor', 'wheel cover', 'helmet', 'tentacle armor']), np.random.choice(['leather', 'bone', 'chitin', 'bronze', 'iron', 'steel', 'elven steel', 'dwarven steel', 'nanotube', 'adamantine'], p=[0.25, 0.1, 0.05, 0.20, 0.20, 0.05, 0.05, 0.05, 0.02, 0.03]), enchantment)

class Backpack(Item):
    def __init__(self, owner, x, y):
        super().__init__(owner, x, y, 'backpack', '¤', (0, 155, 0))
        self.wearable = True
        self.wearcategory = 'backpack'
        self.carryingcapacity = 20000
        self.weight = 500