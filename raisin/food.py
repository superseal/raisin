from collections import defaultdict
from enum import Enum

import bank
import config
import database
import message_queue


class Pot(Enum):
    EMPTY = 0
    PLANTED_WEED_SEED = 1
    GROWING_WEED_SEED = 2
    READY_WEED_PLANT = 3
    PLANTED_CARROT_SEED = 4
    GROWING_CARROT_SEED = 5
    READY_CARROT_PLANT = 6

POT_VALUE = 500
WEED_SEED_VALUE = 200
CARROT_SEED_VALUE = 300

pots = defaultdict(int)
weed_seeds = defaultdict(int)
carrot_seeds = defaultdict(int)
stored_weeds = defaultdict(int)
stored_carrots = defaultdict(int)


def enough(sender):
    return weed > 0 or carrots[sender] > 0




def get_backyard(sender):
    pass
