from battle_simulator import *

# Used with call by calulate_winrate_for_character()
def simulate_battle_between_party(party1, party2):
    turn = 1
    if party1 == [] or party2 == []:
        print("One of the party is empty.")
        return None
    reset_ally_enemy_attr(party1, party2)
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
            character.__init__(character.name, character.lvl, equip=generate_runes_list(4))

        random.shuffle(list_of_characters)
        party1 = list_of_characters[:5]
        party2 = list_of_characters[5:]

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


calculate_winrate_for_character(1)