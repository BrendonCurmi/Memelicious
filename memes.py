import random
from database import Memes


# Process and fix the pool
def __pooling(pool):
    pool = str(pool).split(",")
    if pool[0] == "":
        pool.remove("")
    return pool


# Selects a new random value, from within the limits (both inclusive),
# making sure it's not present in the pool of values.
def __get_new_random(min_val, max_val, pool):
    selected = "%s" % random.randint(min_val, max_val)
    return selected if selected not in pool else __get_new_random(min_val, max_val, pool)


# Selects an array of unique values to be displayed.
def meme_machine(value, pool):
    pool, selected = __pooling(pool), []
    block_size, group_size, paired_groups = 9, 2, 3
    for rows in range(paired_groups + 1):
        if rows == paired_groups:
            value += (block_size + 1) * random.randint(1, paired_groups)
            group_size = 1

        for selector in range(group_size):
            val = __get_new_random(value - block_size, value, pool)
            selected.append(Memes.get_name_from_id(val))
            pool.append(val)
        value -= block_size + 1
    return [selected, pool]


# Selects an array of random unique values to be displayed.
def random_feed(pool):
    pool, selected = __pooling(pool), []
    for selector in range(4):
        val = __get_new_random(0, Memes.get_latest_id(), pool)
        selected.append(Memes.get_name_from_id(val))
        pool.append(val)
    return [selected, pool]
