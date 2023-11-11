from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


# Router class Ref: https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py
class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    # pylint: disable=arguments-differ
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


# Defining the network topology
class NetworkTopo(Topo):
    def build(self, **_opts):
        # h1 and h2 connected to ra
        ra = self.addHost("ra", cls=LinuxRouter, ip="192.168.0.0/24")
        s1 = self.addSwitch("s1")
        self.addLink(s1, ra, intfName2="ra-eth1", params2={"ip": "192.168.0.0/24"})
        h1 = self.addHost("h1", ip="192.168.0.1/24", defaultRoute="via 192.168.0.0")
        h2 = self.addHost("h2", ip="192.168.0.2/24", defaultRoute="via 192.168.0.0")
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        # h3 and h4 connected to rb
        rb = self.addHost("rb", cls=LinuxRouter, ip="192.168.1.0/24")
        s2 = self.addSwitch("s2")
        self.addLink(s2, rb, intfName2="rb-eth1", params2={"ip": "192.168.1.0/24"})
        h3 = self.addHost("h3", ip="192.168.1.1/24", defaultRoute="via 192.168.1.0")
        h4 = self.addHost("h4", ip="192.168.1.2/24", defaultRoute="via 192.168.1.0")
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # h5 and h6 connected to rc
        rc = self.addHost("rc", cls=LinuxRouter, ip="192.168.2.0/24")
        s3 = self.addSwitch("s3")
        self.addLink(s3, rc, intfName2="rc-eth1", params2={"ip": "192.168.2.0/24"})
        h5 = self.addHost("h5", ip="192.168.2.1/24", defaultRoute="via 192.168.2.0")
        h6 = self.addHost("h6", ip="192.168.2.2/24", defaultRoute="via 192.168.2.0")
        self.addLink(h5, s3)
        self.addLink(h6, s3)

        # Connecting ra-rb, rb-rc, rc-ra
        self.addLink(
            ra,
            rb,
            intfName1="ra-eth2",
            intfName2="rb-eth2",
            params1={"ip": "192.168.3.0/24"},
            params2={"ip": "192.168.3.1/24"},
        )
        self.addLink(
            rb,
            rc,
            intfName1="rb-eth3",
            intfName2="rc-eth2",
            params1={"ip": "192.168.4.0/24"},
            params2={"ip": "192.168.4.1/24"},
        )
        self.addLink(
            rc,
            ra,
            intfName1="rc-eth3",
            intfName2="ra-eth3",
            params1={"ip": "192.168.5.0/24"},
            params2={"ip": "192.168.5.1/24"},
        )


if __name__ == "__main__":
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)
    setLogLevel("info")

    # Adding static routes to the routers
    info("***Adding static routes to the routers***\n")

    # Default for h1 -> ra -> rc -> h6
    info(net["ra"].cmd("ip route add 192.168.1.0/24 via 192.168.3.1 dev ra-eth2"))
    info(net["ra"].cmd("ip route add 192.168.2.0/24 via 192.168.5.0 dev ra-eth3"))
    info(net["rb"].cmd("ip route add 192.168.0.0/24 via 192.168.3.0 dev rb-eth2"))
    info(net["rb"].cmd("ip route add 192.168.2.0/24 via 192.168.4.1 dev rb-eth3"))
    info(net["rc"].cmd("ip route add 192.168.0.0/24 via 192.168.5.1 dev rc-eth3"))
    info(net["rc"].cmd("ip route add 192.168.1.0/24 via 192.168.4.0 dev rc-eth2"))

    # # For h1-> ra -> rb -> rc -> h6
    # info(net["ra"].cmd("ip route add 192.168.1.0/24 via 192.168.3.1 dev ra-eth2"))
    # info(net["ra"].cmd("ip route add 192.168.2.0/24 via 192.168.3.1 dev ra-eth2"))
    # info(net["rb"].cmd("ip route add 192.168.0.0/24 via 192.168.3.0 dev rb-eth2"))
    # info(net["rb"].cmd("ip route add 192.168.2.0/24 via 192.168.4.1 dev rb-eth3"))
    # info(net["rc"].cmd("ip route add 192.168.0.0/24 via 192.168.4.0 dev rc-eth2"))
    # info(net["rc"].cmd("ip route add 192.168.1.0/24 via 192.168.4.0 dev rc-eth2"))

    net.start()

    # Print the routing tables of the routers
    info("***Routing tables***\n")
    info(net["ra"].cmd("route"))
    info(net["rb"].cmd("route"))
    info(net["rc"].cmd("route"))

    CLI(net)
    net.stop()
