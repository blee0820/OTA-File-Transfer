# OTA File Transfer

### <u>Purpose</u>
This OTA File Transfer tool allows the transfer of newly introduced files from a local machine onto Linux-powered devices via SSH. In a workplace environment where multiple Linux devices are deployed out in the field, there calls for a need to be able to introduce new, auxiliary files onto said devices on a grand scale. This may call for specific files being placed in specific directories with certain file information (such as file owner and permission). This program is created to allow multi-file and multi-device file transfers over SSH, prevent the need for having an admin to individually SSH into each individual device in order to perform a file transfer, and automate the process as seamlessly as possible. The greater goal of this program was to be able to save the admin and the workspace significant time and resources should the need for such a process to be executed.

### <u>Getting Started</u>
This program requires a Python 3 environment along with the installation of the following modules:
- paramiko
- pynacl
- scp

The above modules can be installed by running the following commands from your terminal:
```
python -m pip paramiko
```
```
python -m pip pynacl
```
```
python -m pip scp
```

You will also need access to a MySQL database and the driver 'MYSQL Connector'.
The 'MYSQL Connector' driver can be downloaded [here](https://dev.mysql.com/downloads/connector/python/).

Once downloaded, the driver can be installed by running the following commands from your terminal:
```
python -m pip install mysql-connector
```

To run the program, navigate to the location of the files in terminal and run
```
python .\transfer.py
```

**Notes:** 
- This program was developed on Windows operating system. A Linux port is currently a work in process.
- Certain lines of code are modified or renamed to mask sensitive information.
- Due to the nature of this program being workspace-specific, a test run may not be successful in your own environment. Screenshots have been attached to demonstrate the workings of this program.

### <u>System Design</u>
This program introduces features designed to make the file transfer process as seamless and as automated as possible. The user is asked to provide credentials to begin the file transfer process. A locally saved configuration file containing database login information is then parsed and used to gain access to a MySQL database. A SQL command is executed on the databse to retrieve specific data based on each individual device requiring a file transfer. Once all required data is retrieved, a SSH connection is made with the remote device. A temporary folder is created on the remote device to house the files and scripts required to execute a successful transfer, which will be transferred from the local machine. The program parses the local machine where the file to be transferred are held and asks the admin to input the following file details for each file to be transferred: owner, permission, and final destination. Based on the inputted information, a bash script is dynamically created that will copy the file(s) to their respective final destinations and will also check for any errors upon the copying process. The folder is then transferred from the local machine onto the temporary folder in the remote device where the bash script will be called to execute the copy process.

### <u>Features</u>
1. **getpass()** was used to mask any password input. This was preferred over *input()* for securely inputting any required passwords.
Password decryption was handled using a very specific manner.
2. Password decryption was handled in a very specific manner using the **NaCl** module which generates an encrypted *sod_key* (sodium key). The admin is asked to provide a password in order to decrypt the *sod_key* which is then used to decrypt encrypted passwords stored in the database. This provides another wall of security when it comes to decrypting sensitive passwords and prevents unauthorized users from gaining access to sensitive information.
3.  The **SCPClient()** module is used to transport files onto remote devies. This allows the transfer of individual files or entire directories from a local machine. If more than one file is required for transfer, instead of transferring each individual file one at a time, the entire directory is transferred. This directory is transferred onto the remote device on a temporary location which contains all files needed for a file copy. Once the copying process is complete, this folder is completely removed from the device before a graceful restart of the remote device.
4.  A dynamically created bash script is created based on the admin's input of credentials and file information (file user, permission, and destination) which is used by the remote device to perform the necessary file copy process on the device and copy checks. If there are any service files that are copied over that need to be enabled on the remote device, the program dynamically searches for any service files and writes code on the bash script to enable those service files.
5.  A requirement for this program was to be able perform the file transfer and copy process as automated as possible. If there are more than one remote devices requiring a file transfer, the admin should not need to perform any input actions after the first file transfer process. This was achieved using the **pickle** module. For instance, if there are 5 remote devices requiring a file transfer, on the first pass of the first remote device, the **pickle** module saves admin inputted information as a dictionary object as a .pickle file. The information saved on this .pickle file can then be accessed for later use. This was implemented to prevent the admin from having to enter in credentials on every remote device after the first. After the file transfer on the first remote device is successful, it automatically goes onto the next remote device and begins the file transfer and copy process with no further admin input required.

### <u>Program Demo</u>
(Click the thumbnail below to be taken to a working demonstration.)

Due to the nature of the program, a working live demo or unmodified screenshots cannot be displayed to due displaying workplace-specific information. In this demo, two different remote devices were identified to have files transferred onto. First, admin credentials are asked to be entered to begin the file transfer process. Then the user is asked to input file-specific information: user, permission, and final directory. This information is then saved as a .pickle file to be utilized in the next remote device for an automated file transfer process. Once this information is entered, a bash script is dynamically created (left side of screen) which will be then used to send commands to the remote device to perform the file transfer to verify the file transfer's integrity. Once the file transfer is deemed successful, the program will then reboot the remote device and then move on to the next one in line. From here on, the process is automated, requiring no input from the user.

[![OTA File Transfer](https://i.imgur.com/d1AiZ0b.jpg)](https://www.youtube.com/watch?v=d1WKdSv4bg8 "OTA File Transfer")

### <u>Acknowledgements</u>
I would like to give thanks to my colleague KC for approaching me with the idea of implementing a file transfer application in our workplace. It gave me great exposure to system design, inner workings of Python, and great modules that I otherwise would have not been exposed to. It was also my first real exposure to writing a full-ledged Python program. It was a great pleasure working on an application that serves practical use in the workplace to reduce labor, time, and resources, and I definitely see great potential in this program to be improved and expanded upon. It should be noted that an application of this purpose has yet to exist in our workplace in its lifetime so it is a great introduction of an application that can really be used to serve the future of the company. Also, hats off to KC for giving me assistance in implementing the sod_key module to work with my program. You're the man!

Next on the plate is to complete work on a modification of this program which would patch existing files on remote devices with files provided on a local machine. After that is complete, it would be merged and implemented into a UI where any admin (given the permissions to do so) could easily perform file transfer and patching process on tens, if not hundreds, remote devices from a single application with a touch of a button.
