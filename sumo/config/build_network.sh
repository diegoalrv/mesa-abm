#!/bin/bash
cd /app/config

# Generate network from nodes and edges
netgenerate -n nodes.nod.xml -e edges.edg.xml -o network.net.xml --turn-lanes 0

echo "Network generated successfully"