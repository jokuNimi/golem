#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 15:46:51 2023

@author: surrealpartisan
"""

import numpy as np

import creature
import item
import utils

class God(creature.Creature):
    def __init__(self, world, world_i, sin):
        super().__init__(world, world_i)
        self.sin = sin
        self.faction = np.random.choice(utils.enemyfactions)
        self.name = utils.unpronounceablename(np.random.randint(2,11))
        self.power = np.random.choice(['weak', 'powerful'])
        self.attitude = np.random.choice(['mellow', 'irritable'])
        self.pronoun = np.random.choice(['he', 'she', 'they', 'it'])
        if self.pronoun == 'they':
            self.copula = 'are'
        else:
            self.copula = 'is'
        self.prayerclocks = {}

    def bless(self, creat):
        blessing = np.random.randint(4)
        if blessing == 0:
            gift = item.Cure(creat.inventory, 0, 0, creat.world.curetypes[np.random.randint(len(creat.world.curetypes))], np.random.randint(max(0, creat.world_i-1), creat.world_i+2))
        if blessing == 1:
            gift = item.randomweapon(creat.inventory, 0, 0)
        if blessing == 2:
            gift = item.randomarmor(creat.inventory, 0, 0)
        if blessing == 3:
            gift = item.randomfood(creat.inventory, 0, 0)
        creat.log().append(self.name + ' has blessed you with a ' + gift.name + '!')

    def smite(self, target):
        targetbodypart = np.random.choice([part for part in target.bodyparts if not part.destroyed()])
        target.lasthitter = self
        if self.power == 'powerful':
            totaldamage = np.random.randint(1, 41)
        else:
            totaldamage = np.random.randint(1, 21)
        damage = min(totaldamage, targetbodypart.hp())
        targetbodypart.damagetaken += damage
        if targetbodypart.parentalconnection != None:
            partname = list(targetbodypart.parentalconnection.parent.childconnections.keys())[list(targetbodypart.parentalconnection.parent.childconnections.values()).index(targetbodypart.parentalconnection)]
        elif targetbodypart == target.torso:
            partname = 'torso'
        if not target.dying():
            if not targetbodypart.destroyed():
                self.log().append('You smote the ' + target.name + ' in the ' + partname + ', dealing ' + repr(damage) + ' damage!')
                target.log().append(self.name + ' smote you in the ' + partname + ', dealing ' + repr(damage) + ' damage!')
            else:
                self.log().append('You smote and destroyed the ' + partname + ' of the ' + target.name + '!')
                target.log().append(self.name + ' smote and destroyed your ' + partname + '!')
        else:
            self.log().append('You smote the ' + target.name + ' in the ' + partname + ', killing it!')
            target.log().append(self.name + ' smote you in the ' + partname + ', killing you!')
            target.log().append('You are dead!')
            target.die()
            target.causeofdeath = ('smite', self)

    def answer_to_prayer(self, creat):
        if self.attitude == 'irritable':
            limit = 200
        else:
            limit = 100
        if not creat in self.prayerclocks or self.prayerclocks[creat] > limit:
            creat.log().append(self.name + ' is pleased by your prayer.')
            self.bless(creat)
        else:
            creat.log().append(self.name + ' is angered by your constant pleading.')
            self.smite(creat)
        self.prayerclocks[creat] = 0