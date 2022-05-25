from functools import partial
from random import expovariate, sample
from tkinter.tix import Tree

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
from ZipfPacketGenerator import ZipfPacketGenerator

env = simpy.Environment()

n_flows = 100
k = 4
pir = 100000    # port rate
buffer_size = 1000
mean_pkt_size = 100.0   # 平均包大小100，认为是指数分布

ft = build_fattree(k)   # 构建fat tree topology
# nx.draw(ft, with_labels = ft.nodes) # nx draw 一下
# plt.show()

pprint("Fat Tree({}) with {} nodes.".format(k, ft.number_of_nodes()))

hosts = set()   # 找到所有服务器，fat tree的流量都是从一台服务器到另一台服务器的
for n in ft.nodes():
    if ft.nodes[n]['type'] == 'host':
        hosts.add(n)

# 提取host
pprint("All Hosts {}".format(hosts))

# 生成流量
all_flows = generate_flows(ft, hosts, n_flows)
pprint(all_flows)

# size distribution: expovariate distribution 
# with lambda = 1.0 / mean_pkt_size, which means E(size) = mean_pkt_size
size_dist = partial(expovariate, 1.0 / mean_pkt_size)

true_flow_size = dict()

for fid in all_flows:
    arr_dist = partial(expovariate, 1 + np.random.rand())   #设置流量的包间隔

    pg = ZipfPacketGenerator(env,
                             f"Flow_{fid}",
                             arr_dist,
                             size_dist,
                             flow_id=fid,
                             alpha=1.5)

    true_flow_size[fid] = pg.flow_size

    ps = PacketSink(env)

    all_flows[fid].pkt_gen = pg
    all_flows[fid].pkt_sink = ps

print(sorted(true_flow_size.items(), key = lambda x: x[1], reverse=True))

max_flow_id = max(true_flow_size.values())

print(f'The size of biggest flow is {max_flow_id}')

ft = generate_fib(ft, all_flows)

n_classes_per_port = 4
weights = {c: 1 for c in range(n_classes_per_port)}


def flow_to_classes(f_id, n_id=0, fib=None):
    return (f_id + n_id + fib[f_id]) % n_classes_per_port

# 遍历fat tree的每个节点
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
                                      element_id=f"Switch_{node_id}")
    # pprint(f'{node_id}')
    # 下一跳
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

env.run()

for flow_id in all_flows:
    f = all_flows[flow_id]
    print(f'Flow {flow_id}: flow_size = {f.pkt_gen.flow_size} and packets_sent = {f.pkt_gen.packets_sent}')


for flow_id in sample(all_flows.keys(), 1):
    flow_id = 26
    pprint(f"Flow {flow_id}")
    pprint("Packets Wait")
    pprint(all_flows[flow_id].pkt_sink.waits)
    pprint("Packet Arrivals")
    pprint(all_flows[flow_id].pkt_sink.arrivals)
    pprint("Arrival Perhop Times")
    pprint(all_flows[flow_id].pkt_sink.perhop_times)
    # pprint(all_flows[flow_id].pkt_sink.packet_times)
