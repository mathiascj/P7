from module import SquareModule
from recipe import Recipe
from configuration.tabu_search import tabu_search

t = [[5, 5, 5, 5],
     [5, 5, 5, 5],
     [5, 5, 5, 5],
     [5, 5, 5, 5]]

queue_length = 2

doll_loader = SquareModule(m_id='doll_loader', wp_time={'load-doll': 10}, t_time=t, queue_length=queue_length)
limb_giver = SquareModule(m_id='limb_giver', wp_time={'arms': 15, 'legs': 15}, t_time=t, queue_length=queue_length)
arm_giver = SquareModule(m_id='arm_giver', wp_time={'arms': 20}, t_time=t, queue_length=queue_length)
leg_giver = SquareModule(m_id='leg_giver', wp_time={'legs': 20}, t_time=t, queue_length=queue_length)
head_giver = SquareModule(m_id='head_giver', wp_time={'head': 10}, t_time=t, queue_length=queue_length)
painter = SquareModule(m_id='painter', wp_time={'paint': 5}, t_time=t, queue_length=queue_length)
gift_wrapper = SquareModule(m_id='gift_wrapper', wp_time={'gift-wrap': 10}, t_time=t, queue_length=queue_length)
wood_loader = SquareModule(m_id='wood_loader', wp_time={'load-wood': 5}, t_time=t, queue_length=queue_length)
jigsaw = SquareModule(m_id='jigsaw', wp_time={'saw': 10}, t_time=t, queue_length=queue_length)
buzzsaw = SquareModule(m_id='buzzsaw', wp_time={'saw': 10}, t_time=t, queue_length=queue_length)
connector = SquareModule(m_id='connector', wp_time={'hammer': 5, 'screw': 5}, t_time=t, queue_length=queue_length)
sander = SquareModule(m_id='sander', wp_time={'sand': 10}, t_time=t, queue_length=queue_length)
wrapper = SquareModule(m_id='wrapper', wp_time={'wrap': 5}, t_time=t, queue_length=queue_length)

modules = [doll_loader, limb_giver, arm_giver, leg_giver, head_giver, painter, gift_wrapper, wood_loader, jigsaw, buzzsaw, connector, sander, wrapper]

print(len(modules))

fd0 = {'load-doll': set(), 'arms': {'load-doll'}, 'legs': {'load-doll'}, 'head': {'load-doll'}, 'paint': {'arms', 'legs', 'head'}, 'gift-wrap': {'paint'}}
fd1 = {'load-wood': set(), 'saw': {'load-wood'}, 'hammer': {'saw'}, 'screw': {'saw'}, 'sand': {'hammer', 'screw'}, 'wrap': {'sand'}}
fd2 = {'load-wood': set(), 'saw': {'load-wood'}, 'hammer': {'saw'}, 'sand': {'hammer'}, 'paint': {'sand'}, 'wrap': {'paint'}}

recipe_doll = Recipe(name='recipe_doll', dependencies=fd0, start_module='doll_loader', start_direction=0, amount=2)
recipe_horse = Recipe(name='recipe_horse', dependencies=fd1, start_module='wood_loader', start_direction=0, amount=2)
recipe_sword = Recipe(name='recipe_sword', dependencies=fd2, start_module='wood_loader', start_direction=0, amount=2)

recipes = [recipe_doll, recipe_horse, recipe_sword]

transporter = SquareModule(m_id='trans', wp_time={}, t_time=t, queue_length=queue_length)

res = tabu_search(recipes, modules, transporter, iters=100, short_term_size=5, max_initial_configs=10)

for r in res:
    print(r)



