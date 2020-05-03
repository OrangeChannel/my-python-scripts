"""Functions to help setup poker tournaments."""
__author__ = 'Dave <orangechannel@pm.me>'
__date__ = '4 February 2020'

from itertools import product

# Constants:
CASE = 100
MAX_PLAYERS = 10

money = {'yellow': 1000,
         'purple': 500,
         'black':  100,
         'green':  25,
         'blue':   10,
         'red':    5,
         'white':  1
         }

amounts = {'yellow': 2 * CASE,
           'purple': 2 * CASE,
           'black':  5 * CASE,
           'green':  3 * CASE,
           'blue':   2 * CASE,
           'red':    4 * CASE,
           'white':  2 * CASE
           }


def combo_finder(starting_stack: int, players: int = 9, min_chip: int = 25, colors: bool = True, ret_list: bool = False):
    """
    Prints possible combinations of poker chips that sum to `amount` using the amounts and money dicts.

    :param starting_stack: desired starting stack value ($)

    :param players: expected amount of players to determine max amount of each chip (Default value = 9)

    :param min_chip: smallest value ($) chip in starting stack (Default value = 25)

    :param colors: fancier print messages with colors instead of $ values (Default value = True)

    :param ret_list: return the list of combinations instead of printing
    """
    combos = []
    # find max chip counts: if chip value is >= the min, include it
    maxes = {k: amounts[k] // players if money[k] >= min_chip else 0 for k in money}

    # if chip value is >= the desired amount, DON'T include it
    for i in maxes:
        if money[i] >= starting_stack:
            maxes[i] = 0

    # optimize maxes: if chip value * max > starting stack, lower the max by 1
    # i.e. maxes['purple'] = 22, starting_stack = 900 --> maxes['purple'] = 1
    for i in maxes:
        if maxes[i]:
            while maxes[i] * money[i] > starting_stack:
                maxes[i] -= 1

    # for i in maxes
    maxes_list = [maxes[i] + 1 for i in maxes.keys()]
    product_list = [range(i) for i in maxes_list]  # range(x), range(y) ... for product arguments

    for pairs in product(*product_list):
        total = sum([pairs[k] * v for k, v in enumerate(money.values())])
        if total == starting_stack:
            if ret_list:
                combos.append(["{:02d} x ${}".format(amt, val) for amt, val in
                               [(pairs[k], v) for k, v in enumerate(money.values())]])
            else:
                if colors:
                    # first we get the amount in `pairs` and the name from money's keys before formatting and printing
                    print(["{:02d} {} chips".format(amt, name) for amt, name in
                           [(pairs[k], v) for k, v in enumerate(money.keys())]])
                else:
                    print(["{:02d} x ${}".format(amt, val) for amt, val in
                           [(pairs[k], v) for k, v in enumerate(money.values())]])
    if ret_list:
        return combos


def prize_calculator(buy_in: int, players: int, entrance_fee: float = None, winners: int = None,
                     chips_per_dollar: int = 100, ret: bool = False):
    """Prints prizes and possible chip values for a standard freezeout poker tournament."""
    prizes = []

    # Entrance Fee Calculator
    if entrance_fee is None:
        if buy_in < 10:
            entrance_fee = 0.25
        elif buy_in < 25:
            entrance_fee = 0.50
        elif buy_in < 50:
            entrance_fee = 1.00
        elif buy_in < 100:
            entrance_fee = 2.00
        else:
            entrance_fee = 3.00

    # Winners Calculator
    if winners is None:
        if players == 10:
            winners = 4
        elif 8 <= players <= 9:
            winners = 3
        elif players > 4:
            winners = 2
        else:
            winners = 1

    worth = buy_in - entrance_fee

    if winners == 4:
        prizes.append(worth / 2)  # 1/20 = 5 %
        prizes.append(3 * worth / 2)  # 3/20 = 15 %
        prizes.append(5 * worth / 2)  # 5/20 = 25 %
        prizes.append(11 * worth / 2)  # 11/20 = 55 %

    elif winners == 3:
        if players == 9:
            prizes.append(worth)  # 2/18 = 11.11 %
            prizes.append(3 * worth)  # 6/18 = 33.33 %
            prizes.append(5 * worth)  # 10/18 = 55.55 %
        elif players == 8:
            prizes.append(worth)  # 2/16 = 12.5 %
            prizes.append(5 * worth / 2)  # 5/16 = 31.25 %
            prizes.append(9 * worth / 2)  # 9/16 = 56.25 %

    elif winners == 2:
        if players == 7:
            prizes.append(2 * worth)
            prizes.append(5 * worth)
        elif players == 6:
            prizes.append(3 * worth / 2)
            prizes.append(9 * worth / 2)
        elif players == 5:
            prizes.append(3 * worth / 2)
            prizes.append(7 * worth / 2)

    else:
        prizes.append(players * worth)

    for k, v in enumerate(prizes[::-1]):
        print('Prize {}: ${:.2f}'.format(k + 1, v))

    if not ret:
        for i in [*map(int, [1E1, 2.5E1, 5E1, 1E2, 5E2, 1E3])]:
            print('Possible chips: {}\n\t${:.2f} per chip -- {} chips per $'.format(int(worth * i), i ** -1, i))
    else:
        return int(worth * chips_per_dollar)


def tournament():
    # Players
    players = int(input('How many players: '))

    # Buy-in
    buy_in = int(input('Tournament buy-in ($): '))

    # Winners
    winners = input('How many winners (leave blank to auto-calculate): ')
    if not winners:
        winners = None
    else:
        winners = int(winners)

    # Entrance-fee
    fee = input('Entrance fee ($) (leave blank to auto-calculate): ')
    if not fee:
        fee = None
    else:
        fee = float(fee)

    # Chips per dollar
    cpd = input('Chips per dollar (Default = 100): ')
    if not cpd:
        cpd = 100
    else:
        cpd = int(cpd)

    print('Starting stack: {}'.format(chips := prize_calculator(buy_in, players, fee, winners, cpd, True)))

    if (stack := buy_in * cpd) <= 500:
        minchip = 1
    elif stack <= 2500:
        minchip = 5
    elif stack <= 7500:
        minchip = 25
    else:
        minchip = 100

    return combo_finder(chips, players, minchip, False, True)


def blockchain_buyin_calc(desired_buyin: int):
    """blockchain.poker clean buy-in calculator with 2.5/2.5% tournament rake"""
    fee = desired_buyin / 19
    return round(desired_buyin + fee)


if __name__ == '__main__':
    combos = tournament()
