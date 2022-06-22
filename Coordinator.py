from threading import Lock
from uuid import uuid4
from Pyro4 import expose, behavior, Daemon, locateNS, Proxy
from sched import scheduler
from time import monotonic

@expose
@behavior(instance_mode="single")
class Coordinator():
    def __init__(self) -> None:
        self.transactions = {}
        self.scheduler = scheduler()
        self.clients = []

        pass

    @expose
    def acquire(self, id:str) -> str:
        return self._transaction(
            user=id,
            kind='ACQUIRE'
        )

    def _foobar(self) -> None:
        # asks validator and generator for something
        # then calls the election proccess
        # after that, decides and communicate the decision
        # to the user
        pass


    def _transaction(self, user:str, kind:str) -> str:
        """_summary_

        Args:
            source_id (str): _description_
            target_id (str): _description_
            value (int): _description_

        Returns:
            str: [ACTIVE | P_COMMITED | FAILED | ABORTED | COMMITED]
        """        
        
        id = uuid4().hex
        self.transactions[id]['status'] = 'ACTIVE'
        self.transactions[id]['user'] = user
        self.transactions[id]['kind'] = kind

        self.scheduler.enterabs(
            time=monotonic(),
            priority=1,
            action=self._foobar
        )

        return id

    def _notify_members(self, trans_id) -> None:
        self.transactions[trans_id]

        for member in self.transactions[trans_id]['members']:
            remote_ref = Proxy(
                "PYRONAME:{0}.callback"
                .format(member))

            remote_ref.notify(
                '{0} {1}'.format(
                    trans_id,
                    self.transactions[trans_id]['status'] 
                )
        )

    def transaction_ok(self, trans_id, user_id) -> bool:
        return True

    def get_decision(self, trans_id) -> bool:
        return True

    def _get_votes(self, trans_id):
        pass

if __name__ == '__main__':
    daemon = Daemon()                # make a Pyro daemon
    ns = locateNS()                  # find the name server
    
    # register the Coordinator as a Pyro object
    uri = daemon.register(Coordinator)
    
    # register the object with a name in the name server
    ns.register("server.coordinator", uri)

    