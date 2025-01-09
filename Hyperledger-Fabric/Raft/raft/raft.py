#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

from builtins import str
from builtins import range
from past.utils import old_div

import time
import json
import random
import threading
from queue import Queue, Empty

from .interface import Listener, Talker

from .protocol import MessageType, MessageDirection, RequestVotesResults, \
    AppendEntriesResults, RequestVotesMessage, AppendEntriesMessage, \
    parse_json_message


address_book_fname = 'address_book.json'
total_nodes = 1
local_ip = '127.0.0.1'
start_port = 5557

class RaftNode(threading.Thread):
    def __init__(self, config, name, role='follower', verbose=True):
        threading.Thread.__init__(self) 
        
        self._terminate = False
        self.daemon = True

        self.verbose = verbose

    
        self.client_queue = Queue()
        self.client_lock = threading.Lock()

   
        if (isinstance(config, dict)):
            address_book = config
        else:
            address_book = self._load_config(config, name)
        self.all_ids = [address_book[a]['ip'] + ':' + address_book[a]['port'] for a in address_book if a != 'leader']
        self.my_id = address_book[name]['ip'] + ':' + address_book[name]['port']

     
        self.election_timeout = random.uniform(0.1, 0.1+0.05*len(self.all_ids))
        self.heartbeat_frequency = 0.01                                    
        self.resend_time = 2.0                                            

      
        self._name = name                                              
        self.current_num_nodes = len(self.all_ids)                    
        self.current_role = role                                     
        self.leader_id = None                                           
        
        # Persistent state variables
        self.current_term = 1                                           
        self.voted_for = None                                            
        self.log = [{'term': 1, 'entry': 'Init Entry', 'id': -1}]         
        self.log_hash = {}
    
        # Volatile state variables
        self.commit_index = 0                                          
        self.last_applied_index = 0                                        
        self.last_applied_term = 1                                      

        # Volotile state leader variables 
        self.next_index = [None for _ in range(self.current_num_nodes)] 
        self.match_index = [0 for _ in range(self.current_num_nodes)]    
        self.heard_from = [0 for _ in range(self.current_num_nodes)]    
        # Start both ends of your interface
        identity = {'my_id': self.my_id, 'my_name': name}
        self.listener = Listener(port_list=self.all_ids, identity=identity)
        self.listener.start()
        self.talker = Talker(identity=identity)
        self.talker.start()

    def stop(self):
        self.talker.stop()
        self.listener.stop()
        self._terminate = True

    @property
    def name(self):
        ''' Return the name of the node. '''
        return self._name
        
    def client_request(self, value, id_num=-1):
        '''
            client_request: Public function to enqueue a value. If the node
                is not the leader, this request will be forewarded to the 
                leader before being appended. If the system is in a transition
                state, the request may not be appended at all, so this should 
                be retried. If no id_num is specified, the id is set to -1.
            Inputs:
                value: any singleton data type.
                id_num: any immutable object.
        '''

        entry = {
            'term': self.current_term,
            # 'entry': value,
            'entry': "Akhilesh",
            'id': id_num
        }
        self.client_queue.put(entry)

    def check_committed_entry(self, id_num=None):
        ''' 
            check_committed_entry: Public function to check the last entry 
                committed. Optionally specify an id_num to search for. If 
                specified, will return the most recent entry with this id_num. 
            Inputs:
                id_num: returns the most recent entry with this id_num. 
        '''
        if (id_num is None):
            with self.client_lock:
                return self.log[self.commit_index]['entry']
        with self.client_lock:
            return self.log_hash.get(id_num, None)

    def check_role(self):
        ''' 
            check_role: Public function to check the role of a given node.
        '''
        with self.client_lock:
            return self.current_role

    def pause(self):
        '''
            pause: Allows the user to pause a node. In this state nodes are 
                "removed" from the system until un_pause is called. 
        '''
        self._set_current_role('none')
        if (self.verbose):
            print(self._name + ': pausing...')
        
    def un_pause(self):
        '''
            un_pause: Allows the user to unpause a node. If the node was not 
                already paused, does nothing.
        '''
        if (self.check_role() == 'none'):
            self._set_current_role('follower')
            if (self.verbose):
                print(self._name + ': unpausing...')
        else:
            if (self.verbose):
                print(self._name + ': node was not paused, doing nothing')

    def run(self):
        '''
            run: Called when the node starts. Facilitates state transitions. 
        '''
        # Wait for the interface to be ready
        time.sleep(self.listener.initial_backoff)

        # Your role determines your action. Every time a state chance occurs, this loop will facilitate a transition to the next state. 
        try:
            while not self._terminate:
                if self.check_role() == 'leader':
                    self._leader()
                elif self.check_role() == 'follower':
                    self._follower()
                elif self.check_role() == 'candidate':
                    self._candidate()
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    def process_client_request(self, entry, start_time):
        ''' Process a client request (append to log or forward to leader) '''
   
        self.log.append(entry)
        self.commit_index += 1

     
        latency = (time.time() - start_time) * 1000  # Latency in ms
        self.total_latency += latency
        
        if self.verbose:
            print(f"Processed client request with latency: {latency:.2f} ms")

    
        self.request_count += 1
        current_time = time.time()

  
        if current_time - self.last_throughput_time >= 1:
            throughput = self.request_count
            avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
            print(f"Throughput: {throughput} requests/sec, Average Latency: {avg_latency:.2f} ms")

            # Reset for the next second
            self.last_throughput_time = current_time
            self.request_count = 0
            self.total_latency = 0

    def _follower(self):
        ''' 
            _follower: Nodes will start here if they have been newly added to 
                the network. The responsibilities of the follower nodes are:
                    - Respond to election requests with a vote if the candidate 
                        is more up-to-date than they are. 
                    - Replicate entries sent by the leader. 
                    - Commit entries committed by the leader. 
                    - Promote self to candidate if the leader has crashed. 
        ''' 

     
        most_recent_heartbeat = time.time()

        while ((not self._terminate) and (self.check_role() == 'follower')):
            incoming_message = self._get_message()
            if (incoming_message is not None):

                if (incoming_message.direction == MessageDirection.Request):

                 
                    if (incoming_message.type == MessageType.RequestVotes):

                     
                        if (incoming_message.term > self.current_term):
                            self._increment_term(incoming_message.term)
                            
                      
                        if ((self.voted_for is None) and (incoming_message.last_log_index >= self.last_applied_index) and (incoming_message.last_log_term >= self.last_applied_term)):
                            self._send_vote(incoming_message.sender)
                        else: 
                            self._send_vote(incoming_message.sender, False)

                     
                        most_recent_heartbeat = time.time()

               
                    elif (incoming_message.type == MessageType.Heartbeat):
                        if (incoming_message.term > self.current_term):
                            self._increment_term(incoming_message.term)
                        self.leader_id = incoming_message.leader_id
                        most_recent_heartbeat = time.time()

                
                        if (self.leader_id):
                            client_request = self._get_client_request()
                            if (client_request is not None):
                                self._send_client_request(incoming_message.leader_id, client_request)
                        
               
                    elif (incoming_message.type == MessageType.AppendEntries):
                        
                   
                        if (incoming_message.term < self.current_term):
                            self._send_acknowledge(incoming_message.leader_id, False)

                    
                        elif (not self._verify_entry(incoming_message.prev_log_index, incoming_message.prev_log_term)):
                            self._send_acknowledge(incoming_message.leader_id, False)

                      
                        else:
                            if (incoming_message.leader_commit > self.commit_index):
                                self._append_entry(incoming_message.entries, commit=True, prev_index=incoming_message.prev_log_index)
                            else:
                                self._append_entry(incoming_message.entries, commit=False, prev_index=incoming_message.prev_log_index)
                            self._send_acknowledge(incoming_message.leader_id, True)
                    
                
                    elif (incoming_message.type == MessageType.Committal):
                        self._commit_entry(incoming_message.prev_log_index, incoming_message.prev_log_term)

       
            if ((time.time() - most_recent_heartbeat) > (self.election_timeout)):
                self._set_current_role('candidate')
                return

        return

    def _candidate(self):
        ''' 
            _candidate: Nodes will start here if they have not heard the leader 
                for a period of time. The responsibilities of the candidate 
                nodes are:
                    - Call for a new election and await the results: 
                    - If you recieve more than half of the votes in the system, 
                        promote yourself. 
                    - If you see someone else starting an election for a term 
                        higher than your own, vote for them, update yourself, 
                        and then demote yourself. 
                    - If you see a heartbeat for a term higher than or equal to 
                        your own, update yourself, and then demote yourself. 
                    - If you have not won after the election timeout, restart 
                        the election. 
        ''' 

        if(self.verbose):
            print(self._name + ': became candidate')

    
        self._increment_term()

        self._send_request_vote()

        self._send_vote(self.my_id, True)

        votes_for_me = 0
        total_votes = 0
        election_start_time = time.time()


        time_election_going = time.time()

        while ((not self._terminate) and (self.check_role() == 'candidate')):
            incoming_message = self._get_message()
            if (incoming_message is not None):

          
                if (incoming_message.direction == MessageDirection.Response):
                
         
                    if (incoming_message.type == MessageType.RequestVotes):
                        if (incoming_message.results.vote_granted):
                            votes_for_me += 1
                        total_votes += 1

                            
                        if ((votes_for_me > int(old_div(self.current_num_nodes, 2))) or (self.current_num_nodes == 1)):
                            self._set_current_role('leader')
                            election_end_time = time.time()
                            # print(f"Leader election completed in {election_end_time - election_start_time:.2f} seconds.")
                            print(f"Leader election completed in {(election_end_time - election_start_time) * 1000:.2f} milliseconds.")
                            return

          
                elif (incoming_message.direction == MessageDirection.Request):

               
                    if (incoming_message.type == MessageType.RequestVotes):
                        if (incoming_message.term > self.current_term):
                            self._increment_term(incoming_message.term)
                            self._send_vote(incoming_message.sender)
                            self._set_current_role('follower')
                            return

                
                    elif (incoming_message.type == MessageType.Heartbeat):
                        if (incoming_message.term >= self.current_term):
                            self._increment_term(incoming_message.term)
                            self.leader_id = incoming_message.leader_id
                            self._set_current_role('follower')
                            return
            
        
            if ((time.time() - time_election_going) > self.election_timeout):
                if(self.verbose):
                    print(self._name + ': election timed out')
                self._set_current_role('candidate')
                return
        
        return

    def _leader(self):
        ''' 
            _leader: Nodes will start here if they have won an election and 
                promoted themselves. The responsibilities of the leader nodes 
                are:
                    - Send a periodic heartbeat. 
                    - Keep track of who is active in the system and their 
                        status. This is done using self.next_index and 
                        self.match_index.
                    - Accept client requests and replicate them on the system. 
                        When a new request is made, send an append entries to 
                        all up-to-date nodes and away a response. When  more 
                        than half of the nodes respond, commit that entry. 
                    - Catch up nodes that are behind by resending append 
                        entries after a short amount of time. 
                    - If there's a vote going on with a term term higher than 
                        your own, vote for them, update yourself, and then 
                        demote yourself. 
        ''' 
        
        if(self.verbose):
            print(self._name + ': became leader')

  
        self._send_heartbeat()

      
        most_recent_heartbeat = time.time()

      
        self.match_index = [self.commit_index for _ in range(self.current_num_nodes)]
        self.next_index = [None for _ in range(self.current_num_nodes)]

    
        self.heard_from = [time.time() for _ in range(self.current_num_nodes)]

        entry = {'term': self.current_term, 'entry': 'Leader Entry', 'id': -1}
        self._broadcast_append_entries(entry)

        while ((not self._terminate) and (self.check_role() == 'leader')):

  
            if ((time.time() - most_recent_heartbeat) > self.heartbeat_frequency):
                self._send_heartbeat()
                most_recent_heartbeat = time.time()
                if (self.verbose):
                    pass
                    #print(self._name + ': sent heartbeat')
                    #print(self._name + ': max committed index: ' + str(self.commit_index))

   
            for node, index in enumerate(self.next_index):
                if ((index is not None) and ((time.time() - self.heard_from[node]) > self.resend_time)):
                    self._send_append_entries(index - 1, self.log[index - 1]['term'], self.log[index], self.all_ids[node])
                    self.heard_from[node] = time.time()

          
            incoming_message = self._get_message()
            if (incoming_message is not None):

          
                if (incoming_message.direction == MessageDirection.Response):

              
                        sender_index = self._get_node_index(incoming_message.sender)
                        self.heard_from[sender_index] = time.time()

                    
                        if (self.next_index[sender_index] is not None):

                                                    if (incoming_message.results.success):
                                self.match_index[sender_index] = self.next_index[sender_index]
                                self.next_index[sender_index] += 1
                            else:
                                if (self.next_index[sender_index] != 1):
                                    self.next_index[sender_index] -= 1

                       
                            if self.next_index[sender_index] > self._log_max_index():
                                self.next_index[sender_index] = None
                            else:
                                next_index = self.next_index[sender_index]
                                self._send_append_entries(next_index - 1, self.log[next_index - 1]['term'], self.log[next_index], incoming_message.sender)
                            
                            if (self.verbose):
                                print(self._name + ": updated standing is " + str(self.match_index) + " my index: " + str(self._log_max_index()))

                            log_lengths = [int(i) for i in self.match_index if (i is not None)]
                            log_lengths.sort(reverse=True)
                            max_committable_index = 0
                            for index in log_lengths:
                                # Count how many other nodes this index is replicated on
                                replicated_on = sum([1 if index <= i else 0 for i in log_lengths])
                                if (replicated_on >= (int(old_div(self.current_num_nodes, 2)) + 1)):
                                    max_committable_index = index

                            if (max_committable_index > self.commit_index):
                                    self._broadcast_commmit_entries(max_committable_index)

                  
                    elif (incoming_message.type == MessageType.ClientRequest):
                        client_request = incoming_message.entries
                        start_time = time.time()  # Record the start time to measure latency
                        self.process_client_request(client_request, start_time)  # Proc
                        self._broadcast_append_entries(client_request)

                elif (incoming_message.direction == MessageDirection.Request):

                 
                    if (incoming_message.type == MessageType.RequestVotes):
                        if (incoming_message.term > self.current_term):
                            self._increment_term(incoming_message.term)
                            self._send_vote(incoming_message.sender)
                            self._set_current_role('follower')

                            if(self.verbose):
                                print(self._name + ': saw higher term, demoting')
                            return

            client_request = self._get_client_request()
            if (client_request is not None):
                self._broadcast_append_entries(client_request)

        return

    def _send_message(self, message):
        '''
            _send_message: A wrapper to send a message.
            Inputs:
                message: (RequestVotesMessage or AppendEntriesMessage)
        '''
        self.talker.send_message(message.jsonify())

    def _get_message(self):
        '''
            _get_message: A wrapper to get a message. If there are no pending 
                messages returns None. 
        '''
        return parse_json_message(self.listener.get_message())

    def _load_config(self, config, name):
        with open(config, 'r') as infile:
            data = json.load(infile)
        return data

    def _get_client_request(self):
        '''
            _get_node_index: Pops the most recent client request. 
        '''
        try:
            return self.client_queue.get(block=False)
        except Empty:
            return None
    
    def _set_current_role(self, role):
        '''
            _set_current_role: Set the node role. Options are ['follower', 
            'leader', 'candidate']
            Inputs: 
                role: (str)
                    Node's new role
        '''
        with self.client_lock:
            self.current_role = role

    def _get_node_index(self, node_address):
        '''
            _get_node_index: Retuns the index of a specific node address,
                e.g. for
                    self.all_ids = ['5556', '5558']
                    _get_node_index('5556') <- returns 0
            Inputs: 
                node_address: (str)
                    The query address
        '''
        return self.all_ids.index(node_address)

    def _log_max_index(self):
        '''
            _log_max_index: Returns the max index of the log. Used for 
                convenience. 
        '''
        return len(self.log) - 1

    def _increment_term(self, term=None):
        '''
            _increment_term: Should be called whenever changing terms. 
                Does the following: clears the voted for status, increments
                the term. Useful for ensuring that both of these are done
                whenever the term is changed
            Input: 
                term: (int or None)
                    If term is none, will increment by one. Else will change
                    the term to whatever was input.
        '''
        self.voted_for = None
        if (term is None):
            self.current_term = self.current_term + 1
        else:
            self.current_term = term

    def _verify_entry(self, prev_index, prev_term):
        '''
            _verify_entry: Should be called whenever checking if an entry can 
                be appended to the log. Checks that the log has enough entries
                that the target index will not cause an error. Then checks if
                the target index has the same term as the target term. If it 
                does then this is a valid entry. 
            Input: 
                prev_index: (int)
                    Index to check.
                prev_term: (int)
                    Term to check.
        '''
        
        if (len(self.log) <= prev_index):
            return False
        if (self.log[prev_index]['term'] == prev_term):
            return True
        return False

    def _append_entry(self, entry, commit=False, prev_index=None):
        '''
            _append_entry: Appends entries to the log and optionally commits. 
                Assumes that the entry has already been verified (see 
                _verify_entry).
            Inputs:
                entry: (dict with the attributes 'term' and 'entry') 
                    Stores  whatever information to append to the log. 
                commit: (bool) 
                    If True, will update the last applied index and term after
                    writing to the log. If false will do nothing. 
                prev_index: (int) 
                    If None, will append the entry to the end of the log. Else 
                    will append the entry to the index specified.
        '''

        if (prev_index is None):
            prev_index = len(self.log) - 1
        else:
            self.log = self.log[:prev_index+1]

        prev_term = self.log[-1]['term']
        with self.client_lock:
            self.log.append(entry)
            self.log_hash[entry['id']] = entry

        if (commit):
            self._commit_entry(prev_index, entry['term'])

        return prev_index, prev_term

    def _commit_entry(self, index, term):
        '''
            _commit_entry: Update internal varables to reflect a commit at the 
                given index and term. Specifically the below variables should 
                be updated whenever a commmit is made. 
            Inputs:
                index: (int) 
                    Index to commit.
                term: (int) 
                    Term corresponding to this commit.
        '''
        self.last_applied_index = index
        self.last_applied_term = term

        with self.client_lock:
            self.commit_index = index

    def _broadcast_append_entries(self, entry):
        '''
            _broadcast_append_entries: Should be called only by the leader. 
                Sends an append entries message to all nodes for the given 
                entry.
            Inputs:
                entry: (dict with the attributes 'term' and 'entry') 
                    Entry to append to all nodes.    
        '''
 
        prev_index, prev_term = self._append_entry(entry, commit=False)

        for node, index in enumerate(self.next_index):
            # Only send out append entries to nodes that are up-to-date. Also they will now be out of date so update next. 
            if (index is None):
                self._send_append_entries(prev_index, prev_term, entry, self.all_ids[node])
                self.next_index[node] = self._log_max_index()

        self.next_index[self._get_node_index(self.my_id)] =  None
        self.match_index[self._get_node_index(self.my_id)] = self._log_max_index()

    def _broadcast_commmit_entries(self, index):
        '''
            _broadcast_commmit_entries: Should be called only by the leader. 
                Sends a commit message to all nodes for the given index.
            Inputs:
                index: (int) 
                    Index to commit.          
        '''

        self._commit_entry(index, self.log[index]['term'])

        for node, index in enumerate(self.match_index):
            if (index >= index):
                self._send_committal(index, self.all_ids[node])

    def _send_request_vote(self, receiver=None):
        message = RequestVotesMessage(
            type_ =   MessageType.RequestVotes, 
            term =   self.current_term, 
            sender = self.my_id,
            receiver = receiver, 
            direction = MessageDirection.Request, 
            candidate_id = self.my_id, 
            last_log_index = self.last_applied_index,
            last_log_term = self.last_applied_term
        )
        self._send_message(message)

    def _send_vote(self, candidate, vote_granted=True):
        message = RequestVotesMessage(
            type_ =   MessageType.RequestVotes, 
            term =   self.current_term,
            sender = self.my_id,
            receiver = candidate, 
            direction = MessageDirection.Response, 
            candidate_id = candidate, 
            last_log_index = self.last_applied_index,
            last_log_term = self.last_applied_term,
            results = RequestVotesResults(
                term = self.current_term,
                vote_granted = vote_granted
            )
        )
        self._send_message(message)
        self.voted_for = candidate

    def _send_heartbeat(self):
        message = AppendEntriesMessage(
            type_ = MessageType.Heartbeat,
            term = self.current_term,
            sender = self.my_id,
            receiver = None,
            direction = MessageDirection.Request,
            leader_id = self.my_id,
            prev_log_index = None,
            prev_log_term = None,
            entries = None,
            leader_commit = self.commit_index
        )
        self._send_message(message)

    def _send_append_entries(self, index, term, entries, receiver=None):
        message = AppendEntriesMessage(
            type_ = MessageType.AppendEntries,
            term = self.current_term,
            sender = self.my_id,
            receiver = receiver,
            direction = MessageDirection.Request,
            leader_id = self.my_id,
            prev_log_index = index,
            prev_log_term = term,
            entries = entries,
            leader_commit = self.commit_index
        )
        self._send_message(message)
    
    def _send_committal(self, index, receiver=None):
        message = AppendEntriesMessage(
            type_ = MessageType.Committal,
            term = self.current_term,
            sender = self.my_id,
            receiver = receiver,
            direction = MessageDirection.Request,
            leader_id = self.my_id,
            prev_log_index = self.last_applied_index,
            prev_log_term = self.last_applied_term,
            entries = None,
            leader_commit = self.commit_index
        )
        self._send_message(message)

    def _send_acknowledge(self, receiver, success, entry=None):
        message = AppendEntriesMessage(
            type_ = MessageType.Acknowledge,
            term = self.current_term,
            sender = self.my_id,
            receiver = receiver,
            direction = MessageDirection.Response,
            leader_id =self.leader_id ,
            prev_log_index = self.last_applied_index,
            prev_log_term = self.last_applied_term,
            entries = entry,
            leader_commit = self.commit_index, 
            results = AppendEntriesResults(
                term = self.current_term,
                success = success
            ) 
        )
        self._send_message(message)

    def _send_client_request(self, receiver, entry):
        message = AppendEntriesMessage(
            type_ = MessageType.ClientRequest,
            term = self.current_term,
            sender = self.my_id,
            receiver = receiver,
            direction = MessageDirection.Response,
            leader_id =self.leader_id ,
            prev_log_index = self.last_applied_index,
            prev_log_term = self.last_applied_term,
            entries = entry,
            leader_commit = self.commit_index
        )
        self._send_message(message)

def test_failures():
    '''
        test_failures: Creates a bunch of nodes and then crashes half of them. 
            A leader should emerge after the crash. 
    '''

    d = {'leader':{'ip': local_ip,
            'port': '5553'}}

    node_num = 1
    for p in range(start_port, start_port+total_nodes):
        name = 'node' + str(node_num)
        d[str(name)] = { 
            'ip': local_ip,
            'port': str(p)
        }
        node_num = node_num + 1
        
    with open(address_book_fname, 'w') as outfile:
        json.dump(d, outfile)

    s = []
    node_num = 1
    for p in range(start_port, start_port+total_nodes):
        name = 'node' + str(node_num)
        s.append(RaftNode(address_book_fname, name, 'follower'))
        node_num = node_num + 1
    for n in s:
        n.start()
    time.sleep(2)

    for i in range(10):
        s[0].client_request(i)
    time.sleep(3)

    l = [n for n in s if (n.check_role() == 'leader')][0]
    l.pause()
    num_to_kill = int(old_div(total_nodes, 2)) - 1
    for n in s:
        num_to_kill = num_to_kill - 1
        if num_to_kill == 0:
            break
        else:
            n.pause()
    time.sleep(5)

    for n in s:
        n.un_pause()
    time.sleep(5)

    for n in s:
        n.stop() 

if __name__ == '__main__':
    test_failures()
