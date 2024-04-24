import json

from machineroom.tunnels.conn import *
from machineroom.const import Config as MachineConfig

MachineConfig.WS_LOCAL = "/Users/hesdx/Documents/sroom"
MachineConfig.PUB_KEY = "/Users/hesdx/.ssh/id_rsa.pub"
MachineConfig.LOCAL_KEY_HOLDER = "/Users/hesdx/.ssh"
MachineConfig.MY_KEY_FEATURE = "apple@dapdefi"

if __name__ == '__main__':
    use_macos_vpn_on("IPANT")
