import simpy

# def my_callback(e):
#     print('Called from', e)

env = simpy.Environment()

# e = env.event()
# e.callbacks.append(my_callback)
# print(e.callbacks)
# env.step()


class School:
    def __init__(self, env):
        self.env = env
        self.class_ends = env.event()
        self.pupil_procs = [env.process(self.pupil()) for i in range(3)]
        self.bell_proc = env.process(self.bell())
    def bell(self):
        for i in range(1):
            print('bell yield timeout')
            yield self.env.timeout(45)
            print("time out triggered and bell resumed",i)
            self.class_ends.succeed()
            print("class_ends succeed, after event.succeed and callback")
            self.class_ends = self.env.event()
            print()
    def pupil(self):
        for i in range(1):
            print(r'\o/')
            # print(env.active_process)
            print("yield class ends", i)
            yield self.class_ends
            print('pupil resumed', i)

            
school = School(env)
# env.run()
while True:
    print('*',env.peek(),"*", end=' ')
    if(env.peek() == float('inf')):
        break
    env.step()