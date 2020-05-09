# Consistent Hashing and RHW Hashing

The distributed cache you implemented in the midterm is based on naive modula hashing to shard the data.

Implementation both part is located in node_ring.py

Test code for this assignment is located in cache_client.py in the main

## How to run:

Start the client first, via provided batch files or direct invocation

See cache_client_output.txt for client output
See cache_server_output.png for server output

On the terminal enter:
```
./run_server

python cache_client.py
```

## Part I.

Implement Rendezvous hashing to shard the data.

Implementation for this part is located in node_ring.py

Usage:
```python
client_ring_RH = NodeRing(clients, mode='Rendezvous Hashing')
client_ring_RH.get_node(key)

```

## Part II.

Implement consistent hashing to shard the data.

Features:

* Add virtual node layer in the consistent hashing.
* Implement virtual node with data replication. 

```python
client_ring_CH = NodeRing(clients,mode='Consistent Hashing', replicas=8)
client_ring_CH.get_node(key)
```
