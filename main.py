from epidemic_emulator import node
from datetime import datetime
import argparse

def parse_network(f, node_id):
    neighbors = []
    nd = None
    for i in f:
        i = i.rstrip("\n").split("|")
        if len(i)<3:
            return neighbors
        if i[0]==node_id:
            nd = (i[0],(i[1],int(i[2])),[(i[3],datetime.now())])
        else:
            neighbors.append((i[0],(i[1],int(i[2])),[(i[3],datetime.now())]))
    f.close()
    return neighbors,nd




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
        network,nd = parse_network(args.network, args.identifier)
    if nd is not None:
        with node.Node() as a:
            #print network
            a.start(nd, network)
            if args.interactive:
                try:
                    help_text = """
                    Commands:
                    0 (help) -> print this
                    1 (update) -> request for n9eighbors states
                    2 (print) -> print current network state
                    3 (end) -> send shutdown message to all nodes"""
                    print help_text
                    while True:
                        opt = raw_input(">> Insert command: ")
                        if opt == "0":
                            print help_text
                        elif opt == "1":
                            #a.update()
                            print "Requests sent!\n"
                        elif opt == "2":
                            a.network_state()
                            print "states\n"
                        elif opt == "3":
                            #a.network_shutdown()
                            a.stop()
                            break
                        else:
                            print "Invalid input\n"
##                except:
##                    a.stop()
                finally:
                    a.stop()
