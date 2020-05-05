import os

peer = [2,4,5,8,9,14,19]
d_peer = peer * 2
ping_time = 30

commd = ''

for i in range(len(peer)):
    commd += 'xterm -hold -title "peer{}" -e "python3 p2p.py init {} {} {} {}" & '.format(d_peer[i], d_peer[i], d_peer[i+1], d_peer[i+2], ping_time)

os.system(commd)


