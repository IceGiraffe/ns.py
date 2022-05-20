# Current Network Components

The network components that have already been implemented include:

* `Packet`: a simple representation of a network packet, carrying its creation time, size, packet id, flow id, source and destination.
  * 网络中的数据包，记录了这个包的创建时间、大小、包ID、流ID、源地址和目的地址
  * 源文件[Packet](..%5Cns%5Cpacket%5Cpacket.py)
* `DistPacketGenerator`: generates packets according to provided distributions of inter-arrival times and packet sizes.
  * 基于某种包间隔数据分布和包大小数据分布的包生成器；
  * 源文件[DistPacketGenerator](..%5Cns%5Cpacket%5Cdist_generator.py)  
* `TracePacketGenerator`: generates packets according to a trace file, with each row in the trace file representing a packet.
  * 根据Trace文件生成包，Trace文件的每一行代表一个包
  * 源文件[TracePacketGenerator](..%5Cns%5Cpacket%5Ctrace_generator.py)
* `TCPPacketGenerator`: generates packets using TCP as the transport protocol.
  * 生成TCP报文[TCPPacketGenerator](..%5Cns%5Cpacket%5Ctcp_generator.py)
* `ProxyPacketGenerator`: redirects real-world packets (with fixed packet sizes) into the simulation environment.
  * 代理，将OS中实际的包（要求包是固定长度）重定向到仿真环境中
  * 源文件[ProxyPacketGenerator](..%5Cns%5Cpacket%5Cproxy_generator.py)
* `PacketSink`: receives packets and records delay statistics.
  * 接收数据包，记录统计数据
  * 源文件[PacketSink](..%5Cns%5Cpacket%5Cproxy_sink.py)
* `TCPSink`: receives packets, records delay statistics, and produces acknowledgements back to a TCP sender.
  * 接收数据包，记录统计数据，然后向发送者发送ACK报文
  * 源文件[TCPSink](..%5Cns%5Cpacket%5Ctcp_sink.py)
* `ProxySink`: redirects all received packets to a destination real-world TCP server.
  * 把所有收到的包重定向到一个真实世界的TCP Server
  * 源文件[ProxySink](..%5Cns%5Cpacket%5Cproxy_sink.py)
* `Port`: an output port on a switch with a given rate and buffer size (in either bytes or the number of packets), using the simple tail-drop mechanism to drop packets.
  * 交换机的一个出端口，可以设置速率和缓冲区大小（可以设置为总包数或总的字节数），使用尾部丢弃处理队列溢出问题
  * 源文件[Port](..%5Cns%5Cport%5Cport.py)
* `REDPort`: an output port on a switch with a given rate and buffer size (in either bytes or the number of packets), using the Early Random Detection (RED) mechanism to drop packets.
  * 使用随机早期检测RED来丢包的队列
  * 源文件[REDPort](..%5Cns%5Cport%5Cred_port.py)
* `Wire`: a network wire (cable) with its propagation delay following a given distribution. There is no need to model the bandwidth of the wire, as that can be modeled by its upstream `Port` or scheduling server.
  * 网络中的传输介质，在介质中的传输时延服从某个给定的分布，抽象介质没有模拟带宽，因为“带宽”可以有上游的`Port`或调度服务器建模
  * 源文件[Wire](..%5Cns%5Cport%5Cwire.py)
* `Splitter`: a splitter that simply sends the original packet out of port 1 and sends a copy of the packet out of port 2.
  * 2路复制包
  * 源文件[Splitter](..%5Cns%5Cutils%5Csplitter.py)
* `NWaySplitter`: an n-way splitter that sends copies of the packet to *n* downstream elements.
  * N路包复制，将一个包复制N份然后发送到N个下游元素
  * 源文件[Splitter](..%5Cns%5Cutils%5Csplitter.py)
* `TrTCM`: a two rate three color marker that marks packets as green, yellow, or red (refer to RFC 2698 for more details).
  * 双速率三色桶
  * 源文件[TrTCM](..%5Cns%5Cutils%5Cmisc.py)
* `RandomDemux`: a demultiplexing element that chooses the output port at random.
  * 随机选择出端口的多路分配元素，好像指的处理不同种类的IP报文
  * 源文件[RandomDemux](..%5Cns%5Cdemux%5Crandom_demux.py)
* `FlowDemux`: a demultiplexing element that splits packet streams by flow ID.
  * 按流ID多路分配元素
  * 源文件[FlowDemux](..%5Cns%5Cdemux%5Cflow_demux.py)
* `FIBDemux`: a demultiplexing element that uses a Flow Information Base (FIB) to make packet forwarding decisions based on flow IDs.
  * 根据FIB表信息，对流ID进行包转发
  * 源文件[FIBDemux](..%5Cns%5Cdemux%5Cfib_demux.py)
* `TokenBucketShaper`: a token bucket shaper.
  * 令牌桶
  * 源文件[TokenBucketShaper](..%5Cns%5Cshaper%5Ctoken_bucket.py)
* `TwoRateTokenBucketShaper`: a two-rate three-color token bucket shaper with both committed and peak rates/burst sizes.
  * 双速率三色令牌桶，承诺数据和峰值速率/突发大小
  * [TwoRateTokenBucketShaper](..%5Cns%5Cshaper%5Ctwo_rate_token_bucket.py)
* `SPServer`: a Static Priority (SP) scheduler.
  * 固定优先级调度器
  * 源文件[SP](..%5Cns%5Cscheduler%5Csp.py)
* `WFQServer`: a Weighted Fair Queueing (WFQ) scheduler.
  * 加权公平队列调度器WFQ
  * 源文件[WFQ](..%5Cns%5Cscheduler%5Cwfq.py)
* `DRRServer`: a Deficit Round Robin (DRR) scheduler.
  * 差分轮询调度器，总的原则是每个队列发送的包的大小尽可能相等
  * 源文件[DRR](..%5Cns%5Cscheduler%5Cdrr.py)
* `VirtualClockServer`: a Virtual Clock scheduler.
  * 虚拟时钟调度器
  * 源文件[VirtualClock](..%5Cns%5Cscheduler%5Cvirtual_clock.py)
* `SimplePacketSwitch`: a packet switch with a FIFO bounded buffer on each of the outgoing ports.
  * 单队列固定缓冲区大小的FIFO队列
  * 源文件[switch.py](..%5Cns%5Cswitch%5Cswitch.py)
* `FairPacketSwitch`: a fair packet switch with a choice of a WFQ, DRR, Static Priority or Virtual Clock scheduler, as well as bounded buffers, on each of the outgoing ports. It also shows an example how a simple hash function can be used to map tuples of (flow_id, node_id, and port_id) to class IDs, and then use the parameter `flow_classes` to activate class-based scheduling rather than flow_based scheduling.
  * 公平队列
  * 源文件[switch.py](..%5Cns%5Cswitch%5Cswitch.py)
* `PortMonitor`: records the number of packets in a `Port`. The monitoring interval follows a given distribution.
  * Monitor，记录`Port`种包的个数，监控间隔服从给定分布
  * 源文件[PortMonitor](..%5Cns%5Cport%5Cmonitor.py)
* `ServerMonitor`: records performance statistics in a scheduling server, such as `WFQServer`, `VirtualClockServer`, `SPServer`, or `DRRServer`.
  * 记录调度服务器的性能，比如`WFQServer`, `VirtualClockServer`, `SPServer`, 以及 `DRRServer`
  * 源文件[ServerMonitor](..%5Cns%5Cscheduler%5Cmonitor.py)

## Current utilities

* `TaggedStore`: a sorted `simpy.Store` based on tags, useful in the implementation of WFQ and Virtual Clock.
  * 带标签的存储，在WFQ和虚拟时钟算法中有用
  * 源文件[TaggedStore](..%5Cns%5Cutils%5Ctaggedstore.py)
* `Config`: a global singleton instance that reads parameter settings from a configuration file. Use `Config()` to access the instance globally.
  * 全局单例对象，从配置文件中读取参数设置，可以使用`Config()`全局访问该对象
  * 源文件[Config](..%5Cns%5Cutils%5Cconfig.py)
