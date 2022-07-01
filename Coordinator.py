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

        self.validator_ref = Proxy(
            "PYRONAME:{0}"
            .format('server.validator')
        )

        self.generator_ref = Proxy(
            "PYRONAME:{0}"
            .format('server.generator')
        )

    @expose
    def acquire(self, id: str) -> str:
        return self._transaction(
            user=id,
            kind='ACQUIRE'
        )

    @expose
    def get_status(self, trans_id) -> str:
        return self.transactions[trans_id]['status']

    @expose
    def is_done(self, trans_id) -> int:
        if 'FAILED' == self.transactions[trans_id]['status'] or \
            'COMMITED' == self.transactions[trans_id]['status'] or \
                'ABORTED' == self.transactions[trans_id]['status']:
            return 1

        return 0

    def _start_acquire(self, user_id) -> None:
        # asks validator and generator for something
        # then calls the election proccess
        # after that, decides and communicate the decision
        # to the user

        self.validator_ref.validate(user_id)
        pass

    def _transaction(self, user: str, kind: str) -> str:
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

        if kind == 'ACQUIRE':
            self.scheduler.enterabs(
                time=monotonic(),
                priority=1,
                action=self._start_acquire
            )

        return id

    def _notify_members(self, trans_id) -> None:
        self.transactions[trans_id]

        for member_id in self.transactions[trans_id]['members']:
            remote_ref = Proxy(
                "PYRONAME:{0}.callback"
                .format(member_id))

            remote_ref.notify(
                '{0} {1}'.format(
                    trans_id,
                    self.transactions[trans_id]['status']
                )
            )

    def _get_votes(self, trans_id):
        pass


if __name__ == '__main__':
    daemon = Daemon()                # make a Pyro daemon
    ns = locateNS()                  # find the name server

    # register the Coordinator as a Pyro object
    uri = daemon.register(Coordinator)

    # register the object with a name in the name server
    ns.register("server.coordinator", uri)

    # start the event loop of the server to wait for calls
    daemon.requestLoop()
