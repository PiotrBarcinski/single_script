import paramiko
import time


def main():
    # credentials
    login = ""
    password = ""
    ips = ['10.1.1.1', '10.1.1.2', '10.1.1.3', '10.1.1.4']
    switch_name = "Switch-"
    today = time.strftime("%Y-%m-%d-%H-%M")
    # create csv file with information "ip, hostname, name changed / not changed"
    # this is for report to check if everything went ok or not
    file_csv = "switch_change_name" + today + ".csv"
    # open file for write in specified location
    csv = open('C:\\Projects\\single_projects\\' + file_csv, "w")
    i = 1
    for ip in ips:
        switch_full_name = switch_name + str(i)
        try:
            print("change hostname on switch:")
            print(ip)
            print(switch_full_name)
            # define and send commands to send on device
            commands = ['conf t ', "hostname " + switch_full_name]
            print("sending commands:")
            print(commands)
            send_command_to_switch(ip, commands, login, password)
            # save results to csv file
            # define each row in csv
            row = ip + "," + switch_full_name + "," + "NAME CHANGED" + "\n"
            csv.write(row)
            i += 1
        except:
            print("ERROR ON SWITCH:")
            print(switch_full_name)
            row = ip + "," + switch_full_name + "," + "ERROR - NAME DID NOT CHANGED - CANNOT LOG ON DEVICE" + "\n"
            csv.write(row)
            i += 1

    csv.close()


def send_command_to_switch(ip, commands, login, password):
    remote_conn_pre = paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(ip, port=22, username=login, password=password,
                            look_for_keys=False, allow_agent=False)

    remote_conn = remote_conn_pre.invoke_shell()
    time.sleep(1)
    remote_conn.send("\n")
    time.sleep(1)
    # send first command
    remote_conn.send(commands[0])
    time.sleep(1)
    remote_conn.send("\n")
    time.sleep(1)
    # send second command
    remote_conn.send(commands[1])
    time.sleep(1)
    remote_conn.send("\n")
    time.sleep(1)
    output = remote_conn.recv(5000).decode("utf-8")

    return True


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted.')
