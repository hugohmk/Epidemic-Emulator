from epidemic_emulator import node
from datetime import datetime
import argparse

def parse_network(f, node_id):
    network = {}
    for i in f:
        i = i.rstrip("\n").split("|")
        if len(i)<3:
            return network
        network[i[0]]=[(i[1],int(i[2])),[(i[3],datetime.now())]]
    f.close()
    return network




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-id","--identifier",required=True,
                        help="Node identifier")
    parser.add_argument("-n","--network",type=argparse.FileType('r'), default="rede.txt",
                        help="File that contains the network's description; each line presents node_id|node_ip|port_number|initial_state")
    parser.add_argument("-i","--interactive",type=int,default=0,
                        help="Interactive mode")
    args = parser.parse_args()

    network = {}
    if args.network is not None:
        network = parse_network(args.network, args.identifier)
    if args.identifier in network:
        with node.Node() as a:
            port = network[args.identifier][0][1]
            state = network[args.identifier][1][0]
            a.start(port, network, state)
            if args.interactive:
                help_text = """
                Commands:
                0 (help) -> print this
                1 (update) -> request for neighbors states
                2 (print) -> print current network state
                3 (end) -> send shutdown message to all nodes"""
                print help_text
                while True:
                    opt = raw_input(">> Insert command: ")
                    if opt == "0":
                        print help_text
                    elif opt == "1":
                        a.update()
                        print "Requests sent!\n"
                    elif opt == "2":
                        a.network_state()
                    elif opt == "3":
                        a.network_shutdown()
                        a.stop()
                    else:
                        print "Invalid input\n"
