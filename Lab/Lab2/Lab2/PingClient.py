#!/usr/bin/python

import socket
import sys
import datetime


def main():
	if len(sys.argv) != 3:
		print("Parameters ERROR!")
		sys.exit(1)
	
	addr = (sys.argv[1], int(sys.argv[2]))
	rtts = []
	
	for i in range(10):
		client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		client.settimeout(1)
		send_time = datetime.datetime.now()
		client.sendto("PING {} {} \r\n".format(i, send_time).encode(), addr)
		
		try:
			resp_data, server_addr = client.recvfrom(2048)
			rtt = round(((datetime.datetime.now() - send_time).total_seconds() * 1000))
			rtts.append(rtt)
			print('ping to {}, seq = {}, rtt = {} ms'.format(addr[0], i, rtt))
		except socket.timeout:
			print('ping to {}, seq = {}, time out'.format(addr[0], i))
		
	if len(rtts) != 0:
		print('round-trip min/avg/max = {}/{}/{} ms'.format(min(rtts), sum(rtts)/len(rtts), max(rtts)))
	else:
		print('All of 10 packages are lost')

if __name__ == "__main__":
	main()
