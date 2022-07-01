            class App
                transactions = {}
                transactions_lock = Lock()
                scheduler = new Scheduler()
                validator_ref = Middleware.get_ref('validator')
                manager_ref = Middleware.get_ref('manager')
                state = _load_state()
                transactions = state['transactions']


                _load_state() -> dict:
                    res = None

                    count = 0

                    while res == None and count < 3:
                        count += 1
                        try:
                            res = read_file_with_lock(path)
                        except:
                            pass

                    if res == None:
                        // handle exception, e.g. shut everything down and do not commit anything
                        
                        task = schedule(time=now(), exit, args=[1])
                        

                    return res

                _save_state(state) -> int:
                    flag = 0

                    count = 0

                    while flag == 0 and count < 3:
                        count += 1
                        try:
                            flag = write_file_with_lock(path, state)

                            // returns 1 if success
                        except:
                            pass

                    if flag == 0:
                        // handle exception, e.g. shut everything down and do not commit anything
                        
                        task = schedule(time=now(), exit, args=[1])

                        return 1

                    return 0

                @expose
                function acquire(self, id: str) -> str:
                    return _new__transaction(user=id, kind='ACQUIRE')

                @expose
                function get_status(trans_id) - > str:
                    with transactions_lock.lock():
                        res = transactions[trans_id]['status']
                    
                    return res

                @expose
                function is_done(trans_id) -> int:
                    res = 0

                    with transactions_lock.lock():
                        if 'FAILED' == self.transactions[trans_id]['status'] or \
                            'COMMITED' == self.transactions[trans_id]['status'] or \
                                'ABORTED' == self.transactions[trans_id]['status']:
                            res = 1

                    return res

                @expose
                function notify_about_trans(trans_id, status) -> None:
                    with transactions_lock.lock():
                        t = transactions[trans_id]

                    res = 0

                    if 'FAILED' == status:
                        res = _cancel(trans_id, 'FAILED')
                    if 'ABORTED' == status:
                        res = _cancel(trans_id, 'ABORT')

                function _cancel(trans_id, new_status) -> int:
                    r = 0

                    with transactions_lock.lock():
                        transactions[trans_id]['status'] = new_status

                    _notify_members(trans_id)

                function _start_acquire(user, trans_id) -> None:
                    // asks validator and generator for something
                    // then calls the election proccess
                    // after that, decides and communicate the decision
                    // to the user

                    validator_ref.validate(trans_id, user)
                    manager_ref.prepare_resource(trans_id, user)

                    scheduler (time=now() + 15, get_votes, args=[trans_id])

                
                function _new_transaction(user, kind) -> str:
                    id = unique_id()
                    
                    with transactions_lock.lock():
                        transactions[id]['status'] = 'ACTIVE'
                        transactions[id]['user'] = user
                        transactions[id]['kind'] = kind
                        transactions[id]['members'] = [user, validator_ref.get_id(), manager_ref.get_id()]


                    if kind == 'ACQUIRE':
                        scheduler.add(time=now(), _start_acquire, args=[user, trans_id])

                    return id

                function _notify_members(trans_id) -> None:
                    with transactions_lock.lock():
                        t = transactions[trans_id]

                    for member_id in t['members']:
                        remote_ref = Middleware.get_ref(member_id)

                        remote_ref.notify_about_trans('{trans_id} {t['status']}')
                
                function _notify_user(trans_id) -> None:
                    with transactions_lock.lock():
                        t = transactions[trans_id]

                    remote_ref = Middleware.get_ref(t['user'])
                    remote_ref.notify_about_trans('{trans_id} {t['status']}')


                function get_votes(trans_id) -> None:
                    with transactions_lock.lock():
                        if transactions[trans_id]['status'] == 'ABORTED' or \
                            transactions[trans_id]['status'] == 'FAILED':
                            return

                    votes = 0

                    if validator_ref.get_status(trans_id) == 'SUCCESS':
                        votes+=1

                    if manager_ref.get_status(trans_id) == 'SUCCESS':
                        votes+=1

                    if votes == 2:
                        with transactions_lock.lock():
                            transactions[trans_id]['status'] = 'COMMITED'

                        r = _save_state()

                        if r == 1:
                            return
                        else:
                            _notify_user(trans_id)

                    elif votes < 2 and votes > 0:
                        with transactions_lock.lock():
                            if transactions[trans_id]['status'] == 'ACTIVE':
                                transactions[trans_id]['status'] = 'PARTIALLY_COMMITED'


                    
                            

