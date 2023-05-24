from equip import *
import copy
import pygame
import pygame_gui
import random
import ctypes


# Disable windows app scaling 
ctypes.windll.user32.SetProcessDPIAware()

# A character have the following attributes: name, maxhp, hp, atk, def,
# spd, eva, acc, crit, critdmg, critdef, penetration, lvl, exp, maxmp, mp, hpregen,
# mpregen, equip, buffs, debuffs, hpdrain, thorn 

class Character:
    def __init__(self, name, lvl, exp=0, equip=[], image=None):
        self.name = name
        self.maxhp = lvl * 100
        self.hp = lvl * 100
        self.atk = lvl * 5
        self.defense = lvl * 5
        self.spd = lvl * 5
        self.eva = 0.05
        self.acc = 0.95
        self.crit = 0.05
        self.critdmg = 2.00
        self.critdef = 0.00
        self.penetration = 0.05
        self.lvl = lvl
        self.exp = exp
        self.maxexp = self.calculate_maxexp()
        self.maxmp = lvl * 50
        self.mp = lvl * 50
        self.hpregen = 0.00
        self.mpregen = 0.00
        self.equip = []
        # The buffs and debuffs should be list of objects.
        self.buffs = []
        self.debuffs = []
        self.hpdrain = 0.00
        self.thorn = 0.00
        self.heal_efficiency = 1.00
        self.final_damage_taken_multipler = 1.00
        self.ally = []
        self.enemy = []
        self.image = image
        self.calculate_equip_effect()

    def reset_stats(self):
        self.maxhp = self.lvl * 100
        self.hp = self.lvl * 100
        self.atk = self.lvl * 5
        self.defense = self.lvl * 5
        self.spd = self.lvl * 5
        self.eva = 0.05
        self.acc = 0.95
        self.crit = 0.05
        self.critdmg = 2.00
        self.critdef = 0.00
        self.penetration = 0.05
        self.maxmp = self.lvl * 50
        self.mp = self.lvl * 50
        self.hpregen = 0.00
        self.mpregen = 0.00
        self.hpdrain = 0.00
        self.thorn = 0.00
        self.heal_efficiency = 1.00
        self.final_damage_taken_multipler = 1.00

    # Calculate equip effects. Equip is a list of objects.
    def calculate_equip_effect(self):
        for item in self.equip:
            self.maxhp += item.maxhp_flat
            self.atk += item.atk_flat
            self.defense += item.def_flat
            self.spd += item.spd_flat

            self.maxhp *= 1 + item.maxhp_percent
            self.maxhp = int(self.maxhp)
            self.atk *= 1 + item.atk_percent
            self.atk = int(self.atk)
            self.defense *= 1 + item.def_percent
            self.defense = int(self.defense)
            self.spd *= 1 + item.spd
            self.spd = int(self.spd)

            self.eva += item.eva
            self.acc += item.acc
            self.crit += item.crit
            self.critdmg += item.critdmg
            self.critdef += item.critdef
            self.penetration += item.penetration
            self.heal_efficiency += item.heal_efficiency
        if self.hp < self.maxhp:
            self.hp = self.maxhp
        return self.equip

    # Normal attack logic
    def normal_attack(self):
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 2 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")

    # Action logic
    def action(self):
        if self.canAction():
            self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot action this turn.\n")
            print(f"{self.name} cannot action this turn.")

    # Print the character's stats
    def __str__(self):
        return "{:<20s} MaxHP: {:>5d} HP: {:>5d} ATK: {:>4d} DEF: {:>4d} Speed: {:>4d}".format(self.name, self.maxhp, self.hp, self.atk, self.defense, self.spd)

    def tooltip_string(self):
        return f"{self.name}\n" \
            f"hp: {self.hp}/{self.maxhp}\n" \
            f"atk: {self.atk}\n" \
            f"def: {self.defense}\n" \
            f"speed: {self.spd}\n" \
            f"eva: {self.eva*100:.2f}%\n" \
            f"acc: {self.acc*100:.2f}%\n" \
            f"crit: {self.crit*100:.2f}%\n" \
            f"critdmg: {self.critdmg*100:.2f}%\n" \
            f"critdef: {self.critdef*100:.2f}%\n" \
            f"penetration: {self.penetration*100:.2f}%\n" \
            f"heal efficiency: {self.heal_efficiency*100:.2f}%\n" \
            f"final damage taken: {self.final_damage_taken_multipler*100:.2f}%\n"

    def get_rune_stats(self):
        str = ""
        for rune in self.equip:
            str += rune.print_stats()
            str += "="*15 + "\n"
        return str

    # Calculate the max exp for the character
    def calculate_maxexp(self):
        if self.lvl <= 300:
            return self.lvl * 100
        else:
            scaling_factor = (self.lvl - 300) * 0.05  
            return int(100 * self.lvl * (1 + scaling_factor))

    # Level up the character
    def level_up(self):
        self.lvl += 1
        self.reset_stats()
        self.calculate_equip_effect()
        self.exp = 0
        self.maxexp = self.calculate_maxexp()

    # Level down the character
    def level_down(self):
        self.lvl -= 1
        self.reset_stats()
        self.calculate_equip_effect()
        self.exp = 0
        self.maxexp = self.calculate_maxexp()

    # Check if the character is alive
    def isAlive(self):
        return self.hp > 0

    # Check if the character is dead
    def isDead(self):
        return self.hp <= 0

    # Check if charmed
    def isCharmed(self):
        return self.hasEffect("Charm")
    
    # Check if confused
    def isConfused(self):
        return self.hasEffect("Confuse")
    
    # Check if stunned
    def isStunned(self):
        return self.hasEffect("Stun")
    
    # Check if silenced
    def isSilenced(self):
        return self.hasEffect("Silence")
    
    # Check if asleep
    def isAsleep(self):
        return self.hasEffect("Asleep")
    
    # Check if frozen
    def isFrozen(self):
        return self.hasEffect("Frozen")
    
    # Check if can action
    def canAction(self):
        return not self.isStunned() and not self.isAsleep() and not self.isFrozen()
    
    # Update allies and enemies
    def updateAllyEnemy(self):
        self.ally = [ally for ally in self.ally if not ally.isDead()]
        self.enemy = [enemy for enemy in self.enemy if not enemy.isDead()]

    # Calculate targets
    def checkTargets(self):
        if self.isCharmed():
            return self.ally
        elif self.isConfused():
            return self.ally + self.enemy
        else:
            return self.enemy
        
    # Check if have certain ally
    def hasAlly(self, ally_name):
        return ally_name in [ally.name for ally in self.ally]
    
    # Check if have certain enemy
    def hasEnemy(self, enemy_name):
        return enemy_name in [enemy.name for enemy in self.enemy]

    def get_neighbor_allies_including_self(self):
        return get_neighbors(self.ally, self)

    def get_neighbor_allies_not_including_self(self):
        return get_neighbors(self.ally, self, include_self=False)

    # Check if the character is the only one alive
    def isOnlyOneAlive(self):
        return len(self.ally) == 1
    
    # Check if the character is the only one dead
    def isOnlyOneDead(self):
        return len(self.enemy) == 1
    
    # Update the character's spd, flat or multiplicative
    def updateSpd(self, value, is_flat):
        if is_flat:
            self.spd += value
            self.spd = int(self.spd)
            if self.spd < 0:
                self.spd = 0
        else:
            self.spd *= value
            self.spd = int(self.spd)
            if self.spd < 0:
                self.spd = 0
 
    # Update the character's atk, flat or multiplicative
    def updateAtk(self, value, is_flat):
        if is_flat:
            self.atk += value
            self.atk = int(self.atk)
            if self.atk < 0:
                self.atk = 0
        else:
            self.atk *= value
            self.atk = int(self.atk)
            if self.atk < 0:
                self.atk = 0

    # Update the character's def, flat or multiplicative
    def updateDef(self, value, is_flat):
        if is_flat:
            self.defense += value
            self.defense = int(self.defense)
            if self.defense < 0:
                self.defense = 0
        else:
            self.defense *= value
            self.defense = int(self.defense)
            if self.defense < 0:
                self.defense = 0

    # Update the character's eva, flat or multiplicative
    def updateEva(self, value, is_flat):
        if is_flat:
            self.eva += value
        else:
            self.eva *= value
    
    # Update the character's acc, flat or multiplicative
    def updateAcc(self, value, is_flat):
        if is_flat:
            self.acc += value
        else:
            self.acc *= value
    
    # Update the character's crit, flat or multiplicative
    def updateCrit(self, value, is_flat):
        if is_flat:
            self.crit += value
        else:
            self.crit *= value
    
    # Update the character's critdmg, flat or multiplicative
    def updateCritdmg(self, value, is_flat):
        if is_flat:
            self.critdmg += value
        else:
            self.critdmg *= value

    # Update the character's critdef, flat or multiplicative
    def updateCritdef(self, value, is_flat):
        if is_flat:
            self.critdef += value
        else:
            self.critdef *= value

    # Update the character's penetration, flat or multiplicative
    def updatePenetration(self, value, is_flat):
        if is_flat:
            self.penetration += value
        else:
            self.penetration *= value

    # Update the character's hp, flat
    def updateHp(self, value):
        self.hp += value
        self.hp = int(self.hp)
        if self.hp < 0:
            self.hp = 0
        if self.hp > self.maxhp:
            self.hp = self.maxhp

    # Heal the character hp, flat, independent of updateHp
    def healHp(self, value, healer):
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        healing = value * self.heal_efficiency
        healing = int(healing)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        self.hp += healing
        if running:
            text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
        print(f"{self.name} is healed for {healing} HP.")
        return healing, healer, overhealing

    # Update the character's maxhp, flat or multiplicative
    def updateMaxhp(self, value, is_flat):
        if is_flat:
            self.maxhp += value
            self.maxhp = int(self.maxhp)
            if self.maxhp < 0:
                self.maxhp = 0
        else:
            self.maxhp *= value
            self.maxhp = int(self.maxhp)
            if self.maxhp < 0:
                self.maxhp = 0

    # Update the character's mp, flat
    def updateMp(self, value):
        self.mp += value
        self.mp = int(self.mp)
        if self.mp < 0:
            self.mp = 0
        if self.mp > self.maxmp:
            self.mp = self.maxmp
    
    # Heal the character mp, flat, independent of updateMp
    def healMp(self, value, healer):
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        healing = value * self.heal_efficiency
        healing = int(healing)
        overhealing = 0
        if self.mp + healing > self.maxmp:
            overhealing = self.mp + healing - self.maxmp
            healing = self.maxmp - self.mp
        self.mp += healing
        return healing, healer, overhealing

    # Update the character's maxmp, flat or multiplicative
    def updateMaxmp(self, value, is_flat):
        if is_flat:
            self.maxmp += value
            self.maxmp = int(self.maxmp)
            if self.maxmp < 0:
                self.maxmp = 0
        else:
            self.maxmp *= value
            self.maxmp = int(self.maxmp)
            if self.maxmp < 0:
                self.maxmp = 0

    # Update the character's hpregen, flat or multiplicative
    def updateHpregen(self, value, is_flat):
        if is_flat:
            self.hpregen += value
        else:
            self.hpregen *= value

    # Update the character's mpregen, flat or multiplicative
    def updateMpregen(self, value, is_flat):
        if is_flat:
            self.mpregen += value
        else:
            self.mpregen *= value
    
    # Heal from regen. This is not a flat heal, but a heal that is based on the character's regen and maxhp/mp
    def regen(self):
        if self.isDead():
            raise Exception
        healing = int(self.maxhp * self.hpregen)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        self.hp += healing
        if healing > 0:
            if running:
                text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
            print(f"{self.name} is regenerated for {healing} HP.")
        return healing, self, overhealing

    # Update the character's hpdrain, flat or multiplicative
    def updateHpdrain(self, value, is_flat):
        if is_flat:
            self.hpdrain += value
        else:
            self.hpdrain *= value

    # Update the character's thorn, flat or multiplicative
    def updateThorn(self, value, is_flat):
        if is_flat:
            self.thorn += value
        else:
            self.thorn *= value

    # Update the character's heal efficiency, flat or multiplicative
    def updateHeal_efficiency(self, value, is_flat):
        if is_flat:
            self.heal_efficiency += value
        else:
            self.heal_efficiency *= value

    # Update the character's final damage reduction, flat or multiplicative
    def updateDamage_reduction(self, value, is_flat):
        if is_flat:
            self.final_damage_taken_multipler += value
        else:
            self.final_damage_taken_multipler *= value

    # Take skill or normal attack damage, flat.
    def takeDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} damage.\n")
        print(f"{self.name} is about to take {value} damage.")
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            for effect in self.buffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
            for effect in self.debuffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
        damage = int(damage)
        if damage < 0:
            damage = 0
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if running:
            text_box.append_html_text(f"{self.name} took {damage} damage.\n")
        print(f"{self.name} took {damage} damage.")
        return damage, attacker
    
    # Take status damage, flat.
    def takeStatusDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} status damage.\n")
        print(f"{self.name} is about to take {value} status damage.")
        if self.isDead():
            return 0, attacker
        if value < 0:
            value = 0
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            for effect in self.buffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
            for effect in self.debuffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
        damage = int(damage)
        if damage < 0:
            damage = 0
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if running:
            text_box.append_html_text(f"{self.name} took {damage} status damage.\n")
        print(f"{self.name} took {damage} status damage.")
        return damage, attacker

    # Take bypass all damage, flat.
    def takeBypassAllDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} bypass all damage.\n")
        print(f"{self.name} is about to take {value} bypass all damage.")
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        damage = value
        damage = int(damage)
        if self.hp - damage < 0:
            damage = self.hp
        if damage < 0:
            raise Exception("damage cannot be negative.")
        self.hp -= damage
        if running:
            text_box.append_html_text(f"{self.name} took {damage} bypass all damage.\n")
        print(f"{self.name} took {damage} bypass all damage.")
        return damage, attacker

    # Check if character have certain effect.
    def hasEffect(self, effect_name):
        if type(effect_name) != str:
            raise Exception("effect_name must be a string.")
        for effect in self.buffs:
            if effect.name == effect_name:
                return True
        for effect in self.debuffs:
            if effect.name == effect_name:
                return True
        return False

    # Check if character have CC immunity.
    def hasCCImmunity(self):
        for effect in self.buffs:
            if effect.cc_immunity:
                return True
        for effect in self.debuffs:
            if effect.cc_immunity:
                return True
        return False

    # Apply buff or debuff effect to the character
    def applyEffect(self, effect):
        if self.isAlive() and effect.is_buff:
            self.buffs.append(effect)
        elif self.isAlive() and not effect.is_buff:
            # Check if self has CC immunity
            if effect.name in ["Stun", "Confuse", "Charm", "Silence", "Asleep", "Frozen"]:
                if self.hasCCImmunity():
                    if running:
                        text_box.append_html_text(f"{self.name} is immune to {effect.name}.\n")
                    print(f"{self.name} is immune to {effect.name}.")
                    return
            self.debuffs.append(effect)
        if running:
            text_box.append_html_text(f"{effect.name} has been applied on {self.name}.\n")
        print(f"{effect.name} has been applied on {self.name}.")
        effect.applyEffectOnApply(self)

    # Remove buff or debuff effect from the character
    def removeEffect(self, effect):
        if effect in self.buffs:
            self.buffs.remove(effect)
        elif effect in self.debuffs:
            self.debuffs.remove(effect)
        if running:
            text_box.append_html_text(f"{effect.name} on {self.name} has been removed.\n")
        print(f"{effect.name} on {self.name} has been removed.")
        effect.applyEffectOnRemove(self)

    # Remove all buffs and debuffs from the character
    def removeAllEffects(self):
        for effect in self.buffs:
            effect.applyEffectOnRemove(self)
        for effect in self.debuffs:
            effect.applyEffectOnRemove(self)
        self.buffs = []
        self.debuffs = []

    # Remove set amount buffs effect randomly from the character and return the list of removed effects
    def removeRandomBuffs(self, amount):
        if amount > len(self.buffs):
            amount = len(self.buffs)
        if amount == 0:
            return []
        removed_effects = []
        for i in range(amount):
            effect = random.choice(self.buffs)
            self.removeEffect(effect)
            removed_effects.append(effect)
        return removed_effects

    # Remove set amount debuffs effect randomly from the character and return the list of removed effects
    def removeRandomDebuffs(self, amount):
        if amount > len(self.debuffs):
            amount = len(self.debuffs)
        if amount == 0:
            return []
        removed_effects = []
        for i in range(amount):
            effect = random.choice(self.debuffs)
            self.removeEffect(effect)
            removed_effects.append(effect)
        return removed_effects

    # Every turn, decrease the duration of all buffs and debuffs by 1. If the duration is 0, remove the effect.
    def updateEffects(self):
        for effect in self.buffs:
            effect.decreaseDuration()
            if effect.duration == -1:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                print(f"{effect.name} on {self.name} is active.")
            if effect.duration > 0:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                print(f"{effect.name} on {self.name} has {effect.duration} turns left.")
            if effect.isExpired():
                self.removeEffect(effect)
                effect.applyEffectOnExpire(self)
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                print(f"{effect.name} on {self.name} has expired.")
        for effect in self.debuffs:
            if effect.duration == -1:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                print(f"{effect.name} on {self.name} is active.")
            effect.decreaseDuration()
            if effect.duration > 0:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                print(f"{effect.name} on {self.name} has {effect.duration} turns left.")
            if effect.isExpired():
                self.removeEffect(effect)
                effect.applyEffectOnExpire(self)
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                print(f"{effect.name} on {self.name} has expired.")
    
    # Every turn, calculate applyEffectOnTurn effect of all buffs and debuffs. ie. poison, burn, etc.
    def statusEffects(self):
        for effect in self.buffs:
            effect.applyEffectOnTurn(self)
        for effect in self.debuffs:
            effect.applyEffectOnTurn(self)

    def skill_tooltip(self):
        return ""


# Target winrate : less then 60%
class Lillia(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lillia"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown
        self.skill1_description = "12 hits on random enemies, 170% atk each hit. After 1 critical hit, all hits following will be critical and attack all enemies."
        self.skill2_description = "For 8 turns, cast Infinite Oasis on self gain immunity to CC and reduce damage taken by 35%."
        self.skill3_description = "Heal 10% of max hp on action when Infinite Oasis is active."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 12 hits on random enemies, 170% atk each hit.
        # After 1 critical hit, all hits following will be critical and attack all enemies.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        have_critical = False
        if self.skill1_cooldown > 0:
            raise Exception
        for i in range (12):
            self.updateAllyEnemy()
            available_targets = self.checkTargets()
            if len(available_targets) == 0:
                if running:
                    text_box.append_html_text("No available targets.\n")
                print("No available targets.")
                break
            if not have_critical:
                target = random.choice(available_targets)
                if running:
                    text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
                print(f"{self.name} is targeting {target.name}.")
                damage = self.atk * 1.7 - target.defense * (1-self.penetration)
                final_accuracy = self.acc - target.eva
                dice = random.randint(1, 100)
                miss = False if dice <= final_accuracy * 100 else True
                if not miss:
                    dice = random.randint(1, 100)
                    critical = True if dice <= self.crit * 100 else False
                    if critical:
                        final_damage = damage * (self.critdmg - target.critdef)
                        if running:
                            text_box.append_html_text("Critical!\n")
                        print("Critical!")
                        have_critical = True
                    else:
                        final_damage = damage
                    final_damage *= random.uniform(0.8, 1.2)
                    if final_damage < 0:
                        final_damage = 0
                    target.takeDamage(final_damage, self)
                else:
                    if running:
                        text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                    print(f"Missed! {self.name} attacked {target.name} but missed.")              

            else:
                for target in available_targets:
                    if running:
                        text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
                    print(f"{self.name} is targeting {target.name}.")
                    damage = self.atk * 1.8 - target.defense * (1-self.penetration)
                    final_accuracy = self.acc - target.eva
                    dice = random.randint(1, 100)
                    miss = False if dice <= final_accuracy * 100 else True
                    if not miss:
                        critical = True
                        final_damage = damage * (self.critdmg - target.critdef)
                        if running:
                            text_box.append_html_text("Critical!\n")
                        print("Critical!")
                        final_damage *= random.uniform(0.8, 1.2)
                        if final_damage < 0:
                            final_damage = 0
                        target.takeDamage(final_damage, self)
                    else:
                        if running:
                            text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                        print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.skill1_cooldown = 5

    def skill2(self):
        # For 8 turns, gain immunity to CC and reduce damage taken by 35%.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        self.applyEffect(ReductionShield("Infinite Oasis", 8, True, 0.35, cc_immunity=True))
        self.skill2_cooldown = 5

    def skill3(self):
        # Heal 10% of max hp on action turn when "Infinite Oasis" is active.
        if self.hasEffect("Infinite Oasis"):
            self.healHp(self.maxhp * 0.1, self)


    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        self.skill3()
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Poppy(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Poppy"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "8 hits on random enemies, 300% atk each hit."
        self.skill2_description = "620% atk on random enemy. Target speed is decreased by 30% for 6 turns."
        self.skill3_description = "On taking normal attack or skill damage, 30% chance to apply bleeding to attacker for 3 turns. Bleeding: 50% atk damage per turn."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 8 hits on random enemies, 300% atk each hit.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        for i in range (8):
            self.updateAllyEnemy()
            available_targets = self.checkTargets()
            if len(available_targets) == 0:
                if running:
                    text_box.append_html_text("No available targets.\n")
                print("No available targets.")
                break
            target = random.choice(available_targets)
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")              
        self.skill1_cooldown = 5

    def skill2(self):
        # 620% atk on random enemy. Target speed -30% for 6 turns.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 6.2 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
            target.applyEffect(SpeedEffect("Speed Down", 5, False, 0.7, False))
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")
        self.skill2_cooldown = 5
        

    def skill3(self):
        # When take normal attack or skill damage, 30% chance to apply bleeding to attacker for 3 turns.
        # Bleeding: 50% atk damage per turn.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")

    def takeDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} damage.\n")
        print(f"{self.name} is about to take {value} damage.")
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            for effect in self.buffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
            for effect in self.debuffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
        damage = int(damage)
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        dice = random.randint(1, 100)
        if dice <= 30:
            attacker.applyEffect(BleedEffect("Bleed", 3, False, self.atk * 0.5))
        if running:
            text_box.append_html_text(f"{self.name} took {damage} damage.\n")
        print(f"{self.name} took {damage} damage.")
        return damage, attacker


# Target winrate : more than 40%
class Iris(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "330% atk on all enemies."
        self.skill2_description = "350% atk on all enemies, inflict bleed for 3 turns. Bleed: 35% atk damage per turn."
        self.skill3_description = "At start of battle, apply Cancelation Shield to ally with highest atk. Cancelation shield: cancel 1 attack if attack damage exceed 10% of max hp. When cancelation shield is active, gain immunity to CC."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1(self):
        # 330% atk on all enemies.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        for target in available_targets:       
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.3 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")              
        self.skill1_cooldown = 5

    def skill2(self):
        # 350% atk on all enemies, inflict bleed for 3 turns. Bleed: 35% atk damage per turn.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        for target in available_targets:
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.5 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
                target.applyEffect(BleedEffect("Bleed", 3, False, self.atk * 0.35))
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")
        self.skill2_cooldown = 5

    def skill3(self):
        # At start of battle, apply cancelation shield to ally with highest atk.
        # Cancelation shield: cancel 1 attack if attack damage exceed 10% of max hp.
        # When cancelation shield is active, gain immunity to CC.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Freya(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "580% atk on 1 enemy, 60% chance to silence for 3 turns, always target the enemy with highest ATK."
        self.skill2_description = "480% atk on 1 enemy, always target the enemy with lowest HP."
        self.skill3_description = "Apply Absorption Shield on self if target is fallen by skill 2. Shield will absorb up to 900% of ATK of damage."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 580% atk on 1 enemy, 60% chance to silence for 3 turns, always target the enemy with highest ATK.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        # highest atk target in available_targets
        target = available_targets[0]
        for t in available_targets:
            if t.atk > target.atk:
                target = t
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 5.8 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
            dice2 = random.randint(1, 100)
            if dice2 <= 60:
                target.applyEffect(Effect("Silence", 3, False))
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.skill1_cooldown = 5

    def skill2(self):
        # 480% atk on 1 enemy, always target the enemy with lowest HP. Apply Shield on self if target is fallen. Shield will absorb up to 900% of ATK of damage.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        target = available_targets[0]
        for t in available_targets:
            if t.hp < target.hp:
                target = t
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 4.8 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
            if target.hp <= 0:
                self.applyEffect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 9, cc_immunity=False))
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.skill2_cooldown = 5

    def skill3(self):
        # No effect 
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Luna(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Luna"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "Attack all targets with 300% atk, recover 10% of damage dealt as hp."
        self.skill2_description = "Attack all targets with 300% atk, apply Moonlight on self for next 3 turns, reduce damage taken by 90%."
        self.skill3_description = "Recover 8% hp of maxhp at start of action."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # attack all targets with 300% atk, recover 10% of damage dealt as hp.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        for target in available_targets:
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                damage_dealt, attacker = target.takeDamage(final_damage, self)
                self.healHp(damage_dealt * 0.1, self)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.skill1_cooldown = 5

    def skill2(self):
        # Attack all targets with 300% atk, for next 3 turns, reduce damage taken by 90%.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        for target in available_targets:
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.applyEffect(ReductionShield("Moonlight", 3, True, 0.9, cc_immunity=False))
        self.skill2_cooldown = 5

    def skill3(self):
        # Recover 8% hp of maxhp at start of action. 
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.healHp(self.maxhp * 0.08, self)
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Clover(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clover"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "Target 1 ally with lowest hp and 1 random enemy, deal 400% atk damage to enemy and heal ally for 100% of damage dealt."
        self.skill2_description = "Target 1 ally with lowest hp, heal for 330% atk and grant Absorption Shield, absorb damage up to 330% atk."
        self.skill3_description = "Every time an ally is healed by Clover, heal Clover for 40% of that amount."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1(self):
        # target 1 ally with lowest hp and 1 random enemy, deal 400% atk damage to enemy and heal ally for 100% of damage dealt.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        # lowest hp ally in self.ally
        ally_to_heal = self.ally[0]
        for ally in self.ally:
            if ally.hp < ally_to_heal.hp:
                ally_to_heal = ally
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 4.0 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            damage_dealt, attacker = target.takeDamage(final_damage, self)
            healing, x, y = ally_to_heal.healHp(damage_dealt, self)
            self.healHp(healing * 0.6, self)
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")

        self.skill1_cooldown = 5

    def skill2(self):
        # target 1 ally with lowest hp, heal for 330% atk grant AbsorptionShield, absorb damage up to 330% atk.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        self.updateAllyEnemy()
        ally_to_heal = self.ally[0]
        for ally in self.ally:
            if ally.hp < ally_to_heal.hp:
                ally_to_heal = ally
        healing, x, y = ally.healHp(self.atk * 3.3, self)
        self.healHp(healing * 0.6, self)
        ally.applyEffect(AbsorptionShield("Shield", -1, True, self.atk * 3.3, cc_immunity=False))
        self.skill2_cooldown = 5

    def skill3(self):
        # Every time ally is healed by Clover, heal for 60% of that amount.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Ruby(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ruby"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "400% atk on 3 enemies. 70% chance to inflict stun for 3 turns."
        self.skill2_description = "400% atk on 1 enemy for 3 times. Each attack has 80% chance to inflict stun for 3 turns."
        self.skill3_description = "Skill damage is increased by 30% on stunned targets."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 400% atk on 3 enemies. 70% chance to stun for 3 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        if len(available_targets) < 3:
            targets = available_targets
        else:
            targets = random.sample(available_targets, 3)
        for target in targets:
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 4.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                if target.isStunned():
                    final_damage *= 1.3
                target.takeDamage(final_damage, self)
                dice2 = random.randint(1, 100)
                stun = True if dice2 <= 70 else False
                if stun:
                    target.applyEffect(Effect("Stun", 3, False))
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")              
        self.skill1_cooldown = 5

    def skill2(self):
        # 400% atk on 1 enemy for 3 times. 80% chance to stun for 3 turns.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        for i in range(3):
            if target.isDead():
                if running:
                    text_box.append_html_text(f"{target.name} is no longer available.\n")
                print(f"{target.name} is no longer available.")
                break
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 4.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                if target.isStunned():
                    final_damage *= 1.3
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
                dice2 = random.randint(1, 100)
                stun = True if dice2 <= 80 else False
                if stun and not target.isStunned():
                    target.applyEffect(Effect("Stun", 3, False))
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")
        
        self.skill2_cooldown = 5

    def skill3(self):
        # Skill damage is increased by 30% on stunned targets.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : more than 40%
class Olive(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "480% atk on 1 enemy. Decrease target's atk by 50% for 4 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 240% atk and increase their speed by 30% for 4 turns. "
        self.skill3_description = "Normal attack deals 50% more damage if target has less speed than self."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 480% atk on 1 enemy. Decrease target's atk by 50% for 4 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
    
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 4.8 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
            target.applyEffect(AttackEffect("ATK Down", 4, False, 0.5, False))
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")              
        self.skill1_cooldown = 5

    def skill2(self):
        # heal 3 allies by 240% atk with lowest hp and increase their speed by 30% for 4 turns. 
        if self.skill2_cooldown > 0:
            raise Exception
        print(f"{self.name} cast skill 2.")
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        self.updateAllyEnemy()
        ally_to_heal = sorted(self.ally, key=lambda x: x.hp)[:3]
        for ally in ally_to_heal:
            ally.healHp(self.atk * 2.4, self)
            ally.applyEffect(SpeedEffect("Speed Up", 4, True, 1.3, False))

        self.skill2_cooldown = 5

    def skill3(self):
        # Normal attack deals 50% more damage if target has less speed than Olive.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


    def normal_attack(self):
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 2 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            if target.spd < self.spd:
                final_damage *= 1.5
                if running:
                    text_box.append_html_text(f"50% more damage is dealt.\n")
                print(f"50% more damage is dealt.")
            target.takeDamage(final_damage, self)
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")


# Target winrate : less than 60%
class Pepper(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pepper"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown

        self.skill1_description = "3 hits on random enemies, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns."
        self.skill2_description = "350% atk on random enemy. Remove 2 debuffs for neighbor allies."
        self.skill3_description = "Every turn, apply protection to neighbor allies for 1 turn. When the protected ally below 40% hp is about to take damage, heal the ally for 100% atk."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 3 hits on random enemies, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        for i in range (3):
            self.updateAllyEnemy()
            available_targets = self.checkTargets()
            if len(available_targets) == 0:
                if running:
                    text_box.append_html_text("No available targets.\n")
                print("No available targets.")
                break
            target = random.choice(available_targets)
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 2.2 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")

        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            # if ally have this attribute
            if hasattr(ally, "skill1_cooldown") and hasattr(ally, "skill2_cooldown"):
                if ally.skill1_cooldown > 2:
                    ally.skill1_cooldown -= 2
                    if running:
                        text_box.append_html_text(f"{ally.name} skill 1 cooldown reduced by 2.\n")
                    print(f"{ally.name} skill 1 cooldown reduced by 2.")
                if ally.skill2_cooldown > 2:
                    ally.skill2_cooldown -= 2
                    if running:
                        text_box.append_html_text(f"{ally.name} skill 2 cooldown reduced by 2.\n")
                    print(f"{ally.name} skill 2 cooldown reduced by 2.")                 
        self.skill1_cooldown = 5

    def skill2(self):
        # 350% atk on random enemy. Remove 2 debuffs for neighbor allies.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        self.updateAllyEnemy()
        available_targets = self.checkTargets()
        target = random.choice(available_targets)
        if running:
            text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
        print(f"{self.name} is targeting {target.name}.")
        damage = self.atk * 3.5 - target.defense * (1-self.penetration)
        final_accuracy = self.acc - target.eva
        dice = random.randint(1, 100)
        miss = False if dice <= final_accuracy * 100 else True
        if not miss:
            dice = random.randint(1, 100)
            critical = True if dice <= self.crit * 100 else False
            if critical:
                final_damage = damage * (self.critdmg - target.critdef)
                if running:
                    text_box.append_html_text("Critical!\n")
                print("Critical!")
            else:
                final_damage = damage
            final_damage *= random.uniform(0.8, 1.2)
            if final_damage < 0:
                final_damage = 0
            target.takeDamage(final_damage, self)
        else:
            if running:
                text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
            print(f"Missed! {self.name} attacked {target.name} but missed.")

        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.removeRandomDebuffs(2)
        self.skill2_cooldown = 5
        

    def skill3(self):
        # Every turn, apply protection to neighbor allies for 1 turn. When the neighbor ally below 40% hp is about to
        # take damage, heal the ally for 100% atk.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")


# Target winrate : less than 60%
class Cerberus(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, 
                 skill1_cooldown=0, skill2_cooldown=0, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.skill1_cooldown = skill1_cooldown
        self.skill2_cooldown = skill2_cooldown
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 320% atk each hit. Decrease target's def by 10% for each sucessful hit after the attack."
        self.skill2_description = "300% atk on 1 enemy with lowest hp percentage for 3 times. If target hp is less then 15% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 3%, heal 30% of maxhp and increase atk and critdmg by 30%."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill1(self):
        # 5 hits on random enemies, 320% atk each hit. Decrease target's def by 10% for each sucessful hit after the attack.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        effect_count = 0
        for i in range (5):
            self.updateAllyEnemy()
            available_targets = self.checkTargets()
            if len(available_targets) == 0:
                if running:
                    text_box.append_html_text("No available targets.\n")
                print("No available targets.")
                break
            target = random.choice(available_targets)
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.2 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
                effect_count += 1
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")
        if effect_count > 0:
            target.applyEffect(DefenseEffect("Defence Down", 5, False, (1 - 0.1 * effect_count), False))              
        self.skill1_cooldown = 5

    def skill2(self):
        # 300% atk on 1 enemy with lowest hp percentage for 3 times. 
        # If target hp is less then 15% during the attack, execute the target.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        available_targets = self.checkTargets()
        target = available_targets[0]
        for enemy in available_targets:
            if enemy.hp / enemy.maxhp < target.hp / target.maxhp:
                target = enemy
        for i in range(3):
            if target.isDead():
                if running:
                    text_box.append_html_text(f"{target.name} is no longer available.\n")
                print(f"{target.name} is no longer available.")
                break
            if running:
                text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
            print(f"{self.name} is targeting {target.name}.")
            damage = self.atk * 3.0 - target.defense * (1-self.penetration)
            final_accuracy = self.acc - target.eva
            dice = random.randint(1, 100)
            miss = False if dice <= final_accuracy * 100 else True
            if not miss:
                dice = random.randint(1, 100)
                critical = True if dice <= self.crit * 100 else False
                if critical:
                    final_damage = damage * (self.critdmg - target.critdef)
                    if running:
                        text_box.append_html_text("Critical!\n")
                    print("Critical!")
                else:
                    final_damage = damage
                final_damage *= random.uniform(0.8, 1.2)
                if final_damage < 0:
                    final_damage = 0
                target.takeDamage(final_damage, self)
                if target.hp < target.maxhp * self.execution_threshold and not target.isDead():
                    target.takeBypassAllDamage(target.hp, self)
                    if running:
                        text_box.append_html_text(f"Biribiri! {target.name} is executed by {self.name}.\n")
                    print(f"Biribiri! {target.name} is executed by {self.name}.")
                    self.execution_threshold += 0.03
                    self.healHp(self.maxhp * 0.3, self)
                    self.updateAtk(1.3, False)
                    self.updateCritdmg(0.3, True)
            else:
                if running:
                    text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                print(f"Missed! {self.name} attacked {target.name} but missed.")
        self.skill2_cooldown = 5
        

    def skill3(self):
        # On sucessfully executing a target, increase execution threshold by 3%,
        # heal 30% of maxhp and increase atk and critdmg by 30%.
        pass

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")



class Effect:
    # Effect constructor
    def __init__(self, name, duration, is_buff, cc_immunity=False,**kwargs):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
    
    def isPermanent(self):
        return self.duration == -1
    
    def isExpired(self):
        return self.duration == 0
    
    def isNotExpired(self):
        return self.duration > 0
    
    def decreaseDuration(self):
        if self.duration > 0:
            self.duration -= 1
    
    def applyEffectOnApply(self, character):
        pass
    
    def applyEffectOnTurn(self, character):
        pass

    def applyEffectOnExpire(self, character):
        pass
    
    def applyEffectOnRemove(self, character):
        pass

    def applyEffectDuringDamageStep(self, character, damage):
        return damage

    def __str__(self):
        return self.name
    

# Some common effects
# ---------------------------------------------------------
# Speed effect
class SpeedEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateSpd(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateSpd(-self.value, self.is_flat)
        else:
            character.updateSpd(1/self.value, self.is_flat)

# ---------------------------------------------------------
# Attack effect
class AttackEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateAtk(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateAtk(-self.value, self.is_flat)
        else:
            character.updateAtk(1/self.value, self.is_flat)

# ---------------------------------------------------------
# Defense effect
class DefenseEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateDef(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateDef(-self.value, self.is_flat)
        else:
            character.updateDef(1/self.value, self.is_flat)


# ---------------------------------------------------------
# Bleed effect
class BleedEffect(Effect):
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
    
    def applyEffectOnTurn(self, character):
        print(f"{character.name} is bleeding for {self.value} damage!")
        character.takeStatusDamage(self.value, self)
    

#---------------------------------------------------------
# Absorption Shield effect
class AbsorptionShield(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            if running:
                text_box.append_html_text(f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n")
            print(f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.")
            character.removeEffect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            if running:
                text_box.append_html_text(f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n")
            print(f"{character.name}'s shield absorbs {damage} damage. Remaining shield: {self.shield_value}")
            return 0

#---------------------------------------------------------
# Reduction Shield effect (reduces damage taken by a certain percentage)
class ReductionShield(Effect):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        damage = damage * (1 - self.effect_value)
        return damage


#---------------------------------------------------------
# Effect shield 1 (before damage calculation, if character hp is below certain threshold, healhp for certain amount)
class EffectShield1(Effect):
    def __init__(self, name, duration, is_buff, threshold, heal_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.heal_value = heal_value
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if character.hp < character.maxhp * self.threshold:
            character.healHp(self.heal_value, self)
        return damage

#---------------------------------------------------------
# Cancelation Shield effect (cancel 1 attack if attack damage exceed certain amount of max hp)
class CancelationShield(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > character.maxhp * self.threshold:
            character.removeEffect(self)
            if running:
                text_box.append_html_text(f"{character.name} shielded the attack!\n")
            print(f"{character.name} shielded the attack!")
            return 0
        else:
            return damage


#---------------------------------------------------------
def is_someone_alive(party):
    for character in party:
        if character.isAlive():
            return True
    return False

def get_neighbors(party, char, include_self=True):
    if char in party:
        index = party.index(char)
        neighbors = []
        if index != 0:  # If it's not the first character
            neighbors.append(party[index - 1])
        if include_self:
            neighbors.append(char)
        if index != len(party) - 1:  # If it's not the last character
            neighbors.append(party[index + 1])
        return neighbors
    else:
        raise ValueError

# Check if certain character is in party, if so, return get_neighbors(party, char)
def get_neighbors_of_character_in_party(party, char_name, include_self=True, require_character_for_search_to_be_alive=False):
    for character in party:
        if character.name == char_name:
            if require_character_for_search_to_be_alive:
                if character.isAlive():
                    return get_neighbors(party, character, include_self)
                else:
                    return []
            else:
                return get_neighbors(party, character, include_self)
    return []


def set_up_characters():
    character_selection_menu.rebuild()
    party1 = []
    party2 = []
    character1 = Cerberus("Cerberus", 40)
    character2 = Pepper("Pepper", 40)
    character3 = Clover("Clover", 40)
    character4 = Ruby("Ruby", 40)
    character5 = Olive("Olive", 40)
    character6 = Luna("Luna", 40)
    character7 = Freya("Freya", 40)
    character8 = Poppy("Poppy", 40)
    character9 = Lillia("Lillia", 40)
    character10 = Iris("Iris", 40)

    all_characters = [character1, character2, character3, character4, character5,
                        character6, character7, character8, character9, character10,
                          ]
    
    list_of_characters = random.sample(all_characters, 10)

    for character in list_of_characters:
        level = 40
        character.__init__(character.name, level, generate_runes_list(4))
        character.equip = generate_runes_list(4)
        character.calculate_equip_effect()

    party1 = random.sample(list_of_characters, 5)
    remaining = []
    for character in list_of_characters:
        if character not in party1:
            remaining.append(character)
    party2 = random.sample(remaining, 5)
    start_of_battle_effects(party1)
    start_of_battle_effects(party2)

    character_selection_menu.options_list = []
    character_selection_menu_list = [character.name for character in party1] + [character.name for character in party2]
    character_selection_menu.add_options(character_selection_menu_list)
    character_selection_menu.selected_option = character_selection_menu_list[0]

    redraw_ui(party1, party2)

    for characters in party1:
        # party member will be removed by updateAllyEnemy() if no copy.copy() is used.
        characters.ally = copy.copy(party1)
        characters.enemy = copy.copy(party2)
    for characters in party2:
        characters.ally = copy.copy(party2)
        characters.enemy = copy.copy(party1)

    return party1, party2


def mid_turn_effects(party1, party2):
    for party in [party1, party2]:
        characters_to_apply_effects = get_neighbors_of_character_in_party(party, "Pepper", include_self=False, require_character_for_search_to_be_alive=True)
        if characters_to_apply_effects != []:
            # get atk atr of pepper
            for character in party:
                if character.name == "Pepper":
                    atk = character.atk
            for character in characters_to_apply_effects:
                character.applyEffect(EffectShield1("Protection", 1, True, 0.4, atk, False))


def next_turn(party1, party2):
    if not is_someone_alive(party1) or not is_someone_alive(party2):
        text_box.append_html_text("Battle is over.\n")
        return False
    text_box.append_html_text("=====================================\n")
    text_box.append_html_text(f"Turn {turn}\n")
    for character in party1:
        character.updateEffects()
    for character in party2:
        character.updateEffects()
    if not is_someone_alive(party1) or not is_someone_alive(party2):
        return False
    
    for character in party1:
        character.statusEffects()
        if character.isAlive():
            character.regen()
    for character in party2:
        character.statusEffects()
        if character.isAlive():
            character.regen()

    for character in party1:
        character.updateAllyEnemy()
    for character in party2:
        character.updateAllyEnemy()

    mid_turn_effects(party1, party2)

    if not is_someone_alive(party1) or not is_someone_alive(party2):
        return False
    alive_characters = [x for x in party1 + party2 if x.isAlive()]
    weight = [x.spd for x in alive_characters]
    the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
    text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
    the_chosen_one.action()
    for i, character in enumerate(party1):
        sprite_party1[i].current_health = character.hp
        sprite_party1[i].health_capacity = character.maxhp
        image_slots_party1[i].set_tooltip(character.tooltip_string())
        label_party1[i].set_tooltip(character.skill_tooltip())
    for i, character in enumerate(party2):
        sprite_party2[i].current_health = character.hp
        sprite_party2[i].health_capacity = character.maxhp
        image_slots_party2[i].set_tooltip(character.tooltip_string())
        label_party2[i].set_tooltip(character.skill_tooltip())
    if not is_someone_alive(party1) or not is_someone_alive(party2):
        return False
    return True


def all_turns(party1, party2):
    global turn
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        text_box.set_text("Welcome to the battle simulator!\n")
        text_box.append_html_text("=====================================\n")
        text_box.append_html_text(f"Turn {turn}\n")
        for character in party1:
            character.updateEffects()
        for character in party2:
            character.updateEffects()
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            break
        for character in party1:
            character.statusEffects()
            if character.isAlive():
                character.regen()
        for character in party2:
            character.statusEffects()
            if character.isAlive():
                character.regen()

        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()
        
        mid_turn_effects(party1, party2)

        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
        the_chosen_one.action()
        turn += 1

    for i, character in enumerate(party1):
        sprite_party1[i].current_health = character.hp
        sprite_party1[i].health_capacity = character.maxhp
        image_slots_party1[i].set_tooltip(character.tooltip_string())
        label_party1[i].set_tooltip(character.skill_tooltip())
    for i, character in enumerate(party2):
        sprite_party2[i].current_health = character.hp
        sprite_party2[i].health_capacity = character.maxhp
        image_slots_party2[i].set_tooltip(character.tooltip_string())
        label_party2[i].set_tooltip(character.skill_tooltip())

    if turn >= 300:
        text_box.append_html_text("Battle is taking too long.\n")
    elif not is_someone_alive(party1) and not is_someone_alive(party2):
        text_box.append_html_text("Both parties are defeated.\n")
    elif not is_someone_alive(party1):
        text_box.append_html_text("Party 1 is defeated.\n")
    elif not is_someone_alive(party2):
        text_box.append_html_text("Party 2 is defeated.\n")


def start_of_battle_effects(party):
    # If Iris in party, apply Cancelation shield to ally with highest atk.
    # character.applyEffect(CancelationShield("Cancelation Shield", -1, True, 0.1, cc_immunity=True))
    if any(isinstance(character, Iris) for character in party):
        highest_atk = max([character.atk for character in party])
        for character in party:
            if character.atk == highest_atk:
                character.applyEffect(CancelationShield("Cancelation Shield", -1, True, 0.1, cc_immunity=True))
                

# Used with call by calulate_winrate_for_character()
def simulate_battle_between_party(party1, party2):
    turn = 1
    if party1 == [] or party2 == []:
        print("One of the party is empty.")
        return None
    # party member will be removed by updateAllyEnemy() if no copy.copy() is used.
    for characters in party1:
        characters.ally = copy.copy(party1)
        characters.enemy = copy.copy(party2)
    for characters in party2:
        characters.ally = copy.copy(party2)
        characters.enemy = copy.copy(party1)
    start_of_battle_effects(party1)
    start_of_battle_effects(party2)
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        print("=====================================")
        # turn should be 1 at the start of the battle.
        print(f"Turn {turn}")
        for character in party1:
            character.updateEffects()
        for character in party2:
            character.updateEffects()
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            break
        for character in party1:
            character.statusEffects()
            if character.isAlive():
                character.regen()
        for character in party2:
            character.statusEffects()
            if character.isAlive():
                character.regen()
        
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        mid_turn_effects(party1, party2)

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            break
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        print(f"{the_chosen_one.name}'s turn.")
        the_chosen_one.action()
        print("")
        print("Party 1:")
        for character in party1:
            print(character)
        print("")
        print("Party 2:")
        for character in party2:
            print(character)
        turn += 1
    if turn > 300:
        print("Battle is taking too long.")
        return None
    if is_someone_alive(party1) and not is_someone_alive(party2):
        print("Party 1 win!")
        return party1
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        print("Party 2 win!")
        return party2
    else:
        print("Draw!")
        return None


def calculate_winrate_for_character(sample): 
    character1 = Cerberus("Cerberus", 40)
    character2 = Pepper("Pepper", 40)
    character3 = Clover("Clover", 40)
    character4 = Ruby("Ruby", 40)
    character5 = Olive("Olive", 40)
    character6 = Luna("Luna", 40)
    character7 = Freya("Freya", 40)
    character8 = Lillia("Lillia", 40)
    character9 = Poppy("Poppy", 40)
    character10 = Iris("Iris", 40)

    big_data = []
    all_characters = [character1, character2, character3, character4, character5,
                        character6, character7, character8, character9, character10, 
                        ]
    
    list_of_characters = random.sample(all_characters, 10)

    for i in range(sample):
        for character in list_of_characters:
            character.__init__(character.name, character.lvl, character.equip)
            character.equip = generate_runes_list(4)
            character.calculate_equip_effect()
        party1 = random.sample(list_of_characters, 5)
        remaining = []
        for character in list_of_characters:
            if character not in party1:
                remaining.append(character)
        party2 = random.sample(remaining, 5)

        winner_party = simulate_battle_between_party(party1, party2)
        if winner_party != None:
            big_data.append(winner_party)
    win_counts = {c.name: 0 for c in list_of_characters}
    for party in big_data:
        for character in party:
            win_counts[character.name] += 1
    print("=====================================")
    print("Winrate:")
    for character in list_of_characters:
        winrate = win_counts[character.name] / sample * 100
        print(f"{character.name} winrate: {winrate:.2f}%")


pygame.init()
clock = pygame.time.Clock()

# Some colors
AntiqueWhite = pygame.Color("#FAEBD7")
Deep_Dark_Blue = pygame.Color("#000022")
light_yellow = pygame.Color("#FFFFE0")

# Create a display surface
display_surface = pygame.display.set_mode((1200, 900))

# Create an instance of the Pygame GUI UIManager
ui_manager = pygame_gui.UIManager((1200, 900), "theme_light_yellow.json")

# Game title
pygame.display.set_caption("Battle Simulator")

# Some Invisible Sprites
# =====================================

class InvisibleSprite(pygame.sprite.Sprite):
    def __init__(self, color, width, height, health_capacity, current_health):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.health_capacity = health_capacity
        self.current_health = current_health

    def update(self):
        pass

invisible_sprite1 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite2 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite3 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite4 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite5 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite6 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite7 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite8 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite9 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
invisible_sprite10 = InvisibleSprite(Deep_Dark_Blue, 1200, 900, 1000, 100)
sprite_party1 = [invisible_sprite1, invisible_sprite2, invisible_sprite3, invisible_sprite4, invisible_sprite5]
sprite_party2 = [invisible_sprite6, invisible_sprite7, invisible_sprite8, invisible_sprite9, invisible_sprite10]

all_sprites = pygame.sprite.Group()

health_bar1 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 220), (200, 30)),ui_manager,
                                                        invisible_sprite1)
health_bar2 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 220), (200, 30)),ui_manager,
                                                        invisible_sprite2)
health_bar3 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 220), (200, 30)),ui_manager,
                                                        invisible_sprite3)
health_bar4 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 220), (200, 30)),ui_manager,
                                                        invisible_sprite4)
health_bar5 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 220), (200, 30)),ui_manager,
                                                        invisible_sprite5)
health_bar6 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 825), (200, 30)),ui_manager,
                                                        invisible_sprite6)
health_bar7 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 825), (200, 30)),ui_manager,
                                                        invisible_sprite7)
health_bar8 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 825), (200, 30)),ui_manager,
                                                        invisible_sprite8)
health_bar9 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 825), (200, 30)),ui_manager,
                                                        invisible_sprite9)
health_bar10 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 825), (200, 30)),ui_manager,
                                                        invisible_sprite10)

all_healthbar = [health_bar1, health_bar2, health_bar3, health_bar4, health_bar5,
                    health_bar6, health_bar7, health_bar8, health_bar9, health_bar10]

# Some Images
# ==============================

image_files = ["dog", "cat", "rat", "pig", "chicken", "cow", "horse", "sheep", "goat", "duck", "do_not_use"
               ,"lillia", "amethyst", "poppy", "iris", "freya", "luna", "clover", "ruby", "olive", "pepper"
               , "cerberus"]
images = {name: pygame.image.load(f"image/{name}.jpg") for name in image_files}


image_slot1 = pygame_gui.elements.UIImage(pygame.Rect((100, 50), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot2 = pygame_gui.elements.UIImage(pygame.Rect((300, 50), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot3 = pygame_gui.elements.UIImage(pygame.Rect((500, 50), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot4 = pygame_gui.elements.UIImage(pygame.Rect((700, 50), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot5 = pygame_gui.elements.UIImage(pygame.Rect((900, 50), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot6 = pygame_gui.elements.UIImage(pygame.Rect((100, 650), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot7 = pygame_gui.elements.UIImage(pygame.Rect((300, 650), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot8 = pygame_gui.elements.UIImage(pygame.Rect((500, 650), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot9 = pygame_gui.elements.UIImage(pygame.Rect((700, 650), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)
image_slot10 = pygame_gui.elements.UIImage(pygame.Rect((900, 650), (156, 156)),
                                    pygame.Surface((156, 156)),
                                    ui_manager)

image_slots_party1 = [image_slot1, image_slot2, image_slot3, image_slot4, image_slot5]
image_slots_party2 = [image_slot6, image_slot7, image_slot8, image_slot9, image_slot10]

for image_slot in image_slots_party1:
    image_slot.set_image(images["do_not_use"])
for image_slot in image_slots_party2:
    image_slot.set_image(images["do_not_use"])

# Rune Slots
# ==============================

rune_slota1 = pygame_gui.elements.UIImage(pygame.Rect((75, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slota2 = pygame_gui.elements.UIImage(pygame.Rect((75, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slota3 = pygame_gui.elements.UIImage(pygame.Rect((75, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slota4 = pygame_gui.elements.UIImage(pygame.Rect((75, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsb1 = pygame_gui.elements.UIImage(pygame.Rect((275, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsb2 = pygame_gui.elements.UIImage(pygame.Rect((275, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsb3 = pygame_gui.elements.UIImage(pygame.Rect((275, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsb4 = pygame_gui.elements.UIImage(pygame.Rect((275, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsc1 = pygame_gui.elements.UIImage(pygame.Rect((475, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsc2 = pygame_gui.elements.UIImage(pygame.Rect((475, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsc3 = pygame_gui.elements.UIImage(pygame.Rect((475, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsc4 = pygame_gui.elements.UIImage(pygame.Rect((475, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsd1 = pygame_gui.elements.UIImage(pygame.Rect((675, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsd2 = pygame_gui.elements.UIImage(pygame.Rect((675, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsd3 = pygame_gui.elements.UIImage(pygame.Rect((675, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsd4 = pygame_gui.elements.UIImage(pygame.Rect((675, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotse1 = pygame_gui.elements.UIImage(pygame.Rect((875, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotse2 = pygame_gui.elements.UIImage(pygame.Rect((875, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotse3 = pygame_gui.elements.UIImage(pygame.Rect((875, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotse4 = pygame_gui.elements.UIImage(pygame.Rect((875, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsf1 = pygame_gui.elements.UIImage(pygame.Rect((75, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsf2 = pygame_gui.elements.UIImage(pygame.Rect((75, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsf3 = pygame_gui.elements.UIImage(pygame.Rect((75, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsf4 = pygame_gui.elements.UIImage(pygame.Rect((75, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsg1 = pygame_gui.elements.UIImage(pygame.Rect((275, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsg2 = pygame_gui.elements.UIImage(pygame.Rect((275, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsg3 = pygame_gui.elements.UIImage(pygame.Rect((275, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsg4 = pygame_gui.elements.UIImage(pygame.Rect((275, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsh1 = pygame_gui.elements.UIImage(pygame.Rect((475, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsh2 = pygame_gui.elements.UIImage(pygame.Rect((475, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsh3 = pygame_gui.elements.UIImage(pygame.Rect((475, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsh4 = pygame_gui.elements.UIImage(pygame.Rect((475, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsi1 = pygame_gui.elements.UIImage(pygame.Rect((675, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsi2 = pygame_gui.elements.UIImage(pygame.Rect((675, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsi3 = pygame_gui.elements.UIImage(pygame.Rect((675, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsi4 = pygame_gui.elements.UIImage(pygame.Rect((675, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)

rune_slotsj1 = pygame_gui.elements.UIImage(pygame.Rect((875, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsj2 = pygame_gui.elements.UIImage(pygame.Rect((875, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsj3 = pygame_gui.elements.UIImage(pygame.Rect((875, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
# rune_slotsj4 = pygame_gui.elements.UIImage(pygame.Rect((875, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
                                         
rune_slot_party1 = [rune_slota1, rune_slotsb1, rune_slotsc1, rune_slotsd1, rune_slotse1]
rune_slot_party2 = [rune_slotsf1, rune_slotsg1, rune_slotsh1, rune_slotsi1, rune_slotsj1]
for slot in rune_slot_party1:
    slot.set_image(images["amethyst"])      
for slot in rune_slot_party2:
    slot.set_image(images["amethyst"])                                   

# Character Names and Levels
# ==========================

label1 = pygame_gui.elements.UILabel(pygame.Rect((75, 10), (200, 50)),
                                    "label",
                                    ui_manager)

label2 = pygame_gui.elements.UILabel(pygame.Rect((275, 10), (200, 50)),
                                    "label",
                                    ui_manager)

label3 = pygame_gui.elements.UILabel(pygame.Rect((475, 10), (200, 50)),
                                    "label",
                                    ui_manager)

label4 = pygame_gui.elements.UILabel(pygame.Rect((675, 10), (200, 50)),
                                    "label",
                                    ui_manager)

label5 = pygame_gui.elements.UILabel(pygame.Rect((875, 10), (200, 50)),
                                    "label",
                                    ui_manager)

label6 = pygame_gui.elements.UILabel(pygame.Rect((75, 610), (200, 50)),
                                    "label",
                                    ui_manager)

label7 = pygame_gui.elements.UILabel(pygame.Rect((275, 610), (200, 50)),
                                    "label",
                                    ui_manager)

label8 = pygame_gui.elements.UILabel(pygame.Rect((475, 610), (200, 50)),
                                    "label",
                                    ui_manager)

label9 = pygame_gui.elements.UILabel(pygame.Rect((675, 610), (200, 50)),
                                    "label",
                                    ui_manager)

label10 = pygame_gui.elements.UILabel(pygame.Rect((875, 610), (200, 50)),
                                    "label",
                                    ui_manager)

label_party1 = [label1, label2, label3, label4, label5]
label_party2 = [label6, label7, label8, label9, label10]

# Some buttons
# ==========================

button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 50)),
                                      text='Initiate',
                                      manager=ui_manager,
                                      tool_tip_text = "Click to initiate battle")

button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                      text='Next Turn',
                                      manager=ui_manager,
                                      tool_tip_text = "Click to simulate the next turn")

button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                      text='All Turns',
                                      manager=ui_manager,
                                      tool_tip_text = "Click to skip to the end of the battle. May take a while.")

button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                      text='Clear Board',
                                      manager=ui_manager,
                                      tool_tip_text = "Click to clear the board")

button5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                      text='Quit',
                                      manager=ui_manager,
                                      tool_tip_text = "Click to quit the game")

character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                        "Option 1",
                                                        pygame.Rect((900, 300), (156, 35)),
                                                        ui_manager)

reroll_rune_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 340), (156, 35)),
                                      text='Reroll Rune 1',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and reroll rune 1")

reroll_rune_button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 380), (156, 35)),
                                      text='Reroll Rune 2',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and reroll rune 2")

reroll_rune_button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 420), (156, 35)),
                                      text='Reroll Rune 3',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and reroll rune 3")

reroll_rune_button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 460), (156, 35)),
                                      text='Reroll Rune 4',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and reroll rune 4")

levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 515), (156, 35)),
                                      text='Level Up',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and level up")

leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 555), (156, 35)),
                                      text='Level Down',
                                      manager=ui_manager,
                                      tool_tip_text = "Reset stats and level down")

def redraw_ui(party1, party2):
    for i, character in enumerate(party1):
        image_slots_party1[i].set_image(images[character.name.lower()])
        image_slots_party1[i].set_tooltip(character.tooltip_string())
        rune_slot_party1[i].set_tooltip(character.get_rune_stats())
        sprite_party1[i].current_health = character.hp
        sprite_party1[i].health_capacity = character.maxhp
        label_party1[i].set_text(f"lv {character.lvl} {character.name}")
        label_party1[i].set_tooltip(character.skill_tooltip())

    for i, character in enumerate(party2):
        image_slots_party2[i].set_image(images[character.name.lower()])
        image_slots_party2[i].set_tooltip(character.tooltip_string())
        rune_slot_party2[i].set_tooltip(character.get_rune_stats())
        sprite_party2[i].current_health = character.hp
        sprite_party2[i].health_capacity = character.maxhp
        label_party2[i].set_text(f"lv {character.lvl} {character.name}")
        label_party2[i].set_tooltip(character.skill_tooltip())

    for healthbar in all_healthbar:
        healthbar.rebuild()

def reroll_rune(rune_index):
    all_characters = party1 + party2
    for character in all_characters:
        if character.name == character_selection_menu.selected_option:
            print(character.name)
            print(character.equip)
            character.equip[rune_index] = generate_runes_list(1)[0]
            text_box.append_html_text("====================================\n")
            text_box.append_html_text(f"Rerolling rune {rune_index + 1} for {character.name}\n")
            text_box.append_html_text(character.equip[rune_index].print_stats())
            print(character.equip[rune_index])
            character.reset_stats()
            character.calculate_equip_effect()
    redraw_ui(party1, party2)


def levelup_button_effect():
    all_characters = party1 + party2
    for character in all_characters:
        if character.name == character_selection_menu.selected_option:
            character.level_up()
            text_box.append_html_text(f"Leveling up {character.name}, New level: {character.lvl}\n")
    redraw_ui(party1, party2)

def leveldown_button_effect():
    all_characters = party1 + party2
    for character in all_characters:
        if character.name == character_selection_menu.selected_option:
            character.level_down()
            text_box.append_html_text(f"Leveling down {character.name}. New level: {character.lvl}\n")
    redraw_ui(party1, party2)

# Text entry box
# ==========================

text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 290)),
                                                        "", ui_manager)
text_box.set_text("Hover over character name to show skill information\n")
text_box.append_html_text("Hover over character image to show attributes\n")
text_box.append_html_text("Hover over rune icon to show rune information\n\n")
text_box.append_html_text("Click on Initiate to continue...\n")

# Event loop
# ==========================

running = True

party1 = []
party2 = []
turn = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button1:
                text_box.set_text("Welcome to the battle simulator!\n")
                party1, party2 = set_up_characters()
                turn = 1
            if event.ui_element == button2:
                text_box.set_text("Welcome to the battle simulator!\n")
                if next_turn(party1, party2):
                    turn += 1
            if event.ui_element == button3:
                all_turns(party1, party2)
            if event.ui_element == button4:
                text_box.set_text("Welcome to the battle simulator!\n")
            if event.ui_element == button5:
                running = False
            if event.ui_element == reroll_rune_button1:
                reroll_rune(0)
            if event.ui_element == reroll_rune_button2:
                reroll_rune(1)
            if event.ui_element == reroll_rune_button3:
                reroll_rune(2)
            if event.ui_element == reroll_rune_button4:
                reroll_rune(3)
            if event.ui_element == levelup_button:
                levelup_button_effect()
            if event.ui_element == leveldown_button:
                leveldown_button_effect()

        ui_manager.process_events(event)

    ui_manager.update(1/60)
    display_surface.fill(light_yellow)
    all_sprites.draw(display_surface)
    all_sprites.update()
    ui_manager.draw_ui(display_surface)

    pygame.display.update()
    clock.tick(60)

pygame.quit()

# calculate_winrate_for_character(1000)