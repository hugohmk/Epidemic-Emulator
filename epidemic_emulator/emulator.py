import node


class Emulator:
    """Class that handles an epidemic emulation network in one single host"""
    def __init__(self, n = 10, recovery_rate = 2, infection_rate = 2):
        self.nodes_list = [node.Node() for i in xrange(n)]
        self.recovery_rate = recovery_rate
        self.infection_rate = infection_rate

    #TODO
    def start():
        return 0
