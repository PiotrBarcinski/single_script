import paramiko
import re
import time
import os


class Switch():
    def __init__(self, bin_file_name, file_weight, md5):
        self.bin_file_name = bin_file_name
        self.file_weight = file_weight
        self.md5 = md5


def verify_md5(remote_conn, bin_file_name, md5):
    check_verify_md5_stauts = False
    verify_md5_status = False

    remote_conn.send("\n")
    remote_conn.send("\n")
    remote_conn.send("verify /md5 flash:" + bin_file_name)
    time.sleep(5)
    remote_conn.send("\n")
    remote_conn.send("\n")

    time.sleep(25)

    while (check_verify_md5_stauts != True):
        output = remote_conn.recv(300).decode("utf-8")
        for line in output.splitlines():
            if md5 in line:
                print("Md5 is verified and is ok")
                verify_md5_status = True
                check_verify_md5_stauts = True
                break
            else:
                print ("MD5 is not ok - check manually")
                verify_md5_status = False
        time.sleep(2)

    return verify_md5_status

def upload_ios_software(remote_conn, tftp_server_ip, bin_file_name):
    remote_conn.send("\n")
    remote_conn.send(
        "copy ftp://" + tftp_server_ip + "/" + bin_file_name + " flash:" + bin_file_name)
    time.sleep(2)
    remote_conn.send("\n")
    remote_conn.send("\n")
    time.sleep(5)
    check_uploaded_stauts = False

    while (check_uploaded_stauts != True):
        output = remote_conn.recv(4000).decode("utf-8")
        line_sum = ""
        for line in output.splitlines():
            if "bytes copied" not in line_sum:
                line_sum += line
                print(line)
                print(line_sum)
                print("I am still copying IOS")
            else:
                print(line)
                print("Copying finished")

        time.sleep(20)

    return True

def check_if_enough_free_space(remote_conn):
    # check ios command
    remote_conn.send("dir flash:")
    remote_conn.send("\n")
    time.sleep(2)
    output = remote_conn.recv(2000).decode("utf-8")
    # check free space on device
    free_space_on_device_regex = re.compile('\((([\d].*) b)')
    free_space_on_device = free_space_on_device_regex.search(output)

    # return free space
    return free_space_on_device.group(2)

def check_current_ios(remote_conn, device):
    # check current IOS running on a switch
    remote_conn.send("sh ver | i image")
    remote_conn.send("\r\n")
    time.sleep(5)
    output_from_switch = remote_conn.recv(5000).decode("utf-8")
    print(output_from_switch)
    regex_ios = re.compile(r'System image file is \"(.*)\"')
    found_ios = regex_ios.search(output_from_switch)
    print(found_ios)
    found_full_path_ios = found_ios.group(1)
    if "flash:/"+device.ios_version in found_full_path_ios:
        print("new IOS already up to date")
        result = True
    else:
        print("no new IOS in boot, keep going and add automatically")
        result = False
    return result

def add_boot(remote_conn, found_full_path_ios):
    try:
        remote_conn.send("conf t")
        remote_conn.send("\r\n")
        time.sleep(2)
        remote_conn.send("boot system flash:/c2960-lanbasek9-mz.152-4.E7.bin;" + found_full_path_ios)
        remote_conn.send("\r\n")
        time.sleep(2)
        remote_conn.send("exit")
        remote_conn.send("\r\n")
        time.sleep(1)
        remote_conn.send("write")
        remote_conn.send("\r\n")
        time.sleep(1)
    except:
        print("cannot add commands 'boot system flash:/'")

def reboot(hostname, remote_conn):

    response = os.system("ping " + hostname)
    # and then check the response...
    print(response)
    if response == 0:
        pingstatus = "Network Active"
        remote_conn.send("reload in 10")
        remote_conn.send("\r\n")
        time.sleep(7)

    else:
        pingstatus = "Network Error"

    return pingstatus

def add_commands_to_boot_and_reboot_device(ip, remote_conn, found_full_path_ios,device):
    remote_conn.send("dir")
    remote_conn.send("\r\n")
    time.sleep(2)
    output_from_switch = remote_conn.recv(5000).decode("utf-8")

    if device.bin_file_name in output_from_switch:
        # command to send to set new boot order
        add_boot(remote_conn, found_full_path_ios)
    else:
        result = "required ios is not on flash on device."
        return False, result

    print("reboot begin")
    try:
        c = reboot(ip,  remote_conn)

        print(c)
    except:
        print("reboot failed on device " + ip)

    return True



#provide credentials
login = ""
password = ""
tftp_server_ip = "10.10.10.10"


def main ():
    #define IPs on which you would like to upgrade soft
    ips = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]

    #define device, values for device are: Switch type (full name), IOS version for upgrade,
    #IOS version file name (.bin), weight of file (in bytes), md5 checksum for verification
    device = Switch("c2960-lanbasek9-mz.150-2.SE9.bin",
                    "11831020", "f7b493e85969b23606fb7c0962cd5cea")

    for ip in ips :
        # paramiko (ssh) connection to defined device
        try:
            remote_conn_pre = paramiko.SSHClient()
            remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn_pre.connect(ip, username=login,
                                    password=password,
                                    look_for_keys=False, allow_agent=False)
            remote_conn = remote_conn_pre.invoke_shell()
        except:
            print ("cannot login on device " + ip)
            print ("go to next device")
            continue

        # check if there is new IOS on flash already
        # you can check if there is enough space on flash, but this is not needed, we can also do "try except" and if there is not enough free space
        # the function will go to exception and let us know about that
        # then upload on Flash needed IOS version, if than:
        # verify md5
        if check_if_enough_free_space(remote_conn) > device.file_weight:
            print("we have enough space")

            # upload software on device
            try:
                upload_ios_software(remote_conn, tftp_server_ip, device.bin_file_name)
            except:
                print ("upload software UNSECCFUL - verify what happened manually \n script goes to next IP from list")
                continue

            # verify md5 checksum for new ios
            if verify_md5(remote_conn, device.bin_file_name, device.md5) == True:
                print ("md5 verified successfully")
            else:
                print ("md5 not verified - check manually")
        else:
            # there is no enough space on flas on SW
            end = time.time()
            print("There is no space to download IOS")
            continue
            # log that there is not enough space and operation time

        time.sleep(2)

        # check if the IOS is alread on Flash on device
        # if not, go to next IP from list
        found_full_path_ios= check_current_ios(remote_conn, device)
        if found_full_path_ios == False:
            continue

        #add commands boot file to boot and reboot device
        result = add_commands_to_boot_and_reboot_device(ip, remote_conn, found_full_path_ios,device)
        if result == False:
            print(result)
            continue

        print ("finito for switch" + ip)
        remote_conn_pre.close()


if __name__ == "__main__":
    main()

