#!/usr/local/bin/python3
import socket
import time
import subprocess
import sys
import argparse
import os
import coloredlogs
import logging
from threading import Thread
import queue
import re


# Load hosts from hosts.txt and map into an array
def get_ips(filename):
	with open(filename, "r") as host_file:
		host_ips = []
		host_descs = []
		for line in host_file.readlines():
			host_ip, host_desc = line.strip().split(',')
			host_ips.append(host_ip)
			host_descs.append(host_desc)
	return host_ips, host_descs


def multi_ping(host_list, desc_list, lookup, sleep, threads):

	# create queues
	ips_q = queue.Queue()
	out_q = queue.Queue()

	# start the thread pool
	for i in range(threads):
		worker = Thread(target=thread_ping, args=(out_q, ips_q))
		worker.setDaemon(True)
		worker.start()

	# fill queue
	for ip in host_list:
		ips_q.put(ip)

	ips_q.join()

	while True:
		try:
			msg = out_q.get_nowait()
		except Exception as e:
			logging.info(e)
			break
		logging.info(msg)
	logging.info('Sleeping {} seconds'.format(sleep))
	time.sleep(sleep)


def thread_ping(out_q, q):
	"""
	Ping hosts in queue
	:return:
	"""
	while True:
		# Get an ip address from IP queue
		ip = q.get()
		# ping
		args = ['ping', '-c', '2', '-W', '1', str(ip)]
		p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
		# Save ping stdout
		p_ping_out = p_ping.communicate()[0]
		if p_ping.wait() == 0:
			search = re.search(b'(.*)/(.*)/(.*)/(.*) ms',
							   p_ping_out, re.M | re.I)
			ping_rtt = search.group(2)
			out_q.put(str(ip) + ' OK' + " rtt= " + ping_rtt.decode("utf-8") + 'ms')
		else:
			out_q.put(str(ip) + ' is NOT reachable!')
		q.task_done()


def ping_sweep(host_list, desc_list, lookup, sleep):
	if lookup:
		logging.info('DNS reverse lookup option set')
	'''
	Loop through hosts array, ping each host, and return result
	'''
	for x in range(len(host_list)):
		print(host_list[x])
		result = subprocess.Popen(
			['ping', '-c', '3', "-n", "-W", "1", host_list[x]],
			stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
		if result == 0:
			logging.info('{} - {} is reachable'.format(host_list[x], desc_list[x]))
			if lookup:
				try:
					hostname = socket.gethostbyaddr(host_list[x])[0]
					logging.info('{} resolved to {}'.format(host_list[x], hostname))
				except socket.herror:
					logging.critical('DNS lookup failed for {}'.format(host_list[x]))
		else:
			logging.critical('---> {} - {} is unreachable'.format(host_list[x], desc_list[x]))
			if lookup:
				try:
					hostname = socket.gethostbyaddr(host_list[x])[0]
					logging.info('{} resolved to {}'.format(host_list[x], hostname))
				except socket.herror:
					logging.critical('DNS lookup failed for {}'.format(host_list[x]))
	logging.info('Sleeping {} seconds'.format(sleep))
	time.sleep(sleep)


def main():
	# Set options for passing arguments to the script
	parser = argparse.ArgumentParser()

	# -f option for specifying the input filename is required
	parser.add_argument('-f', '--filename', required=True,
						type=str,
						help="a string for the input file (e.g. - hosts.csv or hosts.txt")
	# - option for specifying the input filename is required
	parser.add_argument('-l', '--lookup', action='store_true')
	parser.add_argument('-c', '--count', required=False,
						type=int,
						nargs='?',
						default=1,
						const=1,
						help="enter number of times you'd like to perform ping sweep")
	parser.add_argument('-d', '--debug', action='store_true', default=False,
						help="set this option to set the logging level to debug.")
	parser.add_argument('-s', '--sleep', required=False, type=int, default=0,
						help="an integer for the time (in seconds) to sleep in between icmp iterations")
	parser.add_argument('-t', '--threads', type=int, default=1, required=False,
						help='set an integer value for the number of threads you would like')
	args = parser.parse_args()

	coloredlogs.install()
	# Check for debug option
	if not args.debug:
		coloredlogs.install(level='INFO')
		logging.warning('LOGGING IS SET TO INFO')
	elif args.debug:
		coloredlogs.install(level='DEBUG')
		logging.info('LOGGING IS SET TO DEBUG')

	# check count
	iterations = int(args.count)

	# read in host list
	try:
		logging.info(f"Reading in hosts file - {args.filename}")
		host_file = os.path.abspath(args.filename)
		host_list, desc_list = get_ips(host_file)
	except AttributeError as ex:
		logging.critical(ex)
		sys.exit(status=0)

	if iterations == 1 and args.threads == 1:
		logging.debug("OPTION 1")
		ping_sweep(host_list, desc_list, args.lookup, args.sleep)
	elif iterations > 1 and args.threads == 1:
		logging.debug("OPTION 2")
		logging.debug('Iterating through hosts in {}, {} times.'.format(args.filename, iterations))
		while iterations > 0:
			ping_sweep(host_list, desc_list, args.lookup, args.sleep)
			iterations -= 1
	elif iterations == 1 and args.threads > 1:
		logging.debug("OPTION 3")
		multi_ping(host_list, desc_list, args.lookup, args.sleep, args.threads)
	elif iterations > 1 and args.threads > 1:
		logging.debug("OPTION 4")
		while iterations > 0:
			multi_ping(host_list, desc_list, args.lookup, args.sleep, args.threads)
			iterations -= 1


if __name__ == '__main__':
	main()
