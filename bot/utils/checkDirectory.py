import os
def check_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)