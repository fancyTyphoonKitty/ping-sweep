#!/usr/local/bin/python3
import socket
import time
import subprocess
import sys
import argparse
import os
import coloredlogs
import logging
import time
coloredlogs.install()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def pingSweep(count,filename,dns):
    logging.info(count)
    while count > 0:
        try:
            hostsFile = os.path.abspath(filename)
            hostList, descriptionList = get_ips(hostsFile)
        except AttributeError:
            sys.exit(status=0)
        '''
        Loop through hosts array, ping each host, and return result
        '''
        for x in range(len(hostList)):
            result = subprocess.Popen(
                ['ping', '-c', '1', "-n", "-W", "2", hostList[x]],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
            if result == 0:
                logging.info('{} - {} is reachable'.format(hostList[x],descriptionList[x]))
                if dns:
                    try:
                        hostname = socket.gethostbyaddr(hostList[x])[0]
                        logging.info('hostname = {}'.format(hostname))
                    except socket.herror:
                        pass
            else:
                logging.critical('---> {} - {} is unreachable'.format(hostList[x],descriptionList[x]))
                if dns:
                    try:
                        hostname = socket.gethostbyaddr(hostList[x])[0]
                        logging.info('hostname = {}'.format(hostname))
                    except socket.herror:
                        pass
        count -= 1
    time.sleep(2)

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
    args = parser.parse_args()
<<<<<<< HEAD
    pingSweep(args.count,args.filename,args.dns)
    
=======
    try:
        hostsFile = os.path.abspath(args.filename)
        hostList, descriptionList = get_ips(hostsFile)
    except AttributeError:
        sys.exit(status=0)
    '''
    Loop through hosts array, ping each host, and return result
    '''
    for x in range(len(hostList)):
        result = subprocess.Popen(
            ['ping', '-c', '2', "-n", "-W", "2", hostList[x]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        if result == 0:
            logging.info('{} - {} is reachable'.format(hostList[x],descriptionList[x]))
            if args.dns:
                try:
                    hostname = socket.gethostbyaddr(hostList[x])[0]
                    logging.info('hostname = {}'.format(hostname))
                except socket.herror:
                    logging.critical('Reverse DNS lookup failed!')
            time.sleep(1)
        else:
            logging.critical('---> {} - {} is unreachable'.format(hostList[x],descriptionList[x]))
            if args.dns:
                try:
                    hostname = socket.gethostbyaddr(hostList[x])[0]
                    logging.info('hostname = {}'.format(hostname))
                except socket.herror:
                    logging.critical('Reverse DNS lookup failed!')
            time.sleep(1)
>>>>>>> 49deaeeb72f94018ba8d4d60e647d65470960c6d

if __name__ == '__main__':
    main()