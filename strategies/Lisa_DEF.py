from constants import GameState
from Strategy import Strategy
from time import sleep
import keyboard


class Generic(Strategy):
    def __init__(self, mouse_handler):
        super().__init__(mouse_handler)

    def mulligan(self, cards, window_x, window_y, window_height):
        # Window stuff
        self.window_x = window_x
        self.window_y = window_y
        self.window_height = window_height

        # Mulligan away cards with cost greater than 2
        for in_game_card_obj in cards:
            if in_game_card_obj.cost > 2: # TO DO: check for 3 cards with cost 2 and remove 2
                cx = window_x + in_game_card_obj.top_center[0]
                cy = window_y + window_height - in_game_card_obj.top_center[1]
                self.mouse_handler.click(cx, cy)
                sleep(0.5)

    def block(self, cards_on_board, window_x, window_y, window_height):
        self.window_x = window_x
        self.window_y = window_y
        self.window_height = window_height

        for i, blocking_card in enumerate(cards_on_board["cards_board"]):
            if i < self.block_counter or "Can't Block" in blocking_card.keywords or "Immobile" in blocking_card.keywords: #or "Overwhelm" in blocking_card.keywords:
                continue
            if self.blocked_with(blocking_card, cards_on_board["opponent_cards_attk"], cards_on_board["cards_attk"]): #, cards_on_board["cards_board"]):
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
            if enemy_card.health <= blocking_card.attack or \
               blocking_card.attack == 1 and enemy_card.health == 1 :
               #n_cards_on_board == 6 and blocking_card.attack <= 2 :
                for ally_card in ally_cards:  # Check if card is already blocked
                    if abs(ally_card.get_pos()[0] - enemy_card.get_pos()[0]) < 10:
                        is_blockable = False
                        break
                if is_blockable:
                    self.drag_card_from_to(blocking_card.get_pos(), enemy_card.get_pos())
                    return True
        return False

    def playable_card(self, playable_cards, game_state, cards_on_board):
        """Return the first playable highest cost card"""
        cards_sorted = sorted(playable_cards, key=lambda playable_card: playable_card.cost, reverse=True)
        n_cards_on_board = len(cards_on_board["cards_board"])
        for playable_card_in_hand in cards_sorted:
            n_summon = 2 if "summon a" in playable_card_in_hand.description_raw.lower() else 1
            if n_cards_on_board + n_summon > 6:
                continue # DO NOT play the card
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

        # Remove cards with 0 attack power
        for attack_card in cards_on_board["cards_attk"]:
            if attack_card.attack == 0:
                self.drag_card_from_to(attack_card.get_pos(), (attack_card.get_pos()[0], 100))
                return False

        return True