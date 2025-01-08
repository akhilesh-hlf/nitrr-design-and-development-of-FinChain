import random
import time
import hashlib
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
        self.pre_election_quorum = self.total_nodes // 2 + 1  # Quorum is majority of the nodes
        self.log = []  # Initialize empty log
        self.commit_index = 0  # Track the index of the last committed log entry
        self.commit_term = 0  # Track the term of the last committed log entry

    def send_heartbeat(self):
        """Simulate the leader sending a heartbeat to followers."""
        if self.state == LEADER:
            self.last_heartbeat = time.time()
            time.sleep(random.uniform(0.1, 0.3))  # Simulate network delay for heartbeat

    def pre_election_rpc(self, candidate_id):
        """Simulate sending a PreElectionRPC to check if the node can become a candidate."""
        if self.state == FOLLOWER and self.last_heartbeat + self.pre_election_timeout < time.time():
            print(f"Node {self.id} detected a timeout and is considering election.")
            responses = 0
            for node in nodes:
                # Simulate a slight delay in responding to the PreElectionRPC
                time.sleep(random.uniform(0.05, 0.1))
                if node.respond_to_pre_election_rpc(candidate_id):
                    responses += 1
            if responses >= self.pre_election_quorum:
                print(f"Node {self.id} has received a quorum and is now transitioning to candidate state.")
                self.state = CANDIDATE
                self.start_election()

    def respond_to_pre_election_rpc(self, candidate_id):
        """Respond to a PreElectionRPC with a vote if the candidate's term is greater."""
        if self.state == FOLLOWER and self.term <= nodes[candidate_id].term:
            return True
        return False

    def request_vote(self, candidate_id, term, commit_index, commit_term):
        """Simulate the process of requesting a vote during leader election."""
        if term > self.term:
            self.state = FOLLOWER
            self.term = term
            self.voted_for = None
        if self.state == FOLLOWER and self.voted_for is None:
            if self.can_grant_vote(candidate_id, commit_index, commit_term):
                self.voted_for = candidate_id
                print(f"Node {self.id} voted for candidate {candidate_id} in term {term}.")
                # Simulate a small delay for processing the vote
                time.sleep(random.uniform(0.05, 0.1))
                return True
        return False

    def can_grant_vote(self, candidate_id, commit_index, commit_term):
        """Check if the candidate has a more up-to-date log."""
        candidate_log_entry = nodes[candidate_id].log[-1] if nodes[candidate_id].log else None
        if candidate_log_entry:
            if candidate_log_entry[1] > self.commit_term or (
                candidate_log_entry[1] == self.commit_term and candidate_log_entry[0] > self.commit_index):
                return True
        return False

    def send_confirm_vote(self, candidate_id, log_hash):
        """Send a ConfirmVote RPC with the hash of the last log entry."""
        if self.state == FOLLOWER:
            log_hash_follower = self.hash_log(self.log[-1]) if self.log else None
            if log_hash_follower == log_hash:
                print(f"Node {self.id} confirmed vote for candidate {candidate_id}.")
                return True
        return False

    def hash_log(self, log_entry):
        """Hash the log entry using SHA256."""
        return hashlib.sha256(str(log_entry).encode('utf-8')).hexdigest()

    def start_election(self):
        """Start an election to become the leader."""
        self.term += 1
        print(f"Node {self.id} started an election in term {self.term}.")
        time.sleep(random.uniform(0.1, 0.2))  # Simulate time taken to start election
        votes = 0
        log_hash = self.hash_log(self.log[-1]) if self.log else None
        for node in nodes:
            if node.request_vote(self.id, self.term, self.commit_index, self.commit_term):
                votes += 1
            # Simulate a slight delay in receiving votes
            time.sleep(random.uniform(0.05, 0.1))

        # Send ConfirmVote RPC after receiving a success vote
        for node in nodes:
            if node.send_confirm_vote(self.id, log_hash):
                votes += 1
            # Simulate slight delay in receiving confirmations
            time.sleep(random.uniform(0.05, 0.1))

        if votes >= self.total_nodes // 2:
            self.become_leader()

    def become_leader(self):
        """Simulate a node becoming the leader."""
        self.state = LEADER
        print(f"Node {self.id} became the leader.")
        self.send_heartbeat()

# Simulating a Raft cluster
def simulate_raft_cluster(num_nodes):
    global nodes
    # Create a list of nodes
    nodes = [RaftNode(i, num_nodes) for i in range(num_nodes)]

    # Randomly select a node to simulate the election
    candidate = random.choice(nodes)
    # Simulate follower timeout
    candidate.pre_election_rpc(candidate.id)

# Running the simulation to measure leader election time
def run_leader_election_simulation():
    node_counts = range(10, 101, 10)
    latency_data = []

    for node_count in node_counts:
        print(f"\nRunning simulation with {node_count} nodes...")
        start_time = time.time()
        simulate_raft_cluster(node_count)
        end_time = time.time()
        latency_data.append(end_time - start_time)  # Measure the time taken for the election

    print("\nLeader Election Time (Latency) over varying number of nodes:")
    for nodes_count, latency in zip(node_counts, latency_data):
        print(f"Nodes: {nodes_count}, Election Time: {latency*1000:.2f} sec")

if __name__ == "__main__":
    run_leader_election_simulation()
