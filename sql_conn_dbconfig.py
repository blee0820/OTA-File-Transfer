import os
from configparser import RawConfigParser

"""
Imports and parses config.ini file which includes
MySQL database login information
"""

curr_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(curr_dir, 'config.ini')

def read_db_config(file=config_file, section='mysql'):
    db = {}
    
    # create parser and read .ini file
    parser = RawConfigParser()
    parser.read(file)
    
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, file))
    return db

if __name__ == '__main__':
    read_db_config()