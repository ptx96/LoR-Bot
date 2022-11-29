from constants import GameState
from Strategy import Strategy
from time import sleep
import keyboard

class Pirates(Strategy):
    def __init__(self, mouse_handler):
        super().__init__(mouse_handler)
        self.mulligan_cards = ("Crackshot Corsair", "Legion Rearguard",
                               "Legion Saboteur", "Precious Pet", "Prowling Cutthroat")

    def block(self, cards_on_board, window_x, window_y, window_height):
        self.window_x = window_x
        self.window_y = window_y
        self.window_height = window_height

        if any(card_on_board.get_name() == "Powder Keg" for card_on_board in (cards_on_board["cards_board"] + cards_on_board["cards_attk"])):
            for card_in_hand in cards_on_board["cards_hand"]:
                if card_in_hand.get_name() == "Make it Rain":
                    self.play_card(card_in_hand)
                    break

        for i, blocking_card in enumerate(cards_on_board["cards_board"]):
            if i < self.block_counter or "Can't Block" in blocking_card.keywords or "Immobile" in blocking_card.keywords or blocking_card.get_name() == "Crackshot Corsair" or blocking_card.get_name() == "Legion Saboteur":
                continue
            if self.blocked_with(blocking_card, cards_on_board["opponent_cards_attk"], cards_on_board["cards_attk"]):
                self.block_counter = (self.block_counter + 1) % len(cards_on_board["cards_board"])
                return True

        self.block_counter = 0
        return False

    # Generic blocked_with, to be overriden by specific deck strategy
    def blocked_with(self, blocking_card, enemy_cards, ally_cards):
        #n_cards_on_board = len(cards_on_board["cards_board"])
        for enemy_card in enemy_cards:
            # Elusive, Fearsome and Ephemeral check
            if "Elusive" in enemy_card.keywords or \
               "Ephemeral" in enemy_card.keywords or \
               "Fearsome" in enemy_card.keywords and blocking_card.attack < 3:
                continue
            is_blockable = True
            # Mixed block
            # TO DO: if n cards on board => 3 block with minimum sufficient stats that has much attack to kill 
            if enemy_card.health <= blocking_card.attack \
               or blocking_card.attack == 1 and enemy_card.health == 1 \
               or blocking_card.name == "Spiderling":
               #or n_cards_on_board == 6 and blocking_card.attack <= 2 :
                for ally_card in ally_cards:  # Check if card is already blocked
                    if abs(ally_card.get_pos()[0] - enemy_card.get_pos()[0]) < 10:
                        is_blockable = False
                        break
                if is_blockable:
                    self.drag_card_from_to(blocking_card.get_pos(), enemy_card.get_pos())
                    return True
        return False

    def playable_card(self, playable_cards, game_state, cards_on_board):
        cards_sorted = sorted(playable_cards, key=lambda playable_card: playable_card.cost, reverse=True)
        n_cards_on_board = len(cards_on_board["cards_board"])

        # Board conditions
        too_few = n_cards_on_board <= 1
        too_few_imp = n_cards_on_board = 0

        for playable_card_in_hand in cards_sorted:
            name = playable_card_in_hand.get_name()
            n_summon = 2 if "summon a" in playable_card_in_hand.description_raw.lower() else 1
            all_1hp_or_lower = len(cards_on_board["cards_board"]) != 0 and all(unit.health <= 1 for unit in cards_on_board["cards_board"])
            if name == "Imperial Demolist" and all_1hp_or_lower \
                or name == "Crowd Favorite" and too_few \
                or name == "Imperial Demolist" and too_few_imp \
                or n_cards_on_board + n_summon > 6 \
                    or all(card.get_name() != name for card in self.deck) \
            or name == "Parrley" or name == "Make it Rain" and len(cards_on_board["opponent_cards_board"]) < 2:
                continue
            if game_state == GameState.Attack_Turn or game_state == GameState.Defend_Turn:
                return playable_card_in_hand
        return None

    def reorganize_attack(self, cards_on_board, window_x, window_y, window_height):
        self.window_x = window_x
        self.window_y = window_y
        self.window_height = window_height

        # Move Overwhelm cards to the right
        overwhelm_counter = 0
        for attack_card in cards_on_board["cards_attk"]:
            if "Overwhelm" in attack_card.keywords:
                overwhelm_counter += 1
                self.drag_card_from_to(attack_card.get_pos(), (attack_card.get_pos()[0], 100))
                sleep(0.5)
        else:
            if overwhelm_counter > 0:
                keyboard.send("a")
                sleep(0.5)

        for attack_card in cards_on_board["cards_attk"]:
            # Remove Crackshot Corsair from board if necessary
            if attack_card.get_name() == "Crackshot Corsair" and len(cards_on_board["opponent_cards_board"]) != 0:
                self.drag_card_from_to(attack_card.get_pos(), (attack_card.get_pos()[0], 100))
                return False

        return True