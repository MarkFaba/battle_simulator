import random


# Normal Distribution with max and min value
def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = int(random.normalvariate(mean, std))
        if value >= min_value and value <= max_value:
            return value

class Equip:
    def __init__(self, name, type, rarity, set="None" ,slot="All"):
        self.name = name
        self.type = type
        self.set = set
        self.rarity = rarity
        self.slot = slot
        self.maxhp_percent = 0.00
        self.atk_percent = 0.00
        self.def_percent = 0.00
        self.spd = 0.00
        self.eva = 0.00
        self.acc = 0.00
        self.crit = 0.00
        self.critdmg = 0.00
        self.critdef = 0.00
        self.penetration = 0.00
        self.heal_efficiency = 0.00
        self.maxhp_flat = 0
        self.atk_flat = 0
        self.def_flat = 0
        self.spd_flat = 0


    def __str__(self):
        return f"{self.name} {self.type} {self.set} {self.rarity} {self.slot} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency}"

    def __repr__(self):
        return f"{self.name} {self.type} {self.set} {self.rarity} {self.slot} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency}"

    def get_nonzero_nonstring_attributes(self):
        return [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and getattr(self, attr) != 0 and not isinstance(getattr(self, attr), str)]

    # Enhance by rarity
    # If rarity is "Common", no effect. If rarity is "Uncommon", all attributes are increased by 10%.
    # If rarity is "Rare", all attributes are increased by 20%. If rarity is "Epic", all attributes are increased by 30%.
    # If rarity is "Unique", all attributes are increased by 40%. IF rarity is "Legendary", all attributes are increased by 50%.
    def enhance_by_rarity(self):
        if self.rarity == "Common":
            pass
        elif self.rarity == "Uncommon":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.10)
        elif self.rarity == "Rare":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.25)
        elif self.rarity == "Epic":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.45)
        elif self.rarity == "Unique":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.70)
        elif self.rarity == "Legendary":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 2.00)
        else:
            raise Exception("Invalid rarity")
        # Convert flat attributes to integer
        self.maxhp_flat = int(self.maxhp_flat)
        self.atk_flat = int(self.atk_flat)
        self.def_flat = int(self.def_flat)
        self.spd_flat = int(self.spd_flat)

    # Fake dice. From 1 to 6, The chances of rolling a higher number decrease progressively
    # The function returns a random number from 1 to 6.

    def fake_dice(self):
        # choices are the six sides of the dice
        sides = [1, 2, 3, 4, 5, 6]
        
        # weights decrease progressively for higher numbers, providing a higher chance of rolling lower numbers
        # these can be any values, as long as they decrease progressively
        weights = [60, 30, 10, 5, 2, 1]
        
        # the random.choices function selects a random element from sides,
        # where the chance of picking each element is defined by the corresponding weight
        return random.choices(sides, weights=weights, k=1)[0]

    def generate(self):
        extra_lines_to_generate = self.fake_dice() - 1
        if self.type == "Rune of Health":
            self.maxhp_flat = normal_distribution(1, 3000, 1000, 500)
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    # randomly choose a non-flat attribute
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    # generate a random value between (0, 0.3) for the attribute
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    # add the value to the attribute
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Rune of Attack":
            self.atk_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Rune of Defense":
            self.def_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Rune of Speed":
            self.spd_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        else:
            raise Exception("Invalid rune type")
        self.enhance_by_rarity()

    # Print the rune's stats. Only print non-zero stats, including type, rarity.
    def print_stats(self):
        stats = self.rarity + " " + self.type + "\n"
        
        if self.maxhp_flat != 0:
            stats += "Max HP: " + str(self.maxhp_flat) + "\n"
        if self.atk_flat != 0:
            stats += "Attack: " + str(self.atk_flat) + "\n"
        if self.def_flat != 0:
            stats += "Defense: " + str(self.def_flat) + "\n"
        if self.spd_flat != 0:
            stats += "Speed: " + str(self.spd_flat) + "\n"
        if self.maxhp_percent != 0:
            stats += "Max HP: " + "{:.2f}%".format(self.maxhp_percent*100) + "\n"
        if self.atk_percent != 0:
            stats += "Attack: " + "{:.2f}%".format(self.atk_percent*100) + "\n"
        if self.def_percent != 0:
            stats += "Defense: " + "{:.2f}%".format(self.def_percent*100) + "\n"
        if self.spd != 0:
            stats += "Speed: " + "{:.2f}%".format(self.spd*100) + "\n"
        if self.eva != 0:
            stats += "Evasion: " + "{:.2f}%".format(self.eva*100) + "\n"
        if self.acc != 0:
            stats += "Accuracy: " + "{:.2f}%".format(self.acc*100) + "\n"
        if self.crit != 0:
            stats += "Critical Chance: " + "{:.2f}%".format(self.crit*100) + "\n"
        if self.critdmg != 0:
            stats += "Critical Damage: " + "{:.2f}%".format(self.critdmg*100) + "\n"
        if self.critdef != 0:
            stats += "Critical Defense: " + "{:.2f}%".format(self.critdef*100) + "\n"
        if self.penetration != 0:
            stats += "Penetration: " + "{:.2f}%".format(self.penetration*100) + "\n"
        if self.heal_efficiency != 0:
            stats += "Heal Efficiency: " + "{:.2f}%".format(self.heal_efficiency*100) + "\n"
        
        return stats

    # Print the rune's stats in HTML format. Only print non-zero stats, including type, rarity.
    def print_stats_html(self):
        color = ""
        if self.rarity == "Common":
            color = "#2c2c2c"
        elif self.rarity == "Uncommon":
            color = "#B87333"
        elif self.rarity == "Rare":
            color = "#FF0000"
        elif self.rarity == "Epic":
            color = "#659a00"
        elif self.rarity == "Unique":
            color = "#9966CC"
        elif self.rarity == "Legendary":
            color = "#21d6ff"
            
        stats = "<font color=" + color + ">" + self.rarity + " " + self.type + "\n"
        if self.maxhp_flat != 0:
            stats += "Max HP: " + str(self.maxhp_flat) + "\n"
        if self.atk_flat != 0:
            stats += "Attack: " + str(self.atk_flat) + "\n"
        if self.def_flat != 0:
            stats += "Defense: " + str(self.def_flat) + "\n"
        if self.spd_flat != 0:
            stats += "Speed: " + str(self.spd_flat) + "\n"
        if self.maxhp_percent != 0:
            stats += "Max HP: " + "{:.2f}%".format(self.maxhp_percent*100) + "\n"
        if self.atk_percent != 0:
            stats += "Attack: " + "{:.2f}%".format(self.atk_percent*100) + "\n"
        if self.def_percent != 0:
            stats += "Defense: " + "{:.2f}%".format(self.def_percent*100) + "\n"
        if self.spd != 0:
            stats += "Speed: " + "{:.2f}%".format(self.spd*100) + "\n"
        if self.eva != 0:
            stats += "Evasion: " + "{:.2f}%".format(self.eva*100) + "\n"
        if self.acc != 0:
            stats += "Accuracy: " + "{:.2f}%".format(self.acc*100) + "\n"
        if self.crit != 0:
            stats += "Critical Chance: " + "{:.2f}%".format(self.crit*100) + "\n"
        if self.critdmg != 0:
            stats += "Critical Damage: " + "{:.2f}%".format(self.critdmg*100) + "\n"
        if self.critdef != 0:
            stats += "Critical Defense: " + "{:.2f}%".format(self.critdef*100) + "\n"
        if self.penetration != 0:
            stats += "Penetration: " + "{:.2f}%".format(self.penetration*100) + "\n"
        if self.heal_efficiency != 0:
            stats += "Heal Efficiency: " + "{:.2f}%".format(self.heal_efficiency*100) + "</font>\n"

        return stats


# Generate and add to a list
def generate_runes_list(num):
    runes = []
    for i in range(num):
        rune = Equip("Rune_" + str(i+1), random.choice(["Rune of Health", "Rune of Attack", "Rune of Defense", "Rune of Speed"]), random.choice(["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]))
        rune.generate()
        runes.append(rune)
    return runes

