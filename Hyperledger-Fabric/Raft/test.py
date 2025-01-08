#!/usr/bin/env python
import time
from raft import RaftNode

# Create the intercommunication json 
ip_addr = "172.16.101.19"
comm_dict = nodes = {
    f"node{i}": {"ip": ip_addr, "port": str(5567 - i)}
    for i in range(10)
}


# {
#     "node0": {"ip": ip_addr, "port": "5567"},
#     "node1": {"ip": ip_addr, "port": "5566"},
#     "node2": {"ip": ip_addr, "port": "5565"},
#     "node3": {"ip": ip_addr, "port": "5564"},
#     "node4": {"ip": ip_addr, "port": "5563"},
#     "node5": {"ip": ip_addr, "port": "5562"},
#     "node6": {"ip": ip_addr, "port": "5561"},
#     "node7": {"ip": ip_addr, "port": "5560"},
#     "node8": {"ip": ip_addr, "port": "5559"},
#     "node9": {"ip": ip_addr, "port": "5558"},
#     "node10": {"ip": ip_addr, "port": "5557"},
#     "node11": {"ip": ip_addr, "port": "5556"},
#     "node12": {"ip": ip_addr, "port": "5555"},
#     "node13": {"ip": ip_addr, "port": "5554"},
#     "node14": {"ip": ip_addr, "port": "5553"},
#     "node15": {"ip": ip_addr, "port": "5552"},
#     "node16": {"ip": ip_addr, "port": "5551"},
#     "node17": {"ip": ip_addr, "port": "5550"},
#     "node18": {"ip": ip_addr, "port": "5549"},
#     "node19": {"ip": ip_addr, "port": "5548"},
#     "node20": {"ip": ip_addr, "port": "5547"},
#     "node21": {"ip": ip_addr, "port": "5546"},
#     "node22": {"ip": ip_addr, "port": "5545"},
#     "node23": {"ip": ip_addr, "port": "5544"},
#     "node24": {"ip": ip_addr, "port": "5543"},
#     "node25": {"ip": ip_addr, "port": "5542"},
#     "node26": {"ip": ip_addr, "port": "5541"},
#     "node27": {"ip": ip_addr, "port": "5540"},
#     "node28": {"ip": ip_addr, "port": "5539"},
#     "node29": {"ip": ip_addr, "port": "5538"},
#     "node30": {"ip": ip_addr, "port": "5537"},
#     "node31": {"ip": ip_addr, "port": "5536"},
#     "node32": {"ip": ip_addr, "port": "5535"},
#     "node33": {"ip": ip_addr, "port": "5534"},
#     "node34": {"ip": ip_addr, "port": "5533"},
#     "node35": {"ip": ip_addr, "port": "5532"},
#     "node36": {"ip": ip_addr, "port": "5531"},
#     "node37": {"ip": ip_addr, "port": "5530"},
#     "node38": {"ip": ip_addr, "port": "5529"},
#     "node39": {"ip": ip_addr, "port": "5528"}
# }


# {
#     "node0": {"ip": ip_addr, "port": "5567"},
#     "node1": {"ip": ip_addr, "port": "5566"},
#     "node2": {"ip": ip_addr, "port": "5565"},
#     "node3": {"ip": ip_addr, "port": "5564"},
#     "node4": {"ip": ip_addr, "port": "5563"},
#     "node5": {"ip": ip_addr, "port": "5562"},
#     "node6": {"ip": ip_addr, "port": "5561"},
#     "node7": {"ip": ip_addr, "port": "5560"},
#     "node8": {"ip": ip_addr, "port": "5559"},
#     "node9": {"ip": ip_addr, "port": "5558"},
#     "node10": {"ip": ip_addr, "port": "5557"},
#     "node11": {"ip": ip_addr, "port": "5556"},
#     "node12": {"ip": ip_addr, "port": "5555"},
#     "node13": {"ip": ip_addr, "port": "5554"},
#     "node14": {"ip": ip_addr, "port": "5553"},
#     "node15": {"ip": ip_addr, "port": "5552"},
#     "node16": {"ip": ip_addr, "port": "5551"},
#     "node17": {"ip": ip_addr, "port": "5550"},
#     "node18": {"ip": ip_addr, "port": "5549"},
#     "node19": {"ip": ip_addr, "port": "5548"},
#     "node20": {"ip": ip_addr, "port": "5547"},
#     "node21": {"ip": ip_addr, "port": "5546"},
#     "node22": {"ip": ip_addr, "port": "5545"},
#     "node23": {"ip": ip_addr, "port": "5544"},
#     "node24": {"ip": ip_addr, "port": "5543"},
#     "node25": {"ip": ip_addr, "port": "5542"},
#     "node26": {"ip": ip_addr, "port": "5541"},
#     "node27": {"ip": ip_addr, "port": "5540"},
#     "node28": {"ip": ip_addr, "port": "5539"},
#     "node29": {"ip": ip_addr, "port": "5538"}
# }




# {
#     "node0": {"ip": ip_addr, "port": "5567"},
#     "node1": {"ip": ip_addr, "port": "5566"},
#     "node2": {"ip": ip_addr, "port": "5565"},
#     "node3": {"ip": ip_addr, "port": "5564"},
#     "node4": {"ip": ip_addr, "port": "5563"},
#     "node5": {"ip": ip_addr, "port": "5562"},
#     "node6": {"ip": ip_addr, "port": "5561"},
#     "node7": {"ip": ip_addr, "port": "5560"},
#     "node8": {"ip": ip_addr, "port": "5559"},
#     "node9": {"ip": ip_addr, "port": "5558"},
#     "node10": {"ip": ip_addr, "port": "5557"},
#     "node11": {"ip": ip_addr, "port": "5556"},
#     "node12": {"ip": ip_addr, "port": "5555"},
#     "node13": {"ip": ip_addr, "port": "5554"},
#     "node14": {"ip": ip_addr, "port": "5553"},
#     "node15": {"ip": ip_addr, "port": "5552"},
#     "node16": {"ip": ip_addr, "port": "5551"},
#     "node17": {"ip": ip_addr, "port": "5550"},
#     "node18": {"ip": ip_addr, "port": "5549"},
#     "node19": {"ip": ip_addr, "port": "5548"}
# }





# {
#     "node0": {"ip": ip_addr, "port": "5567"},
#     "node1": {"ip": ip_addr, "port": "5566"},
#     "node2": {"ip": ip_addr, "port": "5565"},
#     "node3": {"ip": ip_addr, "port": "5564"},
#     "node4": {"ip": ip_addr, "port": "5563"},
#     "node5": {"ip": ip_addr, "port": "5562"},
#     "node6": {"ip": ip_addr, "port": "5561"},
#     "node7": {"ip": ip_addr, "port": "5560"},
#     "node8": {"ip": ip_addr, "port": "5559"},
#     "node9": {"ip": ip_addr, "port": "5558"}
# }




            # {"node0": {"ip": ip_addr, "port": "5567"}, 
            #  "node1": {"ip": ip_addr, "port": "5566"}, 
            #  "node2": {"ip": ip_addr, "port": "5565"},
            #  "node3": {"ip": ip_addr, "port": "5564"},
            #  "node4": {"ip": ip_addr, "port": "5563"}}

# Start a few nodes
nodes = []
for name, address in comm_dict.items():
    nodes.append(RaftNode(comm_dict, name))
    nodes[-1].start()

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
