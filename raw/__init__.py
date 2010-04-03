from nntp import Server
from settings import *

def get_server():
    return Server(USENET_HOST, USENET_PORT, USENET_USER, USENET_PW)
    