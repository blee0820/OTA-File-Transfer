import getpass
import nacl.secret
import nacl.utils 
import base64
import sys
import pickle

"""
Driver to decrypt sod_key. 
sod_key is used to securely decrypt the encrypted camera password
retrieved from the MySQL database.
"""

def sod_key_decrypt(cam_count):
    try:
        # Always ask for user input on first camera and save info on a .pickle file
        if cam_count == 1:
            auth_key = getpass.getpass("Enter password to decrypt sod key: ").encode()
            auth_key_dict = {'auth_key': auth_key}
            filename = 'auth_key.pickle'
            outfile = open(filename, 'wb')
            pickle.dump(auth_key_dict, outfile)
            outfile.close()
        # If there is more than one camera needing a file transfer,
        # open .pickle file to load data to bypass user input
        else:
            pickle_file = open('auth_key.pickle', 'rb')
            load_pickle = pickle.load(pickle_file)
            auth_key = load_pickle['auth_key']
            pickle_file.close()
        box = nacl.secret.SecretBox(auth_key)
        sod_key = box.decrypt(b"nx\x90\x85\xe1\x16\xc7\xeb\xb8]Ij*\xbdp\xfa\xea\xf8\x90o\x11\xac\xe6\x7f\x1b\xb9\xe1\xd5\xd7\x89\x04\x8e7-uBb\xa8yL`\x16\xf8\xa8\xc7'\xe9\x90\x15\x8fN\\\x89\x94q\xe7{\x81\x00\xe4\xef\xd4a\xf1\x1d\x08\\\x9ci\xd7X\xdd\xaa\x1c\xf9\xe8\xa3w\xed\x92\x8e\xa2\x07\x94")
        box = nacl.secret.SecretBox(sod_key, encoder=nacl.encoding.Base64Encoder)
        return sod_key
    except KeyboardInterrupt:
        print("Exiting Program")
        sys.exit(0)
    except:
        print("Sodium Key Decryption Error")
        sys.exit(1)
        
if __name__ == '__main__':
    sod_key_decrypt(cam_count)