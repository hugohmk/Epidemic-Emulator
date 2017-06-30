import socket
import threading
import time
import random
from datetime import datetime
from contextlib import closing
import matplotlib.pyplot as plt

class Node(object):
    """Class that represents the network nodes"""


    def __init__(self, recovery_rate = 1.0, endogenous_infection_rate = 1.0,
exogenous_infection_rate = 1.0):
        self._state = "S"
        self._initial_state = "S"
        self._neighbors = []
        self._stopped = False
        self._sock_closed = True

        self._recovery_rate = recovery_rate
        self._endogenous_infection_rate = endogenous_infection_rate
        self._exogenous_infection_rate = exogenous_infection_rate

        self._susceptible = threading.Event()
        self._infected = threading.Event()

        self._create_threads()


    def start(self, nd, neighbors=[]):
        """
        Starts node activity.
        port = port number for listener socket
        state = initial node state; can be "S" or "I"
        
        nd = node identifier tuple ('node_id', ('ip','port'), node_history)
        where node_history is a list of ('state', timedelta) with the successive
        states and differential timestamps where the transitions occurred.
        
        neighbors = list of all node identifiers present in the network
        """

        if (self._stopped or (nd is None)):
            return False

        self._st = datetime.now()

        self._nd = nd

        self._port = nd[1][1]
        self._stopped = False
        self._neighbors = neighbors

        self.state = "S"
        self.state = nd[2][0][0]
        self._initial_state = self.state

        self._start_threads()
        return True


    def stop(self):
        """
        Stops node activity (threads and sockets).
        """

        #print "STOPPING NODE "+self._nd[0]+"\n"
        self._stopped = True
        if not self._sock_closed: self._close_sock()

        self._infected.set()
        self._susceptible.set()

        #self._join_threads()

        self._infected.clear()
        self._susceptible.clear()


    def stopped(self):
        return self._stopped


    def restart(self):
        """
        Restarts node activity: stops any current threads / sockets and restars them afterwards.
        """
        print "restart STOP\n"
        self.stop()
        self._stopped = False

        self.state = self._initial_state
        self._restart_threads()


    def update(self):
        """
        Sends status update requests to all neighbors.
        """
        if self._sock_closed: return
        for i in self._neighbors:
            try:
                self._sock.sendto("R",i[1])
            except IOError as IOe:
                print "REQUEST I/O error({0}): {1}".format(IOe.errno, IOe.strerror)


    def _get_state(self):
        return self._state

    def _set_state(self, state):
        if state == "S":
            if self._state != state:
                self._nd[2].append((state,datetime.now()-self._st))
                self._broadcast_state()
            self._state = state
            self._infected.clear()
            self._susceptible.set()
        if state == "I":
            if self._state != state:
                self._nd[2].append((state,datetime.now()-self._st))
                self._broadcast_state()
            self._state = state
            self._susceptible.clear()
            self._infected.set()
    state = property(_get_state, _set_state)


    def _get_recovery_rate(self):
        return self._recovery_rate
    recovery_rate = property(_get_recovery_rate)


    def _get_endogenous_infection_rate(self):
        return self._endogenous_infection_rate
    endogenous_infection_rate = property(_get_endogenous_infection_rate)


    def _get_exogenous_infection_rate(self):
        return self._exogenous_infection_rate
    exogenous_infection_rate = property(_get_exogenous_infection_rate)


########## Simulation threads ##########

    def _recovery(self):
        try:
            while self._stopped == False:
                self._infected.wait()
                if self._stopped == True:
                    return
                if (self._susceptible.wait(random.expovariate(self.recovery_rate))):
                    return
                else:
                    if self._stopped == True:
                        return
                    self.state = "S"
        except:
            dmy=1
        return


    def _infect(self):
        while self._stopped == False:
            try:
                self._infected.wait()
                if self._stopped == True:
                    return
                if (self._susceptible.wait(random.expovariate(self.endogenous_infection_rate))):
                    continue
                else:
                    if self._stopped == True:
                        return
                    if len(self._neighbors):
                        rn = random.choice(self._neighbors)[1]
                        #print("Infecting neighbor " + str(rn))
                        self._sock.sendto("I",rn)

                    #print "mandei I\n"
            except IOError as IOe:
                print "INFECT I/O error({0}): {1}".format(IOe.errno, IOe.strerror)
                #if not self._sock_closed: self._close_sock()
##        except:
##            self._close_sock()
    ##        finally:
    ##            if not self._sock_closed: self._close_sock()
        #print "Infect Stopped\n"
        return


    def _infection(self):
        try:
            while self._stopped == False:
                self._susceptible.wait()
                if self._stopped == True:
                    return
                if (self._infected.wait(random.expovariate(self.exogenous_infection_rate))):
                    #return
                    continue
                else:
                    if self._stopped == True:
                        return
                    self.state = "I"
                    #print "exogenous infection"
        except:
            #print "Infection exception\n"
            dmy=1
        #print "Infection Stopped\n"
        return


    def _listener(self):
        while self._stopped == False:
            try:
                msg = self._sock.recvfrom(1024)
                
                # End sock message
                if msg[0]=="F":
                   self.stop()
                   return
                   
                # State update request
                elif msg[0]=="R":
                    self._sock.sendto("S:"+self.state,msg[1])
                    
                # State update reply
                elif ("S:" in msg[0]) and (len(msg[0])>2):
                    if msg[0][2] in ["S","I"]:
                        for i in xrange(len(self._neighbors)):
                            if self._neighbors[i][1]==msg[1]:
                                self._neighbors[i][2].append((msg[0][2],datetime.now()-self._st))
                
                # Endogenous infection message
                elif msg[0]=="I":
                    self.state = "I"
                    
            except IOError as IOe:
                print "LISTENER I/O error({0}): {1}".format(IOe.errno, IOe.strerror)
##            self._close_sock()
##        except:
##            self._close_sock()
##        finally:
##            if not self._sock_closed: self._close_sock()
        #print "Listener Stopped\n"
        return


    def _broadcast_state(self):
        """
        Sends current state to all available neighbors.
        Message format: "S:`self.state`"
        """
        for i in self._neighbors:
            try:
                if (not self._stopped) and (not self._sock_closed):
                    self._sock.sendto("S:"+self.state,i[1])
                else:
                    break
            except IOError as IOe:
                print "BROADCAST I/O error({0}): {1}".format(IOe.errno, IOe.strerror)


########## Visualizing state information ##########

    def network_state(self):
        """
        Returns a list of the all the node identifier tuples in the network
        containing only the latest state in node_history.
        
        A node identifier tuple is
        
            ('node_id', ('ip','port'), node_history)
        
        where node_history is a list of ('state', timedelta) with the successive
        states and differential timestamps where the transitions occurred.
        """
        # should we update before returning?
        return [(self._nd[0], self._nd[1], [self._nd[2][-1]])] \
            + [(i[0],i[1],[i[2][-1]]) for i in self._neighbors]


    def network_history(self):
        """
        Returns a list of the all the node identifier tuples in the network
        containing full node_history.
        """
        # should we update before returning?
        return [self._nd]+self._neighbors


    def print_state(self):
        #self.update()
        netstat = self.network_state()
        infected_nodes = []
        susceptible_nodes = []
        for i in netstat:
            node_state = i[2][0][0]
            if node_state == 'I':
                infected_nodes.append(i[0])
            elif node_state == 'S':
                susceptible_nodes.append(i[0])

        print('%d nodes, %d susceptible, %d infected' % \
            tuple(map(len,[netstat,susceptible_nodes,infected_nodes])) )
        print('susceptible nodes: ' + ','.join(susceptible_nodes))
        print('infected nodes: ' + ','.join(infected_nodes))

    def print_history(self):
        #self.update()
        nethist = self.network_history()
        for i in nethist:
            node_id = i[0]
            print("Node " + node_id + ":")
            node_history = i[2]
            history = []
            for state in node_history:
                #print(state)
                node_state = state[0]
                node_time = state[1].total_seconds()
                state_string = "(%s, %.4f)" % (node_state,node_time)
                history.append(state_string)
            print(', '.join(history))

    display_state = print_state

    def display_history(self):
        #self.update()
        history_records = []
        nethist = self.network_history()
        for i in nethist:
            node_id = i[0]
            node_history = i[2]
            for state in node_history:
                node_state = state[0]
                node_time = state[1].total_seconds()
                # this test is just to disconsider the initial state of each node
                if node_time > 0.0:
                    history_records.append( (node_id, node_state, node_time) )

        history_records = sorted(history_records, key=lambda x: x[2])
        # stats is initialized with the initial state of each node
        stats = dict( (i[0], i[2][0][0]) for i in nethist )
        infected_count = 0
        for i in stats:
            if stats[i] == 'I':
                infected_count = infected_count+1

        event_times = [0.0]
        infected_numbers = [0]
        for r in history_records:
            #print(r)
            if r[1] == 'I' and stats[r[0]] == 'S':
                stats[r[0]] = r[1]
                infected_count = infected_count+1
                event_times.append(r[2])
                infected_numbers.append(infected_count)
                print("%.4f\t%d" % (r[2],infected_count))

            elif r[1] == 'S' and stats[r[0]] == 'I':
                stats[r[0]] = r[1]
                infected_count = infected_count-1
                event_times.append(r[2])
                infected_numbers.append(infected_count)
                print("%.4f\t%d" % (r[2],infected_count))

#           else:
#               print("nada acontece, feijoada")

        plt.plot(event_times,infected_numbers,'-o')
        plt.show()

########## Thread manipulation ##########

    def _create_threads(self):
        self._recovery_thread = threading.Thread(target=self._recovery)
        self._infect_thread = threading.Thread(target=self._infect)
        self._infection_thread = threading.Thread(target=self._infection)
        self._listener_thread = threading.Thread(target=self._listener)


    def _start_threads(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1",self._port))
        self._sock_closed = False

        self._recovery_thread.start()
        self._infect_thread.start()
        self._infection_thread.start()
        self._listener_thread.start()


    def _join_threads(self):
        self._recovery_thread.join()
        self._infect_thread.join()
        self._infection_thread.join()
        self._listener_thread.join()


    def _restart_threads(self):
        self._create_threads()
        self._start_threads()

########## Exiting simulation ##########

    def _close_sock(self):
        try:
            self._sock_closed = True
            self._sock.sendto("F",("localhost",self._port))
            self._sock.close()
        finally:
            self._sock.close()

    def network_shutdown(self):
        if self._sock_closed: return
        for i in self._neighbors:
            try:
                self._sock.sendto("F",i[1])
            except IOError as IOe:
                print "SHUTDOWN I/O error({0}): {1}".format(IOe.errno, IOe.strerror)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        #print "__exit__ STOP\n"
        self.stop()
