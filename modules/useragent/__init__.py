from random import choice
def UserAgent():
    with open("useragents.txt") as file:
        ua=file.read().split("\n")
    return choice(ua)
