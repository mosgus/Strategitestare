import random


def spin_wheel(bet_array):
    """
    Simulates an American Roulette spin.

    input:
        bet_array (list): A list of 38 numbers representing bets on [0, 00, 1, 2, ..., 36]
    output:
        payout (float): The net earnings (e.g. +35.0 or -10.0)
    """
    total_wagered = sum(bet_array)     # 1. Calc the user bet

    winning_index = random.randint(0, 37)     # 2. Pick a random winning index (0 to 37)

    amount_on_winner = bet_array[winning_index]     # 3. Calculate slot payout

    print(f"Winning tile: {winning_index}, Amount on winner: {amount_on_winner:.2f}")

    if amount_on_winner > 0: # WIN
        payout = amount_on_winner + (amount_on_winner * 35)
    else: # LOSE
        payout = 0

    return payout - total_wagered # 4. Return the net result

'''
USAGE EXAMPLE 1:1: 
if __name__ == "__main__":
    # Simulate a $10 bet on the number '7' (index 8)
    test_bet = [0] * 38

    bet_amount_per_number = 10 / 18
    for i in range(2, 20):
        test_bet[i] = bet_amount_per_number

    result = spin_wheel(test_bet)

    if result > 0:
        print(f"You win: +{result:.2f}")
    else:
        print(f"You lose: {result:.2f}")
'''