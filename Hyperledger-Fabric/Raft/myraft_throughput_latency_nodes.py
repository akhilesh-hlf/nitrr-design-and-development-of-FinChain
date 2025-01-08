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
        self.start_time = time.time()  # Start time for throughput calculation

        # Latency variables
        self.latency_samples = []

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

        # Request votes from other nodes
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.request_vote(node)

        self.reset_timer()

    def request_vote(self, target_node):
        start_time = time.time()
        if random.choice([True, False]):
            self.receive_vote(True)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.latency_samples.append(latency)

    def receive_vote(self, vote_granted):
        if vote_granted:
            self.votes_received += 1
            if self.votes_received > self.total_nodes // 2:
                self.become_leader()

    def become_leader(self):
        self.state = State.LEADER
        self.reset_timer()
        self.send_heartbeats()

    def send_heartbeats(self):
        if self.state != State.LEADER:
            return

        start_time = time.time()
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.append_entries(node)

        self.commit_log_entry(f"Entry at term {self.current_term}")

        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.latency_samples.append(latency)

        threading.Timer(self.heartbeat_interval, self.send_heartbeats).start()

    def append_entries(self, target_node):
        pass

    def commit_log_entry(self, entry):
        start_time = time.time()
        self.log.append(entry)
        self.commit_index += 1
        self.committed_operations += 1
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.latency_samples.append(latency)

    def calculate_throughput_latency(self):
        elapsed_time = time.time() - self.start_time
        throughput = self.committed_operations / elapsed_time if elapsed_time > 0 else 0
        avg_latency = sum(self.latency_samples) / len(self.latency_samples) if self.latency_samples else 0
        return throughput, avg_latency


def simulate_raft_for_nodes(node_counts):
    results = []

    for num_nodes in node_counts:
        print(f"\nSimulating for {num_nodes} nodes...")
        nodes = [RaftNode(node_id, num_nodes) for node_id in range(num_nodes)]

        # Let the simulation run for a fixed period
        time.sleep(10)

        # Collect throughput and latency statistics
        total_throughput = 0
        total_latency = 0
        for node in nodes:
            throughput, avg_latency = node.calculate_throughput_latency()
            total_throughput += throughput
            total_latency += avg_latency
            node.timer.cancel()  # Stop timers to avoid hanging threads

        avg_throughput = total_throughput / num_nodes
        avg_latency = total_latency / num_nodes
        results.append((num_nodes, avg_throughput, avg_latency))
        print(f"Nodes: {num_nodes}, Throughput: {avg_throughput:.2f} ops/sec, Latency: {avg_latency:.2f} ms")

    return results


if __name__ == "__main__":
    node_counts = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    results = simulate_raft_for_nodes(node_counts)

    print("\nFinal Results:")
    for num_nodes, throughput, latency in results:
        print(f"Nodes: {num_nodes}, Avg Throughput: {throughput:.2f} ops/sec, Avg Latency: {latency:.2f} ms")
