import os

# Create a simple node file
nodes_content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">
    <node id="A" x="0.0" y="0.0" type="priority"/>
    <node id="B" x="100.0" y="0.0" type="priority"/>
    <node id="C" x="100.0" y="100.0" type="priority"/>
    <node id="D" x="0.0" y="100.0" type="priority"/>
</nodes>
"""

# Create a simple edge file
edges_content = """<?xml version="1.0" encoding="UTF-8"?>
<edges version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd">
    <edge id="AB" from="A" to="B" numLanes="1" speed="13.9"/>
    <edge id="BC" from="B" to="C" numLanes="1" speed="13.9"/>
    <edge id="CD" from="C" to="D" numLanes="1" speed="13.9"/>
    <edge id="DA" from="D" to="A" numLanes="1" speed="13.9"/>
</edges>
"""

# Write files
with open("nodes.nod.xml", "w") as f:
    f.write(nodes_content)

with open("edges.edg.xml", "w") as f:
    f.write(edges_content)

print("Generated nodes.nod.xml and edges.edg.xml")