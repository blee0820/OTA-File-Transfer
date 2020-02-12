import paramiko
import mysql.connector
import os
import sys
import getpass
import time
import pickle

from paramiko import SSHClient, AutoAddPolicy
from sql_conn import connector
from decrypt_cam_pw import cam_pw_decrypt
from parse_commands import parse_commands
from scp import SCPClient

"""
Main driver for transferring files from local machine to remote device(s).

The purpose of this program is to transfer new files onto remote device(s) from a local host machine.

The program retrieves necessary information to successfully SSH into remote device(s) and
based on user's input of file's user, permission, and directory to be placed in,
generates a bash script that gets transferred onto the remote device along with
the files that need to be transferred. Multiple remote devices can be identified to have files transferred
into them.

A .pickle file is generated which saves user inputted data as a dictionary. These .pickle files are
saved temporarily on user's local machine. 

If there is only one camera needing a file transfer, it will always ask for the user input where
necessary. If there is more than one camera, it will take the updated .pickle file from the first remote device's
file transfer procedure and use data to populate any entries requiring user input. This eliminates the need
to have the user constantly inputting values where necessary after the first remote device has passed its file transfer
procedure and automates the process on all other remote devices.
 
Once the bash script is on the remote device, it executes and starts the transfer process, gracefully rebooting
each remote device as the file process is complete.

After all remote devices have successfully completed their file transfer processes, the main driver program will
remove any generated .pickle files along with the generated bash script.

A bash script was created to be dynamically populated and transferred over due to the complexity and
unreliability of sending individual commands to the remote device over SSH. The remote device's terminal output
was wanted to be displayed to the user and in order to do so, the ssh connection must have been closed and 
the terminal output to be read each time this was wanted to be performed. Creating a dynamic bash script which
would complete all work and then display all terminal output at once proved to be the more efficient way to achieve this.
"""

def pickler(username=None, port=None, su_pw=None, auth_key=None):
        try:
            # Creates .pickle file to store user inputted data.
            if username and port and su_pw:
                user_dict = {'username': username, 'port': port, 'su_pw': su_pw}
                filename = 'user.pickle'
                outfile = open(filename, 'wb')
                pickle.dump(user_dict, outfile)
                outfile.close()
            
            if auth_key:
                infile = open('user.pickle', 'rb')
                user_dict = pickle.load(infile)
                user_dict.update({'auth_key': auth_key})
                outfile = open('user.pickle', 'wb')
                pickle.dump(user_dict, outfile)
                infile.close()
                outfile.close()
            return user_dict
        except Exception as e:
            print("Error has occurred when pickling files. See below.")
            print(e)
            sys.exit(1)

class Transfer:
    def __init__(self, cam_id, cam_count):
        self.cam_id = cam_id
        self.cam_count = cam_count
        
    def transfer_files(self):
        print("These are the files marked for transfer:")
        try:
            file_details = {"Owner": None, "Permission": None, "Directory": None}
            service_file = []
            files = next(os.walk('./bash-scripts/transfer-files'))[2]
            
            # store all .service files in a separate list to be parsed later
            for file_list in files:
                print("-",file_list)
                if ".service" in file_list:
                    service_file.append(file_list)
            
            # print user instructions        
            print("")
            print("*"*87)
            print("For each file, please submit the following info, each submission confirmed with Enter Key")
            print("Owner: (please use format <user:user>)")
            print("Permission: (numeric value or symbolic notation)")
            print("Directory the file should be placed into: (absolute path name)")
            print("*"*87)
            print("")
            
            # begin bash script template
            f = open("./bash-scripts/transfer.sh", "w+" )       
            f.write("#!/bin/bash"\
                    "\n\ntransfer(){"\
                    "\n\tmount - / - oremount,rw"\
                    "\n\tcd /tmp-folder/bash-scripts/transfer-files\n")
            
            # dynamically populate bash script based on user input
            for file in files:
                print("File:", file)
                for key in file_details:
                    file_details[key] = input("{}: ".format(key))
                f.write("\n\tchown " + file_details["Owner"] + " " + file +\
                        "\n\tchmod " + file_details["Permission"] + " " + file +\
                        "\n\techo Copying " + file + " to " + file_details["Directory"] +\
                        "\n\tcp " + file + " " + file_details["Directory"] + " || { echo Failed to copy " + file + " to " + file_details["Directory"] + "; exit 1; }"\
                        "\n\tcmp -s " + file_details["Directory"] + "/" + file + " " + file +  " || { echo Original " + file + " and copied " + file + " at " + file_details["Directory"] + " seem to be different. Aborting file transfer.; exit 1; }\n"
                        )  
                print("")
            
            # if any .service files are detected, add code to bash script to enable service(s)    
            if service_file:
                print("Service file(s) detected. Service file(s) will be attempted to be enabled on the camera.")
                print("")
                for s_file in service_file:
                    s_file = s_file.strip(".service")
                    print("Pushing command to enable " + s_file)
                    f.write("\n\tsystemctl enable " + s_file)
            f.write("\n\trm -r /tmp-folder"
                    "\n\tmount - / -oremount,ro"\
                    "\n}"\
                    "\ntransfer")
            f.close()        
        except KeyboardInterrupt as ki:
            print("Terminating transfer process.")
            print(ki)
  
    def device_SSH(self):
        try:
            print("")
            print("*** Starting Transfer for", self.cam_id,"***")
            if self.cam_count == 1:
                print("")
                username = input("Enter username: ")
                port = input("Enter port number: ")
                su_pw = getpass.getpass("Enter su password: ")
                pickler(username=username, port=port, su_pw=su_pw)
            else:
                pickle_file = open('user.pickle', 'rb')
                load_pickle = pickle.load(pickle_file)
                username = load_pickle['username']
                port = load_pickle['port']
                su_pw = load_pickle['su_pw']
                pickle_file.close()
        except KeyboardInterrupt as ki:
            print(ki)
            sys.exit(0)
        except Exception as e:
            print(e)
            print("An Exception has occurred.")
            print("")
            sys.exit(1)
                       
        try:
            # Retrieve final decrypted IP address and password
            # Calls cam_pw_decrypt() to begin decryption of password
            cam_info = cam_pw_decrypt(self.cam_id, self.cam_count)
            host = cam_info.get('cam_IP')
            password = cam_info.get('password')
            
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=username, password=password)
            
            print("")
            print("SSH connection to camera", self.cam_id, "at", host, "established.")
            print("")
            print("Attempting to transfer files")
            print("")

            try:                
                # call parse_commands() to execute appropriate Linux commands
                stdin, stdout, stderr = ssh.exec_command("su \n")
                stdin.write(su_pw + "\n")
                
                reboot = 0
                while reboot == 0:
                    stdin.write('killall php\n' + 'mount - / -oremount,rw\n' + 'mkdir -m 757 -p /tmp-folder\n')    
                                                    
                    # push required files to camera from local machine
                    with SCPClient(ssh.get_transport(), sanitize=lambda x: x) as scp:
                        try:
                            if self.cam_count == 1:
                                self.transfer_files()
                            scp.put('bash-scripts', '/tmp-folder', recursive=True)
                            scp.close()
                            print("")
                            print("Required files successfully transferred to camera.")
                            print("")
                        except Exception as e:
                            scp.close()
                            ssh.close()
                            print(e)
                            print("Error transferring required files to camera.")
                            print("Terminating program.")
                            print("")
                            sys.exit(1)

                    script = parse_commands()
                    for cmd in script:
                        stdin.write(cmd + '\n')
                                            
                    stdin.close()
                    out = stdout.read().decode()                
                    print("Terminal output:")
                    print(out)
                    reboot = 1
            except Exception as e:
                ssh.close()
                print(e)
                print("Error parsing and executing Linux commands.")
                print("Closing SSH session and terminating program.")
                sys.exit(1)     
        except paramiko.AuthenticationException:
            ssh.close()
            print("Authentication Error. SSH connection terminated.")
            sys.exit(1)
        finally:
            print("Closing SSH connection to " + host + ".")
            print("System will now reboot, please wait.")
            print("")
            stdin, stdout, stderr = ssh.exec_command("su \n")
            stdin.write(su_pw + "\n")
            stdin.write("systemctl reboot\n")
            ssh.close()
            time.sleep(5)
                        
if __name__ == '__main__':        
    cam_id = [12345, 67890]
    
    for cam_count, cam in enumerate(cam_id, 1):        
        start_transfer = Transfer(cam, cam_count)
        start_transfer.device_SSH()
    os.remove('auth_key.pickle')
    os.remove('user.pickle')
    os.remove('bash-scripts/transfer.sh')
    print("Transfer process complete. Program will now exit.")
    sys.exit(0)
        
    
