import paramiko
import time
import re



def command_to_send(remote_conn, command):
    '''
    terminal length 0 is sent before every command to avoid situation that Cisco terminal could
    remove some part of output. this command makes terminal lenght maks value

    word "#" is used to verify when Switch gives output from device (e.g.:
    Router#sh run | i snmp
    snmp-server location Server Room
    Router#
    )

    next we are looking for command "termina length" this is because some times in banner we have "#" chart
    so to avoid issues we begin checking output from device after command "terminal length"

    next till "#" is not in output from switch, script is waiting for output from device

    '''
    remote_conn.send('\n')
    remote_conn.send('terminal length 0')
    remote_conn.send('\n')
    time.sleep(2)
    remote_conn.send(command)
    remote_conn.send('\n')
    word = "#"
    convert_output=[" "]
    convert_outputs = []
    full_output = ""
    while word not in convert_output[-1]:
        time.sleep(3)
        data = remote_conn.recv(10000).decode("utf-8")
        full_output += data
        convert_output = data.splitlines()
        convert_outputs.append(convert_output)
    outputRegex = re.compile(r'(terminal length 0)(.|\n)*')
    outputRegexSearchOutput = outputRegex.search(full_output)
    outputRegexSearchOutputGroup = outputRegexSearchOutput.group()
    return outputRegexSearchOutputGroup

def main ():
    #provide credentials
    login = ""
    password = ""
    list_of_ips = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]

    for ip in list_of_ips:
        try:
            remote_conn_pre = paramiko.SSHClient()
            remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn_pre.connect(ip, username=login,
                                    password=password,
                                    look_for_keys=False, allow_agent=False)
            remote_conn = remote_conn_pre.invoke_shell()
        except:
            print ("i cannot connect to device" + ip)
            continue

        list_of_commands = ['sh ip int br', 'sh vlan', 'sh bgp']
        for command in list_of_commands:
            output = command_to_send(remote_conn,command)
            print (output)


if __name__ == "__main__":
    main()