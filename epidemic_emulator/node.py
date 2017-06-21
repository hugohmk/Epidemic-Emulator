import socket
import threading
import time
import random


class Node(object):
    """Class that represents the network nodes"""


    def __init__(self, recovery_rate = 0.2, endogenous_infection_rate = 1.1, exogenous_infection_rate = 0.2):
        self._state = "S"
        self._initial_state = "S"
        self._neighbors = []
        self._stopped = False

        self._recovery_rate = recovery_rate
        self._endogenous_infection_rate = endogenous_infection_rate
        self._exogenous_infection_rate = exogenous_infection_rate

        self._susceptible = threading.Event()
        self._infected = threading.Event()

        self._create_threads()


    def start(self, port, neighbors=[], state = "S"):
        """
        Starts node activity.
        port = port number for listener socket
        neighbors = [n1,n2,...], ni = ("destIp","destPort")
        state = initial node state; can be "S" or "I" 
        """

        if (self._stopped):
            return False

        self._stopped = False
        self._neighbors = neighbors
        self.state = "S"
        self.state = state
        self._initial_state = self.state
        
        self._start_threads()
        
        return True


    def stop(self):
        """
        Stops node activity (threads and sockets). 
        """
        self._stopped = True
        self._infected.set()
        self._susceptible.set()
        
        self._recovery_thread.join()
        self._infect_thread.join()
        self._infection_thread.join()
        self._listener_thread.join()

        self._infected.clear()
        self._susceptible.clear()


    def restart(self):
        """
        Restarts node activity: stops any current threads / sockets and restars them afterwards. 
        """
        self.stop()
        self._stopped = False
        self.state = self._initial_state
        self._restart_threads()

        
    def _recovery(self):
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
        print "Recovery Stopped\n"
        return


    #TODO
    def _infect(self):
        print "Infect Started\n"
        print "Infect Stopped\n"
        return


    def _infection(self):
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
        print "Infection Stopped\n"
        return


    #TODO
    def _listener(self):
        print "Listener Started\n"
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
        self._recovery_thread.start()
        self._infect_thread.start()
        self._infection_thread.start()
        self._listener_thread.start()


    def _restart_threads(self):
        self._create_threads()
        self._start_threads()
        


