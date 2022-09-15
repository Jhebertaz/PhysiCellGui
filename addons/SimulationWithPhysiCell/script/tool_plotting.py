#############
## Package ##
#############
import os

def get_script_name(script_path):
    """Retrieve script_name from path"""
    return os.path.abspath(script_path).split(os.sep)[-1].replace('.py', '')
