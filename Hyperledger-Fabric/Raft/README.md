
Clone the repo, create a new python environment and then run:
```bash
pip install -r requirements.txt
```

To test the system, edit the test script with your ip and then run:
```bash 
python test.py
```

This package has been tested with python2.7 and python3.6.

```python 
from raft import RaftNode
import time

comm_dict = {"node0": {"ip": "127.0.0.1", "port": "5567"}, 
  "node1": {"ip": "127.0.0.1", "port": "5566"}, 
  "node2": {"ip": "127.0.0.1", "port": "5565"}}

# Start a few nodes
nodes = [RaftNode(comm_dict, 'node0'),
         RaftNode(comm_dict, 'node1'), 
         RaftNode(comm_dict, 'node2')]
for n in nodes:
  n.start()

# Let a leader emerge
time.sleep(2)

# Make some requests
for val in range(5):
  nodes[0].client_request({'val': val})
time.sleep(5)

# Check and see what the most recent entry is
for n in nodes:
  print(n.check_committed_entry())

# Stop all the nodes
for n in nodes:
  n.stop()
```

