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

        # Throughput variables
        self.committed_operations = 0
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

        for node in range(self.total_nodes):
            if node != self.node_id:
                self.request_vote(node)

        self.reset_timer()

    def request_vote(self, target_node):
        if random.choice([True, False]):
            self.receive_vote(True)

    def receive_vote(self, vote_granted):
        if vote_granted:
            self.votes_received += 1

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

        for node in range(self.total_nodes):
            if node != self.node_id:
                self.append_entries(node)

        self.commit_log_entry(f"Entry at term {self.current_term}")

        threading.Timer(self.heartbeat_interval, self.send_heartbeats).start()

    def append_entries(self, target_node):
        pass  # Simulate sending append entries

    def commit_log_entry(self, entry):
        self.log.append(entry)
        self.commit_index += 1
        self.committed_operations += 1  # Increment committed operations counter


def calculate_throughput(nodes, elapsed_time):
    total_operations = sum(node.committed_operations for node in nodes)
    throughput = total_operations / elapsed_time if elapsed_time > 0 else 0
    print(f"Total Throughput: {throughput:.2f} operations/second across {len(nodes)} nodes")
    return throughput

# Example usage
if __name__ == "__main__":
    node_counts = [3, 5, 10]  # Different numbers of nodes to simulate
    for num_nodes in node_counts:
        print(f"\nSimulating {num_nodes} nodes...")
        nodes = [RaftNode(node_id, num_nodes) for node_id in range(num_nodes)]
        start_time = time.time()

        try:
            time.sleep(10)  # Run the simulation for 10 seconds
        except KeyboardInterrupt:
            pass

        elapsed_time = time.time() - start_time
        calculate_throughput(nodes, elapsed_time)

        for node in nodes:
            node.timer.cancel()
