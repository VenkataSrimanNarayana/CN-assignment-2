from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
import argparse  # for options
import re  # for regex
import matplotlib.pyplot as plt  # for plotting


# Defining the network topology
class NetworkTopo(Topo):
    def build(self, **_opts):
        # H1 and H2 connected to S1
        s1 = self.addSwitch("s1")
        h1 = self.addHost("h1", ip="192.168.0.1/24")
        h2 = self.addHost("h2", ip="192.168.0.2/24")
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        # H3 and H4 connected to S2
        s2 = self.addSwitch("s2")
        h3 = self.addHost("h3", ip="192.168.0.3/24")
        h4 = self.addHost("h4", ip="192.168.0.4/24")
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # S1 and S2 connected
        self.addLink(s1, s2, cls=TCLink, loss=_opts["link_loss"])


# Process the output of iperf3
def process_output(o: str):
    throughput_list = o.split("\n")
    # find the line starting with [ ID]
    for i in range(len(throughput_list)):
        if throughput_list[i].startswith("[ ID]"):
            break
    throughput_list = throughput_list[i + 1 : -1]
    # get the throughput values from the list where each string can be compared to a regex [0-9.]* [A-Za-z]*/[A-Za-z]*
    throughput_list = [
        float(re.search(r"([0-9.]*) [A-Za-z]*/[A-Za-z]*", x).groups(1)[0])
        for x in throughput_list
    ]
    return throughput_list


# TCP client server program
def simulate_client_server(
    net: Mininet, congestion_control: str, config: str, link_loss: int
):
    # Get the hosts from the network
    h1 = net.get("h1")
    h2 = net.get("h2")
    h3 = net.get("h3")
    h4 = net.get("h4")
    if not congestion_control:
        congestion_control_list = ["Vegas", "Reno", "Cubic", "BBR"]
    else:
        congestion_control_list = [congestion_control]
    if config == "b":
        for cc in congestion_control_list:
            # Start the server on h4 using iperf using the congestion control algorithm
            h4.cmd("iperf -s -p 80 -i 0.1 " + cc.lower() + " &")

            # Start the client on h1 using iperf using the congestion control algorithm
            o = h1.cmd("iperf -c 192.168.0.4 -t 10 -f M -p 80 -i 0.1 -Z " + cc.lower())

            # Obtain the throughput list from the output
            throughput_list = process_output(o)
            # plot the throughput list
            plt.plot(
                [0.1 * i for i in range(0, len(throughput_list))],
                throughput_list,
                label=cc.lower(),
            )
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (Mbps)")
        plt.title("Throughput vs Time with link loss " + str(link_loss) + "%")
        plt.legend()
        if not congestion_control:
            plt.savefig("images/q2_b_all_cc_" + str(link_loss) + ".png")
        else:
            plt.savefig(
                "images/q2_b_"
                + congestion_control.lower()
                + "_"
                + str(link_loss)
                + ".png"
            )
        plt.close()

        # Close the server on h4 after the client has finished
        h4.cmd("killall -9 iperf3")

    elif config == "c":
        h1_throughput_list = []
        h2_throughput_list = []
        h3_throughput_list = []
        for cc in congestion_control_list:
            # Start the server on h4 using iperf
            h4.cmd("iperf -s -p 80 -i 0.1 " + cc.lower() + " &")

            # Start the clients using iperf using popen
            p1 = h1.popen(
                "iperf -c 192.168.0.4 -t 10 -f M -p 80 -i 0.1 -Z "
                + cc.lower()
                + " >> q2_c_"
                + cc.lower()
                + "_h1.txt",
                shell=True,
            )
            p2 = h2.popen(
                "iperf -c 192.168.0.4 -t 10 -f M -p 80 -i 0.1 -Z "
                + cc.lower()
                + " >> q2_c_"
                + cc.lower()
                + "_h2.txt",
                shell=True,
            )
            p3 = h3.popen(
                "iperf -c 192.168.0.4 -t 10 -f M -p 80 -i 0.1 -Z "
                + cc.lower()
                + " >> q2_c_"
                + cc.lower()
                + "_h3.txt",
                shell=True,
            )
            p1.wait()
            p2.wait()
            p3.wait()

            # Close the server on h4 after the client has finished
            h4.cmd("killall -9 iperf3")

            # Read the output files
            with open("q2_c_" + cc.lower() + "_h1.txt", "r") as f:
                o1 = f.read()
                h1_throughput_list.append(process_output(o1))
            with open("q2_c_" + cc.lower() + "_h2.txt", "r") as f:
                o2 = f.read()
                h2_throughput_list.append(process_output(o2))
            with open("q2_c_" + cc.lower() + "_h3.txt", "r") as f:
                o3 = f.read()
                h3_throughput_list.append(process_output(o3))
            # Remove the output files
            h1.cmd("rm q2_c_" + cc.lower() + "_h1.txt")
            h2.cmd("rm q2_c_" + cc.lower() + "_h2.txt")
            h3.cmd("rm q2_c_" + cc.lower() + "_h3.txt")

        if congestion_control:
            # plot the throughput list
            plt.plot(
                [0.1 * i for i in range(0, len(h1_throughput_list[0]))],
                h1_throughput_list[0],
                label="h1",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h2_throughput_list[0]))],
                h2_throughput_list[0],
                label="h2",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h3_throughput_list[0]))],
                h3_throughput_list[0],
                label="h3",
            )
            plt.xlabel("Time (s)")
            plt.ylabel("Throughput (Mbps)")
            plt.title("Throughput vs Time for " + congestion_control.lower())
            plt.legend()
            plt.savefig("images/q2_c_" + congestion_control.lower() + ".png")
            plt.close()
        else:
            # plot the throughput list of h1 for all congestion control algorithms
            plt.plot(
                [0.1 * i for i in range(0, len(h1_throughput_list[0]))],
                h1_throughput_list[0],
                label="Vegas",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h1_throughput_list[1]))],
                h1_throughput_list[1],
                label="Reno",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h1_throughput_list[2]))],
                h1_throughput_list[2],
                label="Cubic",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h1_throughput_list[3]))],
                h1_throughput_list[3],
                label="BBR",
            )
            plt.xlabel("Time (s)")
            plt.ylabel("Throughput (Mbps)")
            plt.title("Throughput vs Time for h1")
            plt.legend()
            plt.savefig("images/q2_c_h1.png")
            plt.close()

            # plot the throughput list of h2 for all congestion control algorithms
            plt.plot(
                [0.1 * i for i in range(0, len(h2_throughput_list[0]))],
                h2_throughput_list[0],
                label="Vegas",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h2_throughput_list[1]))],
                h2_throughput_list[1],
                label="Reno",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h2_throughput_list[2]))],
                h2_throughput_list[2],
                label="Cubic",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h2_throughput_list[3]))],
                h2_throughput_list[3],
                label="BBR",
            )
            plt.xlabel("Time (s)")
            plt.ylabel("Throughput (Mbps)")
            plt.title("Throughput vs Time for h2")
            plt.legend()
            plt.savefig("images/q2_c_h2.png")
            plt.close()

            # plot the throughput list of h3 for all congestion control algorithms
            plt.plot(
                [0.1 * i for i in range(0, len(h3_throughput_list[0]))],
                h3_throughput_list[0],
                label="Vegas",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h3_throughput_list[1]))],
                h3_throughput_list[1],
                label="Reno",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h3_throughput_list[2]))],
                h3_throughput_list[2],
                label="Cubic",
            )
            plt.plot(
                [0.1 * i for i in range(0, len(h3_throughput_list[3]))],
                h3_throughput_list[3],
                label="BBR",
            )
            plt.xlabel("Time (s)")
            plt.ylabel("Throughput (Mbps)")
            plt.title("Throughput vs Time for h3")
            plt.legend()
            plt.savefig("images/q2_c_h3.png")
            plt.close()


if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument(
        "-c",
        "--config",
        help="configuration, choose according to the question from {b, c}",
        required=True,
    )
    parser.add_argument(
        "-cc",
        "--congestion-control",
        help="congestion control algorithm to use. Choose from {Vegas, Reno, Cubic, and BBR}",
    )
    parser.add_argument(
        "-ll",
        "--link-loss",
        help="link loss(in percentage) of the s1-s2 link",
    )

    # Read arguments from command line
    args = parser.parse_args()
    if not args.link_loss:
        args.link_loss = 0
    args.link_loss = int(args.link_loss)

    setLogLevel("info")
    # Creating a topology according to the value of the config option
    topo = NetworkTopo(link_loss=args.link_loss)
    net = Mininet(topo=topo, waitConnected=True)

    net.start()

    # run the client server program
    simulate_client_server(net, args.congestion_control, args.config, args.link_loss)

    net.stop()
