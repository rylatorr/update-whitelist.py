#!/usr/bin/python3

READ_ME = '''
=== PREREQUISITES ===
Run in Python 3

Assign network tag "update_whitelist" to all networks that you want to add the whitelist entries to.

Install both requests & Meraki Dashboard API Python modules:
pip[3] install --upgrade requests
pip[3] install --upgrade meraki

=== DESCRIPTION ===
This script iterates through the org's networks that are tagged with the label
"update_whitelist". For each of these networks'
Remove the network tag/label "update_whitelist" afterwards.

=== USAGE ===
python[3] update_whitelist.py -k <api_key> -o <org_id> -w <domains, comma-separated>
'''

from datetime import datetime
import getopt
import logging
import sys
import time
import meraki
import requests

# Prints READ_ME help message for user to read
def print_help():
    lines = READ_ME.split('\n')
    for line in lines:
        print('# {0}'.format(line))

logger = logging.getLogger(__name__)

def configure_logging():
    logging.basicConfig(
        filename='{}_log_{:%Y%m%d_%H%M%S}.txt'.format(sys.argv[0].split('.')[0], datetime.now()),
        level=logging.DEBUG,
        format='%(asctime)s: %(levelname)7s: [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# https://developer.cisco.com/meraki/api-v1/#!get-network-appliance-content-filtering
# https://developer.cisco.com/meraki/api-v1/#!update-network-appliance-content-filtering

def main(argv):
    # Set default values for command line arguments
    api_key = org_id = arg_mode = None

    # Get command line arguments
    try:
        opts, args = getopt.getopt(argv, 'hk:o:w:')
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == '-k':
            api_key = arg
        elif opt == '-o':
            org_id = arg
        elif opt == '-w':
            whitelistArg = arg

    # Check if all required parameters have been input
    if api_key == None or org_id == None:
        print_help()
        sys.exit(2)

    # Instantiate a Meraki dashboard API session
    dashboard = meraki.DashboardAPI(
        api_key,
        output_log=False
        #log_file_prefix=os.path.basename(__file__)[:-3],
        #log_path='',
        #print_console=False
    )

    # Parse domain string to list
    whitelistDomainsToAdd = whitelistArg.split(",")

    # Get list of current networks in org
    networks = dashboard.organizations.getOrganizationNetworks(org_id)

    # Iterate through all networks
    for network in networks:
        # Skip if network does not have the tag "update_whitelist"
        if network['tags'] is None or 'update_whitelist' not in network['tags']:
            continue

        # Get current Content Filtering Settings
        currentContentFilteringSettings = dashboard.appliance.getNetworkApplianceContentFiltering(network['id'])

        currentWhitelist = currentContentFilteringSettings["allowedUrlPatterns"]

        # debug
        print(f'Current Whitelist:\n {currentWhitelist}')
        print(f'Whitelist Entries to add:\n {whitelistDomainsToAdd}')

        # Append entries to whitelist
        combinedWhitelist = currentWhitelist + whitelistDomainsToAdd
        # remove any duplicates
        combinedWhitelist = list(dict.fromkeys(combinedWhitelist))
        print(f'new whitelist to submit:\n {combinedWhitelist}')

        # Commit new content filtering settings
        dashboard.appliance.updateNetworkApplianceContentFiltering(network['id'], allowedUrlPatterns=combinedWhitelist)

if __name__ == "__main__":
    # Configure logging to stdout
    configure_logging()
    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # Set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # Tell the handler to use this format
    console.setFormatter(formatter)
    # Add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Output to logfile/console starting inputs
    start_time = datetime.now()
    logger.info('Started script at {0}'.format(start_time))
    inputs = sys.argv[1:]
    try:
        key_index = inputs.index('-k')
    except ValueError:
        print_help()
        sys.exit(2)
    inputs.pop(key_index+1)
    inputs.pop(key_index)
    logger.info('Input parameters: {0}'.format(inputs))

    main(sys.argv[1:])

    # Finish output to logfile/console
    end_time = datetime.now()
    logger.info('Ended script at {0}'.format(end_time))
    logger.info(f'Total run time = {end_time - start_time}')
