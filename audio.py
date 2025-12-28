import pygame as pg
from random import choice, randint
pg.mixer.init()

# Get sounds
def to_sound(path) -> pg.mixer.Sound:
    return pg.mixer.Sound(path)



steproot = "rsc/sounds/step"
glassroot = "rsc/sounds/glass"
cyka = pg.mixer.Sound("rsc/sounds/cyka.mp3")
dig_wall = pg.mixer.Sound("rsc/sounds/wall_dig.ogg")
place1 = pg.mixer.Sound("rsc/sounds/wall_place.ogg")
remove1 = pg.mixer.Sound("rsc/sounds/place2.mp3")
dig_glass1 = pg.mixer.Sound("rsc/sounds/glass_dig1.ogg")
dig_glass2 = pg.mixer.Sound("rsc/sounds/glass_dig2.ogg")
dig_glass3 = pg.mixer.Sound("rsc/sounds/glass_dig3.ogg")

class Audio:
    def __init__(self, blyat_mode=False) -> None:
        self.steps = []
        self.glass = []
        self.idx = 0
        for root, liste in ((steproot, self.steps), (glassroot, self.glass)):
            for i in range(1, 5):
                liste.append(pg.mixer.Sound(root + str(i) + ".mp3"))
        if blyat_mode:
            pg.mixer.music.load("rsc/sounds/anthem.mp3")
            pg.mixer.music.play()
    
    @staticmethod
    def play_place():
        place1.play()

    @staticmethod
    def play_dig(glass=False):
        liste = [dig_glass1, dig_glass2, dig_glass3] if glass else [remove1]
        choice(liste).play()

    
    def play_rdm(self, steps=False, glass=False):
        if steps:
            liste = self.steps
        if glass:
            liste = self.glass
        choices = list(range(len(liste)))
        choices.remove(self.idx)
        self.idx = choice(choices)
        liste[self.idx].play()




