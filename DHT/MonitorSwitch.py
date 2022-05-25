from xdrlib import Packer
from xml.etree.ElementTree import ElementTree
from ns.switch.switch import FairPacketSwitch
from CMSketch import CountMinSketch
from collections.abc import Callable

class MonitorSwitchDHT(FairPacketSwitch):
    def __init__(self,
                 env,
                 nports: int,
                 port_rate: float,
                 buffer_size: int,
                 weights,
                 server: str,
                 flow_classes: Callable = lambda x: x,
                 element_id: str = "",
                 debug: bool = False) -> None:
        super().__init__(env, 
                        nports, 
                        port_rate, 
                        buffer_size,
                        weights, 
                        server, 
                        flow_classes, 
                        element_id, 
                        debug)
        self.element_id = element_id
        self.SKETCH = CountMinSketch(50, 3)
    
    def put(self, packet):
        # 测量
        self.SKETCH.add(packet.flow_id)
        # put
        self.demux.put(packet)

    def query(self, flow_id):
        return self.SKETCH[flow_id]
        
    def flip(self):
        print(f'Flip at switch({self.element_id})')
