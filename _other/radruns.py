import itertools
import random
from fractions import Fraction
import functools

intact      = [Fraction(76, 100), Fraction(22, 100), Fraction(2 , 100)]
exceptional = [Fraction(70, 100), Fraction(26, 100), Fraction(4 , 100)]
flawless    = [Fraction(60, 100), Fraction(34, 100), Fraction(6 , 100)]
radiant     = [Fraction(50, 100), Fraction(40, 100), Fraction(10, 100)]

rarities = [intact, exceptional, flawless, radiant]
rarity_names = {0: 'Common', 1: 'Uncommon', 2: 'Rare'}
refinement_names = {0: 'Intact', 1: u'\u2605Exceptional', 2: u'\u2605\u2605Flawless', 3: u'\u2605\u2605\u2605Radiant'}
refinement_costs = {0: 0, 1: 25, 2: 50, 3: 100}

sub_intact      = [intact     [0]/3, intact     [1]/2, intact     [2]]
sub_exceptional = [exceptional[0]/3, exceptional[1]/2, exceptional[2]]
sub_flawless    = [flawless   [0]/3, flawless   [1]/2, flawless   [2]]
sub_radiant     = [radiant    [0]/3, radiant    [1]/2, radiant    [2]]

sub_rarities = [sub_intact, sub_exceptional, sub_flawless, sub_radiant]

def _rarity(ref: int, sub: bool=False):
    """returns float values of chances based on refinement level"""
    rar = rarities if not sub else sub_rarities
    if   ref == 0: return [*map(float, rar[0])]
    elif ref == 1: return [*map(float, rar[1])]
    elif ref == 2: return [*map(float, rar[2])]
    elif ref == 3: return [*map(float, rar[3])]


class Relic:

    def __init__(self, refinement: int):
        self.refinement = refinement
        self.common,  self.uncommon,  self.rare  = _rarity(refinement)
        self.scommon, self.suncommon, self.srare = _rarity(refinement, sub=True)


def run(refinement_levels: list, specific: bool=False):
    players, rewards = [], []
    for r in refinement_levels:
        players.append(Relic(r))
    if specific:
        for p in players:
            rewards.append(random.choices(list(range(6)),weights=[p.scommon, p.scommon, p.scommon, p.suncommon, p.suncommon, p.srare])[0])
    else:
        for p in players:
            rewards.append(random.choices(list(range(3)),weights=[p.common, p.uncommon, p.rare])[0])
    return rewards


def auto():
    start = '\n-->   '

    player_count = int(input('How many players: '))
    print('{}Player count: {}\n'.format(start, player_count))

    # int list 0 - 3
    refinement_levels = list(map(int, input('Refinement levels of each relic: ').strip().split()))[:player_count]

    level_names = [refinement_names[i] for i in refinement_levels]
    print('{}Refinement Levels: {}'.format(start, ',  '.join(level_names)))

    # number of void traces per run
    print('{}Void traces spent per run: {}\n'.format(start, traces := sum(map(lambda i: refinement_costs[i], refinement_levels))))

    # rarity 0 - 2
    rarity = int(input('What rarity: '))
    print('{}Rarity: {}\n'.format(start, rarity_names[rarity]))

    if rarity != 2:
        goal_type = input(r'Trying for a specfic item? [Y/n] ')
        specific = True if goal_type == 'Y' else False
    else: specific = False


    # chance of getting AT LEAST one
    p_nots = []
    for i in range(player_count):
        p_nots.append(1 - _rarity(refinement_levels[i], specific)[rarity])

    p_not = functools.reduce(lambda x, y: x*y, p_nots)

    print(u'\t\u2605\u2605\u2605  Chance per run of getting {}{} loot: {:.2%}'.format('the specific ' if specific else '',rarity_names[rarity], chance := 1 - p_not))
    print(u'\t\u2605\u2605\u2605  Number of runs to get {}{} loot: {:.2f}'.format('the specific ' if specific else '',rarity_names[rarity], runs := chance**-1))
    print(u'\t\u2605\u2605\u2605  Number of void traces to get {}{} loot: {}\n'.format('the specific ' if specific else '',rarity_names[rarity], int(traces * runs)))
    for i in range(player_count):
        print('\t\u2605\u2605  Number of void traces for player # {}: {}'.format(i+1, int(runs*refinement_costs[refinement_levels[i]])))

    # chance of getting an exact number

    # lists of combinations of receiving goal X number of times
    one, two, three, four = [], [], [], []
    prod = [i for i in itertools.product([True, False], repeat=player_count)]
    for i in prod:
        if i.count(True) == 1:
            one.append(i)  # [False, True, False, False]
        elif i.count(True) == 2:
            two.append(i)
        elif i.count(True) == 3:
            three.append(i)
        elif i.count(True) == 4:
            four.append(i)  # [True, ...]

    possibilities = [one, two, three, four]

    # probability of EXACTLY 1
    count_rarity = {}
    for amount, pos_list in enumerate(possibilities):
        if pos_list:
            B = []
            for combo_list in pos_list:
                C = []
                for player_n in range(player_count):
                    if combo_list[player_n]:
                        C.append(_rarity(refinement_levels[player_n], specific)[rarity])
                    else:
                        C.append(1 - _rarity(refinement_levels[player_n], specific)[rarity])
                B.append(functools.reduce(lambda x, y: x*y, C))

            count_rarity[amount+1] = sum(B)

    print('')
    for i in range(player_count):
        print('\t\u2605  The chance of getting the {}{} loot exactly {} time(s) is {:.2%}'.format('the specific ' if specific else '', rarity_names[rarity], i+1, count_rarity[i+1]))

    print('\n\t  The chance of wasting a relic therefore is {:.2%}'.format(sum(list(count_rarity.values())[1:])))


if __name__ == '__main__':
    auto()
