from Pyro4 import expose, behavior, Daemon, locateNS, Proxy

class Validator():
    def __init__(self) -> None:
        pass

if __name__ == '__main__':
    daemon = Daemon()                # make a Pyro daemon
    ns = locateNS()                  # find the name server
    
    # register the Validator as a Pyro object
    uri = daemon.register(Validator)
    
    # register the object with a name in the name server
    ns.register("server.validator", uri)
