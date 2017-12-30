#!/usr/local/bin/python3
# import modules
import subprocess
import sys
import argparse
import os
import coloredlogs
import logging
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
# This command-line parsing code is provided.
# Make a list of command line arguments, omitting the [0] element
# which is the script itself.

def main():

    # Set options for passing arguments to the script
    parser = argparse.ArgumentParser()

    # -f option for specifying the input filename is required
    parser.add_argument('-f', '--filename', required=True,
                    type=str,
                    help="a string for the input file (e.g. - hosts.csv or hosts.txt")
        # - option for specifying the input filename is required
    parser.add_argument('-d', '--dns', required=False,
                    type=bool,
                    help="set -d or --dns option to perform a DNS reverse lookup on the ip address")
    args = parser.parse_args()
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
            ['ping', '-c', '1', "-n", "-W", "2", hostList[x]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        if result == 0:
            logging.info('{} - {} is reachable'.format(hostList[x],descriptionList[x]))
        else:
            logging.critical('---> {} - {} is unreachable'.format(hostList[x],descriptionList[x]))

if __name__ == '__main__':
    main()