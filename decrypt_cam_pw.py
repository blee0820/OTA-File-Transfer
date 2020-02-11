import getpass
import nacl.secret
import nacl.utils 
import base64
import sys

from sql_conn import connector
from decrypt_sod_key import sod_key_decrypt

"""
Driver for decrypting the encrypted password retrieved from database.
Utilizes Base64 encoding and PyNaCl module for Secret-Key encryption.
"""

def cam_pw_decrypt(cam_id, cam_count):
    try:
        # Call connector() to connect to database and retrieve requested info
        cam_info = connector(cam_id)
        requested_IP = cam_info.get('camera_IP')
        requested_cam_pass = cam_info.get('camera_pw')
        
        # Call sod_key_decrypt() to retrieve sod_key required to 
        # decrypt encrypted password from database
        sod_key = sod_key_decrypt(cam_count)
        encrypted = base64.b64decode(requested_cam_pass)
        box = nacl.secret.SecretBox(sod_key, encoder=nacl.encoding.Base64Encoder)
        decrypted = box.decrypt(encrypted)
        password = decrypted.decode('utf-8')
        retrieved_info = {
            'cam_IP': requested_IP,
            'password': password
        }
        return retrieved_info  
    except KeyboardInterrupt:
        print("Exiting Program")
        sys.exit(0)
    except:
        print("Camera Password Decryption Error")
        sys.exit(1)
        
if __name__ == '__main__':
    cam_pw_decrypt(cam_id, cam_count)