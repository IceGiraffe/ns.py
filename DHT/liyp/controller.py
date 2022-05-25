class Controller:
    def __init__(self, env, topo, interval):
        self.env = env
        self.interval = interval
        self.topo = topo
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(self.interval)
            print("flip at time %d" % self.env.now)
            for node_id in self.topo.nodes():
                node = self.topo.nodes[node_id]
                if node['type'] == 'switch':
                    node['device'].flip()

