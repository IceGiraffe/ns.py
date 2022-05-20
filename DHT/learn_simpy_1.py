from numpy import true_divide
import simpy


print('*' * 50)
print(f"Simulation 0")


def clock(env, name, tick):
    while True:
        print(name, env.now)
        yield env.timeout(tick)


env0 = simpy.Environment()

# The behavior of active components (like vehicles, customers or messages) is modeled with processes
# All processes live in an environment.
# * They interact with the environment and with each other via events
# process 是一个 generator
# process yield an event, then it will be suspended until the event occurs(triggered). SimPy resumes multiple processes waiting for the same event in the order they yield the event.
env0.process(clock(env0, 'fast', 0.5))

env0.process(clock(env0, 'slow', 1))

env0.run(until=2)


print('*' * 50)
print("Simulation 1")

# car是一个Generator，yield之后控制权会回到主函数


def car(env):
    while True:
        print(f'Start parking at {env.now}')
        parking_duration = 5
        yield env.timeout(parking_duration)

        print(f'Start driving at {env.now}')
        trip_duration = 2
        yield env.timeout(trip_duration)


env2 = simpy.Environment()
env2.process(car(env2))
env2.run(until=100)

print('*' * 50)
print('Simulation 2: Interact with other process')

# Environment.process() create a new ~simpy.events.Process instance for *generator*. The object can be used for interaction.

# process 也可以被用作 event 触发 process, 这样就可以实现process之间的交互


class Vehicle(object):
    def __init__(self, env):
        self.name = "A random vehicle"
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            # We yield the process that process() returns
            # to wait for it to finish
            yield self.env.process(self.charge(charge_duration))

            # The charge process has finished and
            # we can start driving again.
            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        print("Entering Charge")
        yield self.env.timeout(duration)

env2 = simpy.Environment()
car = Vehicle(env2)

# env2.run(until=15)
while True:
    print(env2.peek())
    env2.step()
    if(env2.now > 20):
        break


print("*" * 50)
print("Simulation 3: Interrupt an process")

def driver(env, car):
    yield env.timeout(3)
    car.action.interrupt()

class ImpatientCar(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            print(f'Start parking and charging at {self.env.now}')
            charge_duration = 5
            try:
                # 当这个process结束的时候，会回到yield之后继续运行
                yield self.env.process(self.charge(charge_duration))
            except simpy.Interrupt:
                print("Was interrupted. Hope, the battery is full enough...")
        
            print(f'Start driving at {self.env.now}')
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)

env3 = simpy.Environment()
car = ImpatientCar(env3)

env3.process(driver(env3, car))
while True:
    print(env3.peek())
    env3.step()
    if(env3.now > 20):
        break
# env3.run(until=10)
# env3.run(until=30)


print("*" * 50)
print("Simulation 4: Resources")

# 可以用来模拟生产者-消费者问题

def new_car(env, name, bcs, driving_time, charge_duration):
    yield env.timeout(driving_time)

    print(f'{name} arriving at {env.now}')
    # with as statement 可以自动释放资源
    # 
    with bcs.request() as req:
        yield req

        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))

env4 = simpy.Environment()
bcs = simpy.Resource(env4, capacity=2)

for i in range(4):
    env4.process(new_car(env4, f'Car {i}', bcs, i*2, 5))

env4.run()