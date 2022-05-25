from random import sample
import networkx as nx

from ns.flow.flow import Flow


def read_topo(fname):
    ftype = ".graphml"
    if fname.endswith(ftype):
        return nx.read_graphml(fname)
    else:
        print(f"{fname} is not GraphML")


def generate_flows(G, hosts, nflows):
    all_flows = dict()
    for flow_id in range(nflows):
        src, dst = sample(hosts, 2)
        # print("Generating flows")
        # print(src)
        # print(dst)
        all_flows[flow_id] = Flow(flow_id, src, dst)
        all_flows[flow_id].path = sample(
            list(nx.all_simple_paths(G, src, dst, cutoff=nx.diameter(G))),
            1)[0]
    return all_flows


def generate_fib(G, all_flows):
    for n in G.nodes():
        node = G.nodes[n]

        node['port_to_nexthop'] = dict()
        node['nexthop_to_port'] = dict()

        # 建立端口与邻居节点交换机之间的映射
        for port, nh in enumerate(nx.neighbors(G, n)):
            node['nexthop_to_port'][nh] = port
            node['port_to_nexthop'][port] = nh

        # print(node['nexthop_to_port'])
        # print(node['port_to_nexthop'])

        # 建立流与端口的映射
        # 该流的出端口
        node['flow_to_port'] = dict()
        # 该流的下一跳
        node['flow_to_nexthop'] = dict()

    # 遍历流
    for f in all_flows:
        flow = all_flows[f]
        path = list(zip(flow.path, flow.path[1:]))
        for seg in path:
            a, z = seg
            # flow to port，从哪个端口出去，达到z？
            G.nodes[a]['flow_to_port'][
                flow.fid] = G.nodes[a]['nexthop_to_port'][z]
            # flow to nexthop，这个流的下一跳？
            G.nodes[a]['flow_to_nexthop'][flow.fid] = z

    return G
