import json

from machineroom.tunnels.conn import *
from machineroom.const import Config as MachineConfig
from machineroom.worker import internal_work

MachineConfig.WS_LOCAL = "/Users/hesdx/Documents/sroom"
MachineConfig.PUB_KEY = "/Users/hesdx/.ssh/id_rsa.pub"
MachineConfig.LOCAL_KEY_HOLDER = "/Users/hesdx/.ssh"
MachineConfig.MY_KEY_FEATURE = "apple@dapdefi"


MachineConfig.DATAPATH_BASE = "/Users/hesdx/Documents/sroom"
MachineConfig.PUB_KEY = "/Users/hesdx/.ssh/id_rsa.pub"
MachineConfig.LOCAL_KEY_HOLDER = "/Users/hesdx/.ssh"
MachineConfig.MY_KEY_FEATURE = "apple@dapdefi"
MachineConfig.REMOTE_WS = "/home/ckb"



# if __name__ == '__main__':
#    internal_work()

if __name__ == '__main__':
    # use_macos_vpn_on("IPANT")
    internal_work()
