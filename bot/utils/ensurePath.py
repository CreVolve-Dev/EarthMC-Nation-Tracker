import os

def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)