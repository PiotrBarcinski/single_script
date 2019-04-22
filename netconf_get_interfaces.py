#!/usr/bin/env python

from ncclient import manager
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
PASS = 'xxxx'

# create a main() method
def get_gigabitethernet_interfaces():
    """Main method that retrieves the interfaces from config via NETCONF."""
    with manager.connect(host=HOST, port=PORT, username=USER, password=PASS,
                         hostkey_verify=False, device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        interface_filter = '''
                              <filter>
                                  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                                    <interface>
                                    <GigabitEthernet>
                                    </GigabitEthernet>
                                    </interface>
                                  </native>
                              </filter>
                              '''

        # Pretty print the XML reply
        xml_dom = xml.dom.minidom.parseString(str(m.get_config('running', interface_filter)))
        # print (xml_dom)
        # print(xml_dom.toprettyxml(indent="  "))
        interface_name = xml_dom.getElementsByTagName("name")
        description = xml_dom.getElementsByTagName("description")
        ip_address = xml_dom.getElementsByTagName("address")

        i=0
        for i in range(0,len(interface_name)):
            print ("interface name: GigabitEthernet" + (interface_name[i].firstChild.nodeValue))
            try:
                print("interface description: " + (description[i].firstChild.nodeValue))
            except:
                print ("interface description: NO DESCRIPTION ")
            try:
                print("interface ip adress: " + (ip_address[i].firstChild.nodeValue))
            except:
                print("interface ip adress: NO IP ADDRESS")
            print ("\n")
            i+=1
        return True


def main():
    """Simple main method calling our function."""
    get_gigabitethernet_interfaces()


if __name__ == '__main__':
    main()