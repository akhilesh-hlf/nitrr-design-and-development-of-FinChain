import random
import time
import threading

# Raft Node States
FOLLOWER = "follower"
CANDIDATE = "candidate"
LEADER = "leader"

# Raft Node class
class RaftNode:
    def __init__(self, id, total_nodes):
        self.id = id
        self.state = FOLLOWER
        self.term = 0
        self.votes_received = 0
        self.total_nodes = total_nodes
        self.last_heartbeat = time.time()
        self.voted_for = None
        self.pre_election_timeout = random.uniform(1.0, 2.0)  # Randomized timeout for candidate transition

    def send_heartbeat(self):
        """Simulate the leader sending a heartbeat to followers."""
        if self.state == LEADER:
            self.last_heartbeat = time.time()
            time.sleep(random.uniform(0.1, 0.3))  # Simulate network delay for heartbeat

    def request_vote(self, candidate_id, term):
        """Simulate the process of requesting a vote during leader election."""
        if term > self.term:
            self.state = FOLLOWER
            self.term = term
            self.voted_for = None
        if self.state == FOLLOWER and self.voted_for is None:
            self.voted_for = candidate_id
            print(f"Node {self.id} voted for candidate {candidate_id} in term {term}.")
            return True
        return False

    def start_election(self):
        """Start an election to become the leader."""
        self.state = CANDIDATE
        self.term += 1
        print(f"Node {self.id} started an election in term {self.term}.")
        time.sleep(random.uniform(0.1, 0.2))  # Simulate time taken to start election
        votes = 0
        for node in nodes:
            if node.request_vote(self.id, self.term):
                votes += 1
        if votes > self.total_nodes // 2:
            self.become_leader()

    def become_leader(self):
        """Simulate a node becoming the leader."""
        self.state = LEADER
        print(f"Node {self.id} became the leader.")

# Simulating a Raft cluster
def simulate_raft_cluster(num_nodes):
    global nodes
    # Create a list of nodes
    nodes = [RaftNode(i, num_nodes) for i in range(num_nodes)]

    # Randomly select a node to start the election
    candidate = random.choice(nodes)
    candidate.start_election()

# Running the simulation to measure leader election time
def run_leader_election_simulation():
    node_counts = range(10, 101, 10)
    latency_data = []

    for node_count in node_counts:
        print(f"Running simulation with {node_count} nodes...")
        start_time = time.time()
        simulate_raft_cluster(node_count)
        end_time = time.time()
        latency_data.append(end_time - start_time)  # Measure the time taken for the election

    print("\nLeader Election Time (Latency) over varying number of nodes:")
    for nodes_count, latency in zip(node_counts, latency_data):
        print(f"Nodes: {nodes_count}, Election Time: {latency*1000:.2f} sec")

if __name__ == "__main__":
    run_leader_election_simulation()
