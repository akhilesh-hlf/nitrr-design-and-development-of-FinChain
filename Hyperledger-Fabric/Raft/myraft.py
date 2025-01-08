import threading
import time
import random
from enum import Enum

class State(Enum):
    FOLLOWER = "Follower"
    CANDIDATE = "Candidate"
    LEADER = "Leader"

class RaftNode:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.state = State.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []  # Log entries
        self.commit_index = -1
        self.last_applied = -1
        self.votes_received = 0

        # Election timeout and heartbeat interval
        self.election_timeout = random.uniform(2, 5)  # in seconds
        self.heartbeat_interval = 1.0  # in seconds

        self.timer = threading.Timer(self.election_timeout, self.start_election)
        self.timer.start()

    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.election_timeout, self.start_election)
        self.timer.start()

    def start_election(self):
        self.state = State.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1  # Vote for itself

        print(f"Node {self.node_id}: Starting election for term {self.current_term}")

        # Request votes from other nodes
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.request_vote(node)

        # Reset the timer for this election
        self.reset_timer()

    def request_vote(self, target_node):
        print(f"Node {self.node_id}: Requesting vote from Node {target_node} for term {self.current_term}")
        # Simulate receiving a vote
        if random.choice([True, False]):
            self.receive_vote(True)

    def receive_vote(self, vote_granted):
        if vote_granted:
            self.votes_received += 1
            print(f"Node {self.node_id}: Received vote, total votes: {self.votes_received}")

            if self.votes_received > self.total_nodes // 2:
                self.become_leader()

    def become_leader(self):
        self.state = State.LEADER
        print(f"Node {self.node_id}: Became leader for term {self.current_term}")
        self.reset_timer()
        self.send_heartbeats()

    def send_heartbeats(self):
        if self.state != State.LEADER:
            return

        print(f"Node {self.node_id}: Sending heartbeats to other nodes")
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.append_entries(node)

        threading.Timer(self.heartbeat_interval, self.send_heartbeats).start()

    def append_entries(self, target_node):
        print(f"Node {self.node_id}: Sending append entries to Node {target_node}")

    def receive_heartbeat(self, term):
        if term >= self.current_term:
            self.state = State.FOLLOWER
            self.current_term = term
            self.reset_timer()

# Example usage
if __name__ == "__main__":
    num_nodes = 5
    nodes = [RaftNode(node_id, num_nodes) for node_id in range(num_nodes)]

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        for node in nodes:
            node.timer.cancel()
