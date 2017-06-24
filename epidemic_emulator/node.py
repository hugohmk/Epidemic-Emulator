import socket
import threading
import time
import random
from contextlib import closing


class Node(object):
    """Class that represents the network nodes"""


    def __init__(self, recovery_rate = 0.666, endogenous_infection_rate = 1.1, exogenous_infection_rate = 0.666):
        self._state = "S"
        self._initial_state = "S"
        self._neighbors = []
        self._stopped = False
        self._sock_closed = False

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
        neighbors = [n1,n2,...], ni = ("destIp","destPort")
        state = initial node state; can be "S" or "I" 
        """

        if (self._stopped):
            return False

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

        print "STOPPING NODE\n"
        self._stopped = True
        if not self._sock_closed: self._close_sock()
        
        self._infected.set()
        self._susceptible.set()
        
        #self._join_threads()

        self._infected.clear()
        self._susceptible.clear()


    def restart(self):
        """
        Restarts node activity: stops any current threads / sockets and restars them afterwards. 
        """
        print "restart STOP\n"
        self.stop()
        self._stopped = False
        self._sock_closed = False
        self.state = self._initial_state
        self._restart_threads()

        
    def _recovery(self):
        try:
            while self._stopped == False:
                self._infected.wait()
                print "Recovery Started\n"
                if self._stopped == True:
                    print "Recovery Stopped\n"
                    return
                if (self._susceptible.wait(random.expovariate(self.recovery_rate))):
                    print "Recovery Stopped\n"
                    return
                else:
                    if self._stopped == True:
                        print "Recovery Stopped\n"
                        return
                    self.state = "S"
                    print "Recovery!!!\n"
        except:
            print "Recovery exception\n"
        print "Recovery Stopped\n"
        return


    def _infect(self):
        print "Infect Started\n"
        while self._stopped == False:
            try:
                self._infected.wait()
                if self._stopped == True:
                    print "Infect Stopped\n"
                    return
                if (self._susceptible.wait(random.expovariate(self.exogenous_infection_rate))):
                    continue
                else:
                    if self._stopped == True:
                        print "Infect Stopped\n"
                        return
                    if len(self._neighbors):
                        rn = random.choice(self._neighbors)[1]
                        print rn
                        self._sock.sendto("I",rn)
                        
                    print "mandei I\n"
            except IOError as IOe:
                print "INFECT I/O error({0}): {1}".format(IOe.errno, IOe.strerror)
                #if not self._sock_closed: self._close_sock()
##        except:
##            self._close_sock()
    ##        finally:
    ##            if not self._sock_closed: self._close_sock()
        print "Infect Stopped\n"
        return


    def _infection(self):
        try:
            while self._stopped == False:
                self._susceptible.wait()
                print "Infection Started\n"
                if self._stopped == True:
                    print "Infection Stopped\n"
                    return
                if (self._infected.wait(random.expovariate(self.exogenous_infection_rate))):
                    #print "Infection Stopped\n"
                    #return
                    continue
                else:
                    if self._stopped == True:
                        print "Infection Stopped\n"
                        return
                    self.state = "I"
                    print "Infection!!!\n"
        except:
            print "Infection exception\n"
        print "Infection Stopped\n"
        return


    def _listener(self):
        print "Listener Started\n"
        while self._stopped == False:
            try:
                msg = self._sock.recvfrom(1024)
                print "recebi: " + str(msg) + "\n"
                if msg[0]=="F":
                   print "End sock msg received\n"
                   self.stop()
                   return
                elif msg[0]=="R":
                    self._sock.sendto("S "+self.state,msg[1])
                elif "S " in msg[0]:
                    print "TODO"
                elif msg[0]=="I":
                    self.state = "I"
            except IOError as IOe:
                print "LISTENER I/O error({0}): {1}".format(IOe.errno, IOe.strerror)
##            self._close_sock()
##            raise
##        except:
##            self._close_sock()
##        finally:
##            if not self._sock_closed: self._close_sock()
        print "Listener Stopped\n"
        return
    
        
    def _get_state(self):
        return self._state
    def _set_state(self, state):
        if state == "S":
            self._state = state
            self._infected.clear()
            self._susceptible.set()
        if state == "I":
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


    def _create_threads(self):
        self._recovery_thread = threading.Thread(target=self._recovery)
        self._infect_thread = threading.Thread(target=self._infect)
        self._infection_thread = threading.Thread(target=self._infection)
        self._listener_thread = threading.Thread(target=self._listener)
    

    def _start_threads(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1",self._port))
            
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

    def _close_sock(self):
        try:
            self._sock_closed = True
            self._sock.sendto("F",("localhost",self._port))
            self._sock.close()
##        except:
##            self._sock.close()
        finally:
            self._sock.close()


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print "__exit__ STOP\n"
        self.stop()
        


