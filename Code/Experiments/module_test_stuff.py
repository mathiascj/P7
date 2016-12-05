from framework.module import SquareModule


t_time = [[-1, -1, -1, -1],
          [-1, -1, -1, 112],
          [-1, -1, -1, -1],
          [-1, 112, -1, -1]]

m0 = SquareModule(0, [0], {0: 0}, t_time, 0)
m1 = SquareModule(1, [0], {0: 0}, t_time, 0)
m2 = SquareModule(2, [0], {0: 0}, t_time, 0)
m3 = SquareModule(3, [0], {0: 0}, t_time, 0)
m4 = SquareModule(4, [0], {0: 0}, t_time, 0)
m5 = SquareModule(5, [0], {0: 0}, t_time, 0)
m6 = SquareModule(6, [0], {0: 0}, t_time, 0)

m0.up = m1
m1.right = m2
m2.down = m3
m3.down = m4
m4.left = m5


grid = m0.make_grid()
res = m0.can_connect(m5, (-1, 0))