class GlobalController:
    def __init__(self, env, interval = 100, finish = float("inf"), topo = None):
        self.env = env
        self.interval = interval
        self.topo = topo
        self.finish = finish
        self.action = env.process(self.run())

    def run(self):
        while self.env.now < self.finish:
            yield self.env.timeout(self.interval)
            print(f"Flip at time {self.env.now}")
            
            for node_id in self.topo.nodes():
                node = self.topo.nodes[node_id]
                if node['type'] == 'switch':
                    node['device'].flip()