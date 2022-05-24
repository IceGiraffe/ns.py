import simpy
env = simpy.Environment()

res = simpy.Resource(env, capacity=2)
def print_stats(res):
    print(f'{res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')
def user(res, i):
    print("** Init Stats",i)
    print_stats(res)
    with res.request() as req:
        yield req
        print("* After Yield Stats",i)
        print_stats(res)
    
    print("*** Final Stats",i)
    print_stats(res)
procs = [env.process(user(res, 1)), env.process(user(res, 2)), env.process(user(res, 3))]
env.run()
# ** Init Stats 1
# 0 of 2 slots are allocated.
#   Users: []
#   Queued events: []
# ** Init Stats 2
# 1 of 2 slots are allocated.
#   Users: [<Request() object at 0x112c1d454c0>]
#   Queued events: []
# ** Init Stats 3
# 2 of 2 slots are allocated.
#   Users: [<Request() object at 0x112c1d454c0>, <Request() object at 0x112bf970f40>]
#   Queued events: []
# * After Yield Stats 1
# 2 of 2 slots are allocated.
#   Users: [<Request() object at 0x112c1d454c0>, <Request() object at 0x112bf970f40>]
#   Queued events: [<Request() object at 0x112bf970d30>]
# *** Final Stats 1
# 1 of 2 slots are allocated.
#   Users: [<Request() object at 0x112bf970f40>]
#   Queued events: [<Request() object at 0x112bf970d30>]
# * After Yield Stats 2
# 1 of 2 slots are allocated.
#   Users: [<Request() object at 0x112bf970f40>]
#   Queued events: [<Request() object at 0x112bf970d30>]
# *** Final Stats 2
# 0 of 2 slots are allocated.
#   Users: []
#   Queued events: [<Request() object at 0x112bf970d30>]
# * After Yield Stats 3
# 1 of 2 slots are allocated.
#   Users: [<Request() object at 0x112bf970d30>]
#   Queued events: []
# *** Final Stats 3
# 0 of 2 slots are allocated.
#   Users: []
#   Queued events: []