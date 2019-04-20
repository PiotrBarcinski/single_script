#!/usr/bin/env python

import logging
from ncclient import manager
import sys
import xml.dom.minidom


# the variables below assume the user is requesting access to a
# Nexus device running in VIRL in the  DevNet Always On Sandbox
# use the IP address or hostname of your Nexus device
# please login to devnet Sandbox and check what is up-to-date login /  password
HOST = 'ios-xe-mgmt.cisco.com'
# use the NETCONF port for your Nexus device
PORT = 10000
# use the user credentials for your Nexus device
USER = 'root'
PASS = 'xxxxx'
# XML file to open
FILE = 'get_interfaces.xml'


# create a main() method
def get_hostname():
    """Main method that retrieves the interfaces from config via NETCONF."""
    with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                         hostkey_verify=False, device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        hostname_filter = '''
                              <filter>
                                  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                                    <hostname>
                                    </hostname>
                                  </native>
                              </filter>
                              '''

        # Pretty print the XML reply
        xml_dom = xml.dom.minidom.parseString(str(m.get_config('running', hostname_filter)))
        hostname = xml_dom.getElementsByTagName("hostname")
        return (hostname[0].firstChild.nodeValue)


def main():
    """Simple main method calling our function."""
    hostname = get_hostname()
    print(hostname)


if __name__ == '__main__':
    sys.exitmain()