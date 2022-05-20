[TOC]

# Overview

* `SimPy`可以简单理解为一个移步`Evnet`的调度器，不断生成`Evnet``Event`然后按照时间顺序调度这些`Evnet`，`Evnet`按照优先级、时间和`Evnet ID`排序。

* 每个`Evnet`都与一系列**回调函数**`callbacks`相关联，在`Evnet`被触发后，这些回调函数按顺序被调用；`Evnet`可以有返回值。

* `SimPy`通过`Process`来模拟模型，`Process`是`Python`中的`generator`类型，yield出一个Event。在`Process`yield`Event`时，`SimPy`会把`Process`本身插入到该`Event`的回调函数列表里面，然后将这个`Process`挂起。

* `Environment`存储`Event`，记录当前的模拟时间`Simulation Time`，随着时间不断前进，`Event`会不断触发`Trigger`，之后会调用回调函数列表中的函数，注意，`Process`一定在该函数中，这样就可以通过`process`循环生成`Event`，`Event`的返回值也会传入到`Process`中。

* 下面的例子详细说明了上述过程

  ~~~Python
  >>> import simpy
  >>>
  >>> def example(env):
  ...     event = simpy.events.Timeout(env, delay=1, value=42)
  ...     value = yield event
  ...     print('now=%d, value=%d' % (env.now, value))
  >>>
  >>> env = simpy.Environment()
  >>> example_gen = example(env)
  >>> p = simpy.events.Process(env, example_gen)
  >>>
  >>> env.run()
  >>> now=1, value=42
  ~~~

# Environments

## Simulation Control

* `Environment`是`SimPy`中定义的模拟环境，一般模拟使用`Environment`即可，*不过注意`SimPy`还提供了`RealtimeEnvironment`用来进行实时模拟*。

* `env.run()`方法开始仿真，仿真结束的条件如下：

  * 如果没有传入任何参数，`env`中所有事件都执行完毕结束仿真，这样做可能会导致无限循环；

  * 到达`until`参数指定的模拟时间：

    * `env.run(until = 100)`，当时间`step=100`时仿真结束

    * `until`时间点的`Event`将不会被触发；

    * 当多次调用`env.run()`时，将在模拟环境上次停下的时间继续，下方代码模拟了一个进度条，`until`参数的值不能小于当前的模拟时间。

      ```python
      for i in range(100):
          env.run(until=i)
          progressbar.update(i)
      ```

    * 特定事件被触发

      ```python
      env.run(until=env.timeout(5)) # 等价于env.run(until=5)
      env.run(until=env.process(my_proc(env))) #当该process执行时，仿真结束
      ```

* `SimPy`支持单步仿真

  * `peek()`返回下一个事件的发生时间，或者`float('inf')`表示之后没有事件了；

  * `step()`处理下一个事件，如果没有下一个时间，抛出`EmptySchedule`异常；

  * ~~~python
    until=10
    while env.peek() < until:
        env.step()
    ~~~

## State Access

* `env.now()`是当前时间，模拟时间是一个无单位整数；
* `initial_time`参数设置模拟的出世时间；
* `env.active_process()`返回当前活跃的`Process`对象，如果没有活跃的对象，返回`None`，当程序在当前`process`中时，我们称`Process`是活跃的，当`yield`之后，该`Process`被挂起，或进入不活跃状态。简单理解，在一个generator function的函数体里面调用`env.active_process()`，返回值为当前`process`

## Event Creation

* 事件定义在`simpy.events`里，将当前模拟环境做为参数即可实例化`Event`类；

  * `simpy.enents.Event(env)`

* `Environment`提供了实例化`Event`的快捷方式

  ~~~Python
  env = simpy.Environment()
  env.process()
  env.timeout()
  env.all_of()
  env.any_of()
  ~~~

* `Python 3.3`之后，`generator function`可以有返回值，在`SimPy`中，这可以用来给那些`yield`另一个`process`事件的`process`提供返回值。

  ~~~python
  def another_proc(env):
      yield env.timeout(1)
      return 42
  
  def my_proc(env):
      # another_proc函数会提供一个返回值
      ret_val = yield env.process(another_proc(env))
      assert ret_val == 42
  ~~~

# Events

## Basics

* 基于`Event`派生出不同的`Event`

  ~~~Python
  events.Event
  |
  +— events.Timeout
  |
  +— events.Initialize
  |
  +— events.Process
  |
  +— events.Condition
  |  |
  |  +— events.AllOf
  |  |
  |  +— events.AnyOf
  ~~~

* 事件的生命周期从始至终经历三个状态，事件与时间紧密联系，时钟前进推进事件的状态

  * might happen (not triggered)，事件创建后的初始状态；
  * is going to happen (triggered)，触发之后，`Event.triggered`被设置为`True`，该事件被插入到队列中，然后安排在事件`t`处理
  * has happened (processed)，当时间到达安排的`t`时，执行所有回调函数，该事件状态变为processed，`Event.processed=True`

* Events also have a *value*. The value can be set before or when the event is triggered and can be retrieved via [`Event.value`](https://simpy.readthedocs.io/en/latest/api_reference/simpy.events.html#simpy.events.Event.value) or, within a process, by yielding the event (`value = yield event`).

* If a process function yields an event, `SimPy` adds the process to the event’s callbacks and suspends the process until the **event is triggered and processed**. When a process waiting for an event is resumed, it will also receive the event’s value.

* 给`Event`增加回调函数，注意回调函数有且仅有一个参数`event`，即当前`Event`

  ~~~python
  def my_callback(event):
      print('Called back from', event)
      
  env = simpy.Environment()
  event = env.event()
  event.callbacks.append(my_callback)
  print(event.callbacks)
  ~~~

  在触发并执行该事件之后，`event.callbacks`将被设置为`None`，这时便不能再增加回调函数了。

* `Trigger`触发事件

  * 触发一个事件之后，该事件可能成功，也可能失败
  * `Event.succeed(value=None)`表示触发一个事件，并将其标记为成功
  * `Event.fail(exception)`表示触发一个事件，并将其标记为失败
  * `Event.trigger(event)`表示触发一个事件，将当前事件相关值设置为参数`event`的相关值，相当于根据`event`的结果设置当前`Event`的结果
  * 上述方法返回事件本身，因此可以这样用`yield Event(env).succeed()`

* 一个例子

  ~~~python
  import simpy
  
  env = simpy.Environment()
  
  class School:
      def __init__(self, env):
          self.env = env
          self.class_ends = env.event()
          self.pupil_procs = [env.process(self.pupil()) for i in range(3)]
          self.bell_proc = env.process(self.bell())
      def bell(self):
          for i in range(2):
              print('bell yield timeout')
              yield self.env.timeout(45)
              print("time out triggered and bell resumed",i)
              self.class_ends.succeed()
              print("class_ends succeed, after event.succeed and callback")
              self.class_ends = self.env.event()
              print()
      def pupil(self):
          for i in range(2):
              print(r'\o/')
              print(env.active_process)
              print("yield class ends", i)
              yield self.class_ends
              print('pupil resumed', i)
              
  school = School(env)
  while True:
      print(env.peek(), end=' ')
      if(env.peek() == float('inf')):
          break
      env.step()
  ~~~

  * 输出如下

    > 0 \o/
    > <Process(pupil) object at 0x283592e2f10>
    > yield class ends 0
    > 0 \o/
    > <Process(pupil) object at 0x2835b6af790>
    > yield class ends 0
    > 0 \o/
    > <Process(pupil) object at 0x2835b6af670>
    > yield class ends 0
    > 0 bell yield timeout
    > 45 time out triggered and bell resumed 0
    > class_ends succeed, after event.succeed and callback
    >
    > bell yield timeout
    > 45 pupil resumed 0
    > \o/
    > <Process(pupil) object at 0x283592e2f10>
    > yield class ends 1
    > pupil resumed 0
    > \o/
    > <Process(pupil) object at 0x2835b6af790>
    > yield class ends 1
    > pupil resumed 0
    > \o/
    > <Process(pupil) object at 0x2835b6af670>
    > yield class ends 1
    > 90 time out triggered and bell resumed 1
    > class_ends succeed, after event.succeed and callback
    >
    > // 下面90之后的就是class_ends事件及其callback
    >
    > 90 pupil resumed 1
    > pupil resumed 1
    > pupil resumed 1
    > 90 90 90 90 inf

  * 这个例子说明：`event`可以被共享，多个`pupil`的`process`同时`yield`了`class_ends`事件，该事件触发之后，这些`pupil`也依次被恢复，顺序与`yield`顺序一致。

  * **存在一个问题：最后的90 90 90 90是什么**，是执行`pupil`和`bell`的回调（实际是空的）

* `Timeout`事件使时间流逝

  * `Timeout(delay, value=None)`
  * 在`delay`之后触发该事件

## Process as Events

* 当`Process`被创建之后，它的`Initialize`事件被安排，当`Initialize`触发之后，函数体会被执行；*事件本身则用来处理回调*

* 可以使用`start_delayed`延迟一个`Process`

* ~~~python
  >>> from simpy.util import start_delayed
  >>>
  >>> def sub(env):
  ...     yield env.timeout(1)
  ...     return 23
  ...
  >>> def parent(env):
  ...     sub_proc = yield start_delayed(env, sub(env), delay=3)
  ...     ret = yield sub_proc
  ...     return ret
  ...
  >>> env.run(env.process(parent(env)))
  23
  ~~~

## Waiting for Multiple Events at Once

* `SimPy`提供了条件事件，可以用来实现同时等待多个事件或多个事件之一的功能

  ~~~python
  >>> from simpy.events import AnyOf, AllOf, Event
  >>> events = [Event(env) for i in range(3)]
  >>> a = AnyOf(env, events)  # Triggers if at least one of "events" is triggered.
  >>> b = AllOf(env, events)  # Triggers if all each of "events" is triggered.
  ~~~

* 条件事件的值是一个有序字典，每个条目都是一个**触发的**事件，`key`是`event`对象，`value`为该`event`的`value`。

  * 对于`Allof`事件，字典大小跟给定的条件的数量是相同的；
  * 对于`Allof`和`＆`，字典中条目的顺序跟条件的顺序一致；
  * 对于`Anyof`事件，字典大小至少为1，至多与条件数量相同。

* `SimPy`重载了`＆`和`|`用来简化条件事件声明

  ~~~python
  >>> def test_condition(env):
  ...     t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
  ...     ret = yield t1 | t2
  ...     assert ret == {t1: 'spam'}
  ...
  ...     t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
  ...     ret = yield t1 & t2
  ...     assert ret == {t1: 'spam', t2: 'eggs'}
  ...
  ...     # You can also concatenate & and |
  ...     e1, e2, e3 = [env.timeout(i) for i in range(3)]
  ...     yield (e1 | e2) & e3
  ...     assert all(e.processed for e in [e1, e2, e3])
  ...
  >>> proc = env.process(test_condition(env))
  >>> env.run()
  ~~~

# Process Interaction

* Sleep until woken up

* Waiting for another process to terminate

* Interrupting another process

  ~~~python
  >>> class EV:
  ...     def __init__(self, env):
  ...         self.env = env
  ...         self.drive_proc = env.process(self.drive(env))
  ...
  ...     def drive(self, env):
  ...         while True:
  ...             # Drive for 20-40 min
  ...             yield env.timeout(randint(20, 40))
  ...
  ...             # Park for 1 hour
  ...             print('Start parking at', env.now)
  ...             charging = env.process(self.bat_ctrl(env))
  ...             parking = env.timeout(60)
  ...             yield charging | parking
  ...             if not charging.triggered:
  ...                 # Interrupt charging if not already done.
  ...                 charging.interrupt('Need to go!')
  ...             print('Stop parking at', env.now)
  ...
  ...     def bat_ctrl(self, env):
  ...         print('Bat. ctrl. started at', env.now)
  ...         try:
  ...             yield env.timeout(randint(60, 90))
  ...             print('Bat. ctrl. done at', env.now)
  ...         except simpy.Interrupt as i:
  ...             # Onoes! Got interrupted before the charging was done.
  ...             print('Bat. ctrl. interrupted at', env.now, 'msg:',
  ...                   i.cause)
  ...
  >>> env = simpy.Environment()
  >>> ev = EV(env)
  >>> env.run(until=100)
  Start parking at 31
  Bat. ctrl. started at 31
  Stop parking at 91
  Bat. ctrl. interrupted at 91 msg: Need to go!
  ~~~

  `process.interrupt()`做的事情就是安排一个`Interruption`事件立即执行，该事件会将`bat_ctrl`等待的事件（`target`）的回调函数列表中去除`bat_ctrl._consume()`，并且抛出`Interrupt`异常，这些事情是在`Interruption`的回调函数中实现的。

# Shared Resources

* 模拟了`Process`的竞争点，`Process`排队使用资源。`SimPy`定义了三种资源，分别是`Resources`，`Containers`和`Stores`。
  * [Resources](https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#res-type-resource) – Resources that can be used by a limited number of processes at a time (e.g., a gas station with a limited number of fuel pumps).
  * [Containers](https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#res-type-container) – Resources that model the production and consumption（**生产者-消费者问题**） of a homogeneous, undifferentiated bulk. It may either be continuous (like water) or discrete (like apples).
  * [Stores](https://simpy.readthedocs.io/en/latest/topical_guides/resources.html#res-type-store) – Resources that allow the production and consumption of Python objects.

## Basics

* 资源类似某种容器，一般容量是优先的。`Process`可以从`esource`中`Put`或`Get`某种东西，如果`Resource`满了或者空了，则`Process`需要排队

* ~~~Python
  BaseResource(capacity):
      put_queue
      get_queue
      ...
      put(): event
      get(): event
  ~~~

* 每一个资源都有最大容量和两个队列，`put`和`get`队列，返回值都是事件，当资源可用或请求的动作可以执行时，事件被触发。

* 当在排队的`Process`被打断时，有两种选择：

  * 继续排队，只需要重新`yield` `put`或`get`事件即可；
  * 退出排队，在这种情况下需要调用事件的`cancel()`方法。
  * 可以使用`Python`的上下文管理器简化这一操作，即`with ... as ...`

## Resources

* `Resource`表示有限资源，概念上相当于信号量。`Process`可以`request`一份资源，在使用后`release`掉。`Request`事件继承自`Put`事件，相当于把某个进程的`token`放进去；同样，`Release`继承自`Get`事件，相当于取走自己的`token`。`Release`事件总是会立刻成功。

* `Resource`有以下几种

  * [`Resource`](https://simpy.readthedocs.io/en/latest/api_reference/simpy.resources.html#simpy.resources.resource.Resource)
  * [`PriorityResource`](https://simpy.readthedocs.io/en/latest/api_reference/simpy.resources.html#simpy.resources.resource.PriorityResource), where queueing processes are sorted by priority
  * [`PreemptiveResource`](https://simpy.readthedocs.io/en/latest/api_reference/simpy.resources.html#simpy.resources.resource.PreemptiveResource), where processes additionally may preempt other processes with a lower priority

* `Resource`的基本用法就是`Request`和`Release`，同时支持查看当前用户和队列信息

  ~~~python
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
  ~~~

  注意，这里时间没有前进，各种事件（包括`Initialize`和`Request`）都被安排在同一时刻，按照`schedule`的先后顺序执行，可以从输出看出这一点。

* `PriorityResource`

  ~~~python
  res = simpy.PriorityResource(env, capacity=1)
  
  def resource_user(env, prio):
      with res.request(priority = prio) as req:
          yield req
  ~~~

* `PreemptiveResource`

  * 需要捕获`simpy.Interrupt`异常

  ~~~python
  import simpy
  
  def resource_user(name, env, resource, wait, prio):
      yield env.timeout(wait)
      with resource.request(priority=prio) as req:
          print(f'{name} requesting at {env.now} with priority={prio}')
          yield req
          print(f'{name} got resource at {env.now}')
          try:
              yield env.timeout(3)
          except simpy.Interrupt as interrupt:
              by = interrupt.cause.by
              usage = env.now - interrupt.cause.usage_since
              print(f'{name} got preempted by {by} at {env.now}'
                    f' after {usage}')
  env = simpy.Environment()
  res = simpy.PreemptiveResource(env, capacity=1)
  p1 = env.process(resource_user(1, env, res, wait=0, prio=0))
  p2 = env.process(resource_user(2, env, res, wait=1, prio=0))
  p3 = env.process(resource_user(3, env, res, wait=2, prio=-1))
  env.run()
  # 1 requesting at 0 with priority=0
  # 1 got resource at 0
  # 2 requesting at 1 with priority=0
  # 3 requesting at 2 with priority=-1
  # 1 got preempted by <Process(resource_user) object at 0x...> at 2 after 2
  # 3 got resource at 2
  # 2 got resource at 5
  ~~~

  	* 抢占式资源池继承自优先级资源池，在`Request`时手动指定`preempt=False`，可主动选择不抢占，如果所有进程都这样做，抢占式资源池的行为最终和优先级资源池一致；
  	* 优先级比抢占的优先级更高，如果前方有一个优先级更高的`Process`选择排队而不抢占，后面任何优先级更低的`Process`都无法抢占；
  	* 优先级的值越小，优先级越高。

## Containers

* Containers help you modelling the production and consumption of a homogeneous, undifferentiated bulk. It may either be continuous (like water) or discrete (like apples).
* `Container`类
  * `level`和`capacity`表示当前资源量和总容量
  * `get`和`put`方法
  * `put_queue`和`get_queue`属性

## Stores

* 使用`Store`可以模拟具体对象的生产和消耗，它可以保存不同种类的对象，除了`Store`，还有`FilterStore`和`PriorityStore`两种`Store`。前者可以使用自定义函数筛选从`Store`中取出来的物品，后者允许给物品设置优先级。
* `Store`
  * `item`返回当前物品列表
  * `capacity`表容量
  * `put_queue`和`get_queue`
* `FilterStore`
  * `machine = yield ms.get(lambda machine: machine.size == size)`
* `PriorityStore`
  * `class PriorityItem(NamedTuple)`，元祖中第一个元素是优先级，第二个是`item`
  * `simpy.PriorityItem('P2', '#0000')`
  * `p_store.put(simpy.PriorityItem('P1', 'xxx'))`

# Real-time Simulations

* `SimPy`支持实时仿真。
* 在使用实时仿真时，只需要简单地将`simpy.Environment()`替换为`simpy.rt.RealtimeEnvironment(initial_time=0,factor=0.1,strict=True)`即可
  * `factor`表示虚拟时间和真实时间之间的比值，例如当`factor=60`时，一单位虚拟时间等于实际时间的60秒
  * `strict`参数表示是否严格保持与真实时间的时序，当`strict=True`，如果仿真的`step`消耗的时间过多，计算复杂导致超时，则抛出`RuntimeError`异常；将`strict`设为`False`，则忽略该异常。处理逻辑是以逻辑时间为准，哪怕实际的处理时间超过下一`Event`应该发生的时间，也假设在下一时间触发前该事件也已经处理完毕。

# Monitor

## Monitoring Processes

* 很简单，可以把想保存的信息存到`list`里

## Resource usage

* 内置的`Resource`类无法直接访问，但是可以通过`Monkey-Patching`的方法来间接改变内置方法的行为

## Event tracing 

~~~python
from functools import partial, wraps
import simpy
def trace(env, callback):
    """Replace the ``step()`` method of *env* with a tracing function
    that calls *callbacks* with an events time, priority, ID and its
    instance just before it is processed.
    """
    def get_wrapper(env_step, callback):
        """Generate the wrapper for env.step()."""
        @wraps(env_step)
        def tracing_step():
            """Call *callback* for the next event if one exist before
            calling ``env.step()``."""
            if len(env._queue):
                t, prio, eid, event = env._queue[0]
                callback(t, prio, eid, event)
            return env_step()
        return tracing_step
    env.step = get_wrapper(env.step, callback)
def monitor(data, t, prio, eid, event):
    data.append((t, eid, type(event)))
def test_process(env):
    yield env.timeout(1)
data = []
# Bind *data* as first argument to monitor()
# see https://docs.python.org/3/library/functools.html#functools.partial
monitor = partial(monitor, data)
env = simpy.Environment()
trace(env, monitor)
p = env.process(test_process(env))
env.run(until=p)
for d in data:
    print(d)
# (0, 0, <class 'simpy.events.Initialize'>)
# (1, 1, <class 'simpy.events.Timeout'>)
# (1, 2, <class 'simpy.events.Process'>)
~~~

# Time and Scheduling

* 离散事件仿真需要注意几个问题
  * 一是时间精度的问题，如果精度过低，很多先后发生的事件只能被处理为同一时间发生；
  * 二是单线程模拟无法处理**同时发生**这个概念，只能退而求其次使用`FIFO`等队列模型处理同时发生的事件；
* Note that
  * In the real world, there’s usually no *at the same time*.
  * Discretization of the time scale can make events appear to be *at the same time*.
  * `SimPy` processes events *one after another*, even if they have the *same time*.
* `SimPy`的事件队列使用堆来实现，当安排一个新事件，向堆中插入`(t, event)`，`t`是时间；为了处理同一时间安排多个事件的情况，增加了一个严格递增的Event ID，实际向堆中插入`(t, eid, event)`，实现了FIFO。