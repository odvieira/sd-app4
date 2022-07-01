import json
from Pyro4 import expose, behavior, Daemon, locateNS, Proxy
from random import randint


@expose
@behavior(instance_mode="single")
class Generator():
    state = None

    def __init__(self) -> None:
        self._load_state()

        self.coordinator_ref = Proxy(
            "PYRONAME:{0}"
            .format('server.coordinator')
        )

    def _load_state(self):
        with open('./generator_main_state.csv', 'r') as json_file:
            self.state = json.load(json_file)

    def _save_main_state(self):
        pass

    def _save_partial_state(self, s):
        pass

    def generate_resource(
            self, trans_id, increment: int = 0, decrement: int = 0) -> None:
        
        success = 0
        if randint(1, 100) + increment - decrement > 50:
            success = 1
        
        self.state['transactions'][trans_id]['vote'] = success

        

    def _to_vote(self, trans_id, vote) -> None:
        self.coordinator_ref.send_vote(vote, trans_id, 'Generator')


if __name__ == '__main__':
    daemon = Daemon()                # make a Pyro daemon
    ns = locateNS()                  # find the name server

    # register the Generator as a Pyro object
    uri = daemon.register(Generator)

    # register the object with a name in the name server
    ns.register("server.generator", uri)
