from epidemic_emulator import node
from datetime import datetime
import platform
import argparse
import time
import os


def parse_network(f, node_id):
    neighbors = []
    nd = None
    t = datetime.now()
    t = t-t
    for i in f:
        i = i.rstrip("\n").split("|")
        if len(i)<4:
            return neighbors
        if i[0]==node_id:
            nd = (i[0],(i[1],int(i[2])),[(i[3],t)])
        else:
            neighbors.append((i[0],(i[1],int(i[2])),[(i[3],t)]))
    f.close()
    return neighbors,nd




if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_unix = dir_path.replace("\\","/")
    if (platform.system()!="Windows"): dir_path = dir_path_unix

    
    parser = argparse.ArgumentParser()
    parser.add_argument("-id","--identifier",required=True,
                        help="Node identifier")
    parser.add_argument("-n","--network",type=argparse.FileType('r'), default = dir_path_unix+"/network.txt",
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
                    help_text = """>> Commands:
        0 (help) -> print this
        1 (print current) -> print current network state
        2 (print history) -> print network history
        3 (end) -> send shutdown message to all nodes"""
                    print help_text
                    while True:
                        opt = raw_input(">> Insert command: ")
                        if opt == "0":
                            print help_text
                        elif opt == "1":
                            print a.network_state(),"\n"
                        elif opt == "2":
                            print a.network_history(),"\n"
                        elif opt == "3":
                            a.network_shutdown()
                            a.stop()
                            break
                        else:
                            print "Invalid input\n"
                except:
                    a.network_shutdown()
                    a.stop()
                finally:
                    a.network_shutdown()
                    a.stop()
            else:
                try:
                    while not a.stopped():
                        time.sleep(2)
                except:
                    a.stop()
                finally:
                    a.stop()
