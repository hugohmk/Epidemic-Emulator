from epidemic_emulator import node
from datetime import datetime
import platform
import argparse
import time
import os
import matplotlib.pyplot as plt
import random

def parse_network(f, node_id, topology = "clique"):
    neighbors = []
    nd = None
    t = datetime.now()
    t = t-t
    
    net = []
    index = -1
    cnt = 0

    for i in f:
        i = i.rstrip("\n").split("|")
        if len(i)<4:
            continue
        u = (i[0],(i[1],int(i[2])),[(i[3],t)])
        if i[0]==node_id:
            nd = u
            index = cnt 
        net.append(u)
        cnt+=1
    f.close()
    
    # clique
    if topology == "clique":
        neighbors = [i for i in net if i[0] != node_id]

    # star
    elif topology == "star":
        if index > 0:
            neighbors = [net[0]]
        else:
            neighbors = net[1:]
            
    return neighbors,nd
    
def simulation_controller(args,nd,network):
    
    # Example nd value:
    #('9', ('127.0.0.1', 9179), [('S', datetime.timedelta(0))])
    #
    # network is a tuple containing every node identifier constructed from 
    # args.network (default=network.txt) file

    r = args.recovery_rate
    e = args.endogenous_rate
    x = args.exogenous_rate
     
    if nd is not None:
        with node.Node(r,e,x) as a:
            
            a.start(nd, network)
            
            if args.interaction == 1:
                try:
                    help_text = """>> Commands:
        0 (help) -> print this
        1 (print current) -> print current network state
        2 (print history) -> print network history
        3 (end) -> send shutdown message to all nodes
        4 (display state) -> display current network state
        5 (display history) -> display network history
        """
                    print help_text
                    while True:
                        opt = raw_input(">> Insert command: ")
                        if opt == "0":
                            print help_text
                        elif opt == "1":
                            #print a.network_state(),"\n"
                            a.print_state()
                        elif opt == "2":
                            #print a.network_history(),"\n"
                            a.print_history()
                        elif opt == "3":
                            a.display_history()
                            a.network_shutdown()
                            a.stop()
                            break
                        elif opt == "4":
                            a.display_state()
                        elif opt == "5":
                            a.display_history()
                        else:
                            print "Invalid input\n"
                except:
                    a.network_shutdown()
                    a.stop()
                finally:
                    a.network_shutdown()
                    a.stop()
                    
            elif args.interaction > 1:
                print("Running simulation for %d seconds." % args.interaction)
                time.sleep(args.interaction)
                #a.display_history()
                simdata = a.save_simulation_data()
                a.network_shutdown()
                a.stop()
                return simdata
                
            else:
                try:
                    while not a.stopped():
                        time.sleep(2)
                except:
                    a.stop()
                finally:
                    a.stop()

def process_data(simdata,repetitions,simulation_time):
    
    simresults = [[-1 for t in range(simulation_time+1)] for x in range(repetitions)]
    print_stuff = 1
    
    for k in range(repetitions):
        if print_stuff:
            print("")
            print("Run #%d" % (k+1))
            print("time\tinfected count")

        t = 0

        for event in simdata[k]:
            if print_stuff: print("%.2f\t%d" % (event[0],event[1]))
            time = int(event[0])
            infected_count = event[1]
            
            if time < t:
                continue
            elif t < simulation_time+1:
                if print_stuff: print("* %.2f" % event[0])
                while t <= time:
                    simresults[k][t] = infected_count
                    t = t+1
        while t < simulation_time+1:
            simresults[k][t] = infected_count
            t = t+1
            
        if print_stuff:
            print("")
            print("Processed output:")
            print("time\tinfected count")
            for t in range(simulation_time+1):
                print("%d\t%d" % (t,simresults[k][t]))
        
    average_results = [0.0 for t in range(simulation_time+1)]
    for t in range(simulation_time+1):
        for k in range(repetitions):
            average_results[t] = average_results[t] + simresults[k][t]
        average_results[t] = float(average_results[t]) / repetitions
        
    print(average_results)
        
    plt.plot(list(range(0,simulation_time+1)),average_results,'-o')
    axes = plt.gca()
    axes.set_xlim([0,simulation_time])
    #axes.set_ylim([0,10])
    plt.xlabel("Seconds")
    plt.ylabel("Infected nodes")
    plt.savefig("average_simulation.pdf")



if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path_unix = dir_path.replace("\\","/")
    if (platform.system()!="Windows"): dir_path = dir_path_unix

    
    parser = argparse.ArgumentParser()
    parser.add_argument("-id","--identifier",required=True,
                        help="Node identifier")
    parser.add_argument("-n","--network",type=argparse.FileType('r'), default = dir_path_unix+"/network.txt",
                        help="File that contains the network's description; each line presents node_id|node_ip|port_number|initial_state")
#    parser.add_argument("-i","--interactive",type=int,default=0,
#                        help="Interactive mode")
    parser.add_argument("-i","--interaction",type=int,default=0,
                        help="Interaction mode: default (0), interactive (1), simulation (2)")
    parser.add_argument("-r","--recovery_rate",type=float,#default=1.0,
                        help="Simulation parameter: recovery_rate")
    parser.add_argument("-e","--endogenous_rate",type=float,#default=1.0,
                        help="Simulation parameter: endogenous_infection_rate")
    parser.add_argument("-x","--exogenous_rate",type=float,#default=1e-6,
                        help="Simulation parameter: exogenous_infection_rate")
    parser.add_argument("-t","--topology",choices=["clique","star"],default="clique",
                        help="Network topology: clique or star")
    args = parser.parse_args()
    
    network = {}
    if args.network is not None:
        network,nd = parse_network(args.network, args.identifier, args.topology)
        
    simulation_time = args.interaction
    
    repetitions = 1
    simdata = []
    for i in range(repetitions):
        simdata.append(simulation_controller(args,nd,network))
        
    if args.identifier == '0':
        process_data(simdata,repetitions,simulation_time)

