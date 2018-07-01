import hashlib


def randomise(range_int, chars=""):
    import random
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%s" % chars
    array = []
    for char in range(range_int):
        array.append(random.choice(chars))
    return "".join(array)


def hash_password(raw_pass, salt=None):
    if salt is None:
        salt = randomise(16)

    hash_val = hashlib.sha256(("%s%s" % (salt, raw_pass)).encode("utf-8"))
    return "%s$%s" % (salt, hash_val.hexdigest())


def is_logged_in():
    from flask import session
    return True if "email" in session and "username" in session else False
