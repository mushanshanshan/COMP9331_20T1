1.Init p2p network by run 'python3 autoTest_vlab.py'(peer_id can be modify in autoTest_vlab.py file)

or using "python3 p2p.py init <PEER> <FIRST_SUCCESSOR> <SECOND_SUCCESSOR> <PING_INTERVAL>"


2.Join p2p network by run 'python3 p2p.py join <PEER> <KNOWN_PEER> <PING_INTERVAL>'
(For example 'python3 p2p.py join 15 4 30')

3.Peer Departure (Graceful) by entering “Quit” on its xterm terminal

4.Peer Departure (Abrupt) by using ctrl+c or commond+c

5.Data Insertion by entering “Store <file name>” on any xterm terminal
(For example 'Store 4103')

6.Data Retrieval by entering “Request <file name>” on any xterm terminal
(For example '“Request 4103')

