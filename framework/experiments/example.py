from module import SquareModule
from recipe import Recipe

t = [[0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]]

m0 = SquareModule('RedLoader', {'redload': 10}, t, 3)
m1 = SquareModule('BlueLoader', {'blueload': 10}, t, 3)
m2 = SquareModule('YellowLoader', {'Yellowload': 10}, t, 3)

m3 = SquareModule('RedYellowConditioner', {'redcond': 10, 'yelcond': 10}, t, 3)
m4 = SquareModule('RedBlueConditioner', {'redcond': 10, 'blucond': 10}, t, 3)
m5 = SquareModule('BlueConditioner', {'blucond': 10}, t, 3)


m6 = SquareModule('RedPainter', {'redpaint': 10}, t, 3)
m7 = SquareModule('YellowPainter', {'yelpaint': 10}, t, 3)
m8 = SquareModule('BluePainter', {'blupaint': 10}, t, 3)

m9 = SquareModule('Dryer0', {'dry': 10}, t, 3)
m10 = SquareModule('Dryer1', {'dry': 10}, t, 3)

m11 = SquareModule('Drill0', {'drill': 10}, t, 3)
m12 = SquareModule('Drill1', {'drill': 10}, t, 3)
m13 = SquareModule('Drill2', {'drill': 10}, t, 3)
m14 = SquareModule('Drill3', {'drill': 10}, t, 3)

m15 = SquareModule('Hammer', {'hammer': 10}, t, 3)
m16 = SquareModule('SuperHammer', {'Hammer': 2}, t, 3)

m17 = SquareModule('Packer1', {'pack': 10}, t, 3)
m18 = SquareModule('Packer2', {'pack': 10}, t, 3)
m19 = SquareModule('Packer3', {'pack': 10}, t, 3)

r0 = Recipe('Red', {'redload': set(),
                    'redpaint': {'redload'},
                    'redcond': {'redpaint'},
                    'dry': {'redcond'},
                    'drill': {'dry'},
                    'hammer': {'dry'},
                    'pack': {'drill', 'hammer'}},
            'RedLoader', 0, 2)

r1 = Recipe('Blue', {'bludload': set(),
                    'bludpaint': {'bluload'},
                    'bludcond': {'blupaint'},
                    'dry': {'blucond'},
                    'drill': {'dry'},
                    'hammer': {'dry'},
                    'pack': {'drill', 'hammer'}},
            'BlueLoader', 0, 2)

r2 = Recipe('yel', {'yelload': set(),
                    'yelpaint': {'yelload'},
                    'yelcond': {'yelpaint'},
                    'dry': {'yelcond'},
                    'drill': {'dry'},
                    'hammer': {'dry'},
                    'pack': {'drill', 'hammer'}},
            'YellowLoader', 0, 2)