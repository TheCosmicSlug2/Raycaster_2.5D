from random import randint

def random_rgb():
    return (randint(0, 255), randint(0, 255), randint(0, 255))    

def titlelize(word: str, marge: int=2) -> str:
    """ Stylise un titre """
    return f"{'-' * (len(word) + 2 * marge + 2)}\n|{' ' * marge}{word}{' ' * marge}|\n{'-' * (len(word) + 2 * marge + 2)}"
