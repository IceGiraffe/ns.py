from ns.switch.switch import SimplePacketSwitch

class MonitorSwitch(SimplePacketSwitch):
    def __init__(self,
                 env,
                 nports: int,
                 port_rate: float,
                 buffer_size: int,
                 element_id: str = "",
                 debug: bool = False) -> None:
        self.id = element_id
        self.count = dict()
        super(MonitorSwitch, self).__init__(env, nports, port_rate, buffer_size, element_id, debug)


    def put(self, packet):
        self.count.setdefault(packet.flow_id, 0)
        self.count[packet.flow_id] += 1
        self.demux.put(packet)


    def flip(self):
        print(self.id, self.count)
        self.count = dict()

