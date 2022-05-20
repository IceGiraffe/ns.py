from functools import partial
from random import expovariate, sample

import numpy as np
import simpy

from ns.packet.dist_generator import DistPacketGenerator
from ns.packet.sink import PacketSink
from ns.switch.switch import SimplePacketSwitch
from ns.switch.switch import FairPacketSwitch
from ns.topos.fattree import build as build_fattree
from ns.topos.utils import generate_fib, generate_flows

import matplotlib.pyplot as plt
import networkx as nx

from pprint import pprint

env = simpy.Environment()

n_flows = 100
k = 4
pir = 100000
buffer_size = 1000
mean_pkt_size = 100.0

ft = build_fattree(k)
nx.draw(ft, with_labels = ft.nodes)
# plt.show()

pprint("Fat Tree({}) with {} nodes.".format(k, ft.number_of_nodes()))

hosts = set()
for n in ft.nodes():
    if ft.nodes[n]['type'] == 'host':
        hosts.add(n)

# 提取host
pprint("All Hosts {}".format(hosts))

# 生成流量
all_flows = generate_flows(ft, hosts, n_flows)
pprint(all_flows)


size_dist = partial(expovariate, 1.0 / mean_pkt_size)

for fid in all_flows:
    arr_dist = partial(expovariate, 1 + np.random.rand())

    pg = DistPacketGenerator(env,
                             f"Flow_{fid}",
                             arr_dist,
                             size_dist,
                             flow_id=fid)
    ps = PacketSink(env)

    all_flows[fid].pkt_gen = pg
    all_flows[fid].pkt_sink = ps

ft = generate_fib(ft, all_flows)

n_classes_per_port = 4
weights = {c: 1 for c in range(n_classes_per_port)}


def flow_to_classes(f_id, n_id=0, fib=None):
    return (f_id + n_id + fib[f_id]) % n_classes_per_port


for node_id in ft.nodes():
    # 为每个node增加网卡
    node = ft.nodes[node_id]
    # node['device'] = SimplePacketSwitch(env, k, pir, buffer_size, element_id=f"{node_id}")
    flow_classes = partial(flow_to_classes,
                           n_id=node_id,
                           fib=node['flow_to_port'])
    # env: 模拟环境
    # k: switch端口数
    # pir: port_rate
    # buffer_size: buffer_size
    # weights: 1, 1, 1, 1
    # 'DRR'
    # flow_classes: a function mapping flow id to class id
    # element_id = node_id
    node['device'] = FairPacketSwitch(env,
                                      k,
                                      pir,
                                      buffer_size,
                                      weights,
                                      'DRR',
                                      flow_classes,
                                      element_id=f"{node_id}")
    # pprint(f'{node_id}')
    node['device'].demux.fib = node['flow_to_port']

# 连接交换机出端口
for n in ft.nodes():
    node = ft.nodes[n]
    for port_number, next_hop in node['port_to_nexthop'].items():
        node['device'].ports[port_number].out = ft.nodes[next_hop]['device']

# pkt_gen连接src，dst连接pkt_sink
for flow_id, flow in all_flows.items():
    flow.pkt_gen.out = ft.nodes[flow.src]['device']
    ft.nodes[flow.dst]['device'].demux.ends[flow_id] = flow.pkt_sink

env.run(until=2)

for flow_id in sample(all_flows.keys(), 1):
    pprint(f"Flow {flow_id}")
    pprint("Packets Wait")
    pprint(all_flows[flow_id].pkt_sink.waits)
    pprint("Packet Arrivals")
    pprint(all_flows[flow_id].pkt_sink.arrivals)
    pprint("Arrival Perhop Times")
    pprint(all_flows[flow_id].pkt_sink.perhop_times)
    # pprint(all_flows[flow_id].pkt_sink.packet_times)
