from Pyro4 import expose, behavior, Daemon, locateNS, Proxy
import pandas as pd

@expose
@behavior(instance_mode="single")
class Validator():
    def __init__(self) -> None:
        self.users = pd.read_csv('./user_list.csv')
        self.coordinator_ref = Proxy(
            "PYRONAME:{0}"
            .format('server.coordinator')
        )

    def validate(self, user_id):
        # Search DataFrame for user
        return True

if __name__ == '__main__':
    daemon = Daemon()                # make a Pyro daemon
    ns = locateNS()                  # find the name server
    
    # register the Validator as a Pyro object
    uri = daemon.register(Validator)
    
    # register the object with a name in the name server
    ns.register("server.validator", uri)
