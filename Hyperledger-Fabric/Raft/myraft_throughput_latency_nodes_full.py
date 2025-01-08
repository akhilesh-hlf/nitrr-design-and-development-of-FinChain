# import random
# import time
# import threading
# import statistics

# # Raft Node States
# FOLLOWER = "follower"
# CANDIDATE = "candidate"
# LEADER = "leader"

# # Raft Node class
# class RaftNode:
#     def __init__(self, id, total_nodes):
#         self.id = id
#         self.state = FOLLOWER
#         self.term = 0
#         self.votes_received = 0
#         self.log = []
#         self.commit_index = 0
#         self.last_heartbeat = time.time()
#         self.total_nodes = total_nodes
#         self.leader = None

#     def send_heartbeat(self):
#         """Simulate the leader sending a heartbeat to followers."""
#         if self.state == LEADER:
#             self.last_heartbeat = time.time()
#             print(f"Leader {self.id} sent heartbeat.")
#         else:
#             # Followers and candidates wait for heartbeats or request votes
#             pass

#     def request_vote(self, candidate_id, term):
#         """Simulate the process of requesting a vote during leader election."""
#         if term > self.term:
#             self.state = FOLLOWER
#             self.term = term
#             self.votes_received = 0
#             self.leader = None
#         if self.state == FOLLOWER and self.votes_received < 1:
#             print(f"Node {self.id} voted for candidate {candidate_id} in term {term}.")
#             self.votes_received += 1
#             return True
#         return False

#     def log_append(self, entry):
#         """Append a log entry to the node's log."""
#         if self.state == LEADER:
#             self.log.append(entry)
#             print(f"Leader {self.id} appended log entry {entry}.")
#             return True
#         return False

#     def update_commit_index(self):
#         """Simulate the process of committing logs."""
#         if len(self.log) > self.commit_index:
#             self.commit_index = len(self.log)
#             print(f"Node {self.id} committed log up to index {self.commit_index}.")

#     def become_leader(self):
#         """Simulate a node becoming the leader."""
#         self.state = LEADER
#         self.leader = self.id
#         print(f"Node {self.id} became the leader.")

#     def start_election(self):
#         """Start an election to become the leader."""
#         self.state = CANDIDATE
#         self.term += 1
#         print(f"Node {self.id} started an election in term {self.term}.")
#         votes = 0
#         for node in nodes:
#             if node.request_vote(self.id, self.term):
#                 votes += 1
#         if votes > self.total_nodes // 2:
#             self.become_leader()


# # Simulating a Raft cluster
# def simulate_raft_cluster(num_nodes):
#     # Create a list of nodes
#     nodes = [RaftNode(i, num_nodes) for i in range(num_nodes)]
    
#     start_time = time.time()
    
#     # Simulate leader election and log replication
#     leader = random.choice(nodes)
#     leader.become_leader()

#     for i in range(100):  # Simulating 5 log entries
#         log_entry = f"Log Entry {i}"
#         for node in nodes:
#             if node.log_append(log_entry):
#                 node.update_commit_index()

#     # Calculating throughput and latency
#     end_time = time.time()
#     latency = end_time - start_time
#     throughput = (len(nodes) * 100) / latency  # Assuming 5 entries for simplicity

#     print(f"Throughput: {throughput} entries/sec, Latency: {latency} millisec")

# # Running the simulation with nodes varying from 10 to 100
# def run_simulation():
#     node_counts = range(10, 101, 10)
#     throughput_data = []
#     latency_data = []

#     for node_count in node_counts:
#         print(f"Running simulation with {node_count} nodes...")
#         start = time.time()
#         simulate_raft_cluster(node_count)
#         end = time.time()
#         latency_data.append(end - start)
#         throughput_data.append((node_count * 100) / (end - start))  # 5 log entries for simplicity

#     print("Throughput and Latency over varying number of nodes:")
#     for nodes, throughput, latency in zip(node_counts, throughput_data, latency_data):
#         print(f"Nodes: {nodes}, Throughput: {throughput:.2f} entries/sec, Latency: {latency*1000:.2f} msec")

# if __name__ == "__main__":
#     run_simulation()
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
        self.log = []
        self.commit_index = 0
        self.last_heartbeat = time.time()
        self.total_nodes = total_nodes
        self.leader = None

    def send_heartbeat(self):
        """Simulate the leader sending a heartbeat to followers."""
        if self.state == LEADER:
            self.last_heartbeat = time.time()
            print(f"Leader {self.id} sent heartbeat.")
            time.sleep(random.uniform(0.1, 0.3))  # Simulate network delay for heartbeat

    def request_vote(self, candidate_id, term):
        """Simulate the process of requesting a vote during leader election."""
        if term > self.term:
            self.state = FOLLOWER
            self.term = term
            self.votes_received = 0
            self.leader = None
        if self.state == FOLLOWER and self.votes_received < 1:
            print(f"Node {self.id} voted for candidate {candidate_id} in term {term}.")
            self.votes_received += 1
            time.sleep(random.uniform(0.1, 0.2))  # Simulate network delay for vote request
            return True
        return False

    def log_append(self, entry):
        """Append a log entry to the node's log."""
        if self.state == LEADER:
            self.log.append(entry)
            print(f"Leader {self.id} appended log entry {entry}.")
            time.sleep(random.uniform(0.1, 0.3))  # Simulate network delay for log replication
            return True
        return False

    def update_commit_index(self):
        """Simulate the process of committing logs."""
        if len(self.log) > self.commit_index:
            self.commit_index = len(self.log)
            print(f"Node {self.id} committed log up to index {self.commit_index}.")
            time.sleep(random.uniform(0.1, 0.2))  # Simulate delay in commit index update

    def become_leader(self):
        """Simulate a node becoming the leader."""
        self.state = LEADER
        self.leader = self.id
        print(f"Node {self.id} became the leader.")
        time.sleep(random.uniform(0.1, 0.2))  # Simulate delay when becoming leader

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


# Simulating a Raft cluster
def simulate_raft_cluster(num_nodes):
    # Create a list of nodes
    nodes = [RaftNode(i, num_nodes) for i in range(num_nodes)]
    
    start_time = time.time()
    
    # Simulate leader election and log replication
    leader = random.choice(nodes)
    leader.become_leader()

    for i in range(5):  # Simulating 5 log entries
        log_entry = f"Log Entry {i}"
        for node in nodes:
            if node.log_append(log_entry):
                node.update_commit_index()

    # Calculating throughput and latency
    end_time = time.time()
    latency = end_time - start_time
    throughput = (len(nodes) * 5) / latency  # Assuming 5 entries for simplicity

    print(f"Throughput: {throughput} entries/sec, Latency: {latency} sec")

# Running the simulation with nodes varying from 10 to 100
def run_simulation():
    node_counts = range(10, 101, 10)
    throughput_data = []
    latency_data = []

    for node_count in node_counts:
        print(f"Running simulation with {node_count} nodes...")
        start = time.time()
        simulate_raft_cluster(node_count)
        end = time.time()
        latency_data.append(end - start)
        throughput_data.append((node_count * 5) / (end - start))  # 5 log entries for simplicity

    print("Throughput and Latency over varying number of nodes:")
    for nodes, throughput, latency in zip(node_counts, throughput_data, latency_data):
        print(f"Nodes: {nodes}, Throughput: {throughput:.2f} entries/sec, Latency: {latency:.2f} sec")

if __name__ == "__main__":
    run_simulation()
