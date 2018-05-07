#!/usr/local/bin/python3
import socket
import time
import subprocess
import sys
import argparse
import os
import coloredlogs, logging

# Load hosts from hosts.txt and map into an array
def get_ips(filename):
    with open(filename, "r") as hostsFile:
        hostIps = []
        hostDescriptions = []
        for line in hostsFile.readlines():
            hostIp, hostDescription = line.strip().split(',')
            hostIps.append(hostIp)
            hostDescriptions.append(hostDescription)
    return hostIps, hostDescriptions

def pingSweep(count,filename,dns,debug,sleep):

    coloredlogs.install()
    logger = logging.getLogger(__name__)
    if not debug:
        coloredlogs.install(level='INFO')
        logging.warning('LOGGING IS SET TO INFO')
    elif debug:
        coloredlogs.install(level='DEBUG')
        logging.info('LOGGING IS SET TO DEBUG')
    logging.debug('Iterating through hosts in {}, {} times.'.format(filename, count))
    while count > 0:
        try:
            hostsFile = os.path.abspath(filename)
            hostList, descriptionList = get_ips(hostsFile)
        except AttributeError as ex:
            logging.critical(ex)
            sys.exit(status=0)
        '''
        Loop through hosts array, ping each host, and return result
        '''
        for x in range(len(hostList)):
            result = subprocess.Popen(
                ['ping', '-c', '3', "-n", "-W", "1", hostList[x]],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
            if result == 0:
                logging.info('{} - {} is reachable'.format(hostList[x],descriptionList[x]))
                if dns:
                    try:
                        hostname = socket.gethostbyaddr(hostList[x])[0]
                        logging.info('hostname = {}'.format(hostname))
                    except socket.herror:
                        logging.debug('DNS lookup failed for {}'.format(hostname))
                        pass
                logging.info('Sleeping {} seconds'.format(sleep))
                time.sleep(sleep)
            else:
                logging.critical('---> {} - {} is unreachable'.format(hostList[x],descriptionList[x]))
                if dns:
                    try:
                        hostname = socket.gethostbyaddr(hostList[x])[0]
                        logging.info('hostname = {}'.format(hostname))
                    except socket.herror:
                        logging.debug('DNS lookup failed for {}'.format(hostname))
                        pass
                logging.info('Sleeping {} seconds'.format(sleep))
                time.sleep(sleep)
        count -= 1

def main():
    # Set options for passing arguments to the script
    parser = argparse.ArgumentParser()

    # -f option for specifying the input filename is required
    parser.add_argument('-f', '--filename', required=True,
                    type=str,
                    help="a string for the input file (e.g. - hosts.csv or hosts.txt")
        # - option for specifying the input filename is required
    parser.add_argument('-d', '--dns', action='store_true')
    parser.add_argument('-c', '--count', required=False,
                        type=int,
                        nargs='?',
                        default=1,
                        const=1,
                        help="enter number of times you'd like to perform ping sweep")
    parser.add_argument('-t', '--debug', action='store_true', default=False,
                        help="set this option to set the logging level to debug.")
    parser.add_argument('-s', '--sleep', required=False, type=int, default=1, help="an integer for the time (in seconds) to sleep in between icmp iterations")

    args = parser.parse_args()
    pingSweep(args.count,args.filename,args.dns,args.debug,args.sleep)

if __name__ == '__main__':
    main()
