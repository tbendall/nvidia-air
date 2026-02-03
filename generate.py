
import json
from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict

file_structure = {

    "format": "JSON",
    "title": "interpod_new",
    "ztp": "#!/bin/bash\n# Created by Topology-Converter v4.7.1\n#    Template Revision: v4.7.1\n\nfunction error() {\n  echo -e \"e[0;33mERROR: The Zero Touch Provisioning script failed while running the command $BASH_COMMAND at line $BASH_LINENO.e[0m\" >&2\n}\ntrap error ERR\n\nSSH_URL=\"http://192.168.200.1/authorized_keys\"\n# Uncomment to setup SSH key authentication for Ansible\n# mkdir -p /home/cumulus/.ssh\n# wget -q -O /home/cumulus/.ssh/authorized_keys $SSH_URL\n\n# Uncomment to unexpire and change the default cumulus user password\npasswd -x 99999 cumulus\necho 'cumulus:Lab123' | chpasswd\n\n# Uncomment to make user cumulus passwordless sudo\necho \"cumulus ALL=(ALL) NOPASSWD:ALL\" > /etc/sudoers.d/10_cumulus\n\n# Uncomment to enable all debian sources & netq apps3 repo\nsed -i 's/#deb/deb/g' /etc/apt/sources.list\nwget -q -O pubkey https://apps3.cumulusnetworks.com/setup/cumulus-apps-deb.pubkey\napt-key add pubkey\nrm pubkey\n\n# Uncomment to allow NTP to make large steps at service restart\necho \"tinker panic 0\" >> /etc/ntp.conf\nsystemctl enable ntp@mgmt\n\nexit 0\n#CUMULUS-AUTOPROVISIONING\n#CUMULUS-AUTOPROVISIONING",
    "content": {
        "nodes": {},
        "links": [],
        "oob": False,
        "netq": False

    },

}


nodes = {}

leafs = ["leaf5","leaf6"]
spines = ["spine3","spine4"]

interfaces = 16

interface_list = [f"swp{x}" for x in range(1,interfaces +1) ]
iface_index = 0
used_endpoints = set()
links = []
mac_counter = 1


@dataclass
class node:
    name: str
    interfaces: List[str]
    nic_model: str = "virtio"
    cpu: int = 1
    memory: int = 2048
    storage: int = 10
    positioning: Dict = field(default_factory=dict)
    features: Dict = field(default_factory=lambda: {"uefi": False, "tpm": False})
    pxehost: bool = False
    secureboot: bool = False
    oob: bool = False
    emulation_type = None
    network_pci: Dict = field(default_factory=dict)
    cpu_options: List = field(default_factory=list)
    storage_pci: Dict = field(default_factory=dict)
    used_ifaces: Set[str] = field(default_factory=set)

def allocate_iface(self) -> Optional[str]:
    for iface in self.interfaces:
        if iface not in self.used_ifaces:
            self.used_ifaces.add(iface)
            return iface
    return None

def mark_iface(self, iface: str) -> None:
    self.used_ifaces.add(iface)


def to_dict(self) -> dict:
    return {
        "nic_model": self.nic_model,
        "cpu": self.cpu,
        "memory": self.memory,
        "storage": self.storage,
        "positioning": self.positioning,
        "os": "cumulus-vx-5.9.4",
        "features": self.features,
        "pxehost": self.pxehost,
        "secureboot": self.secureboot,
        "oob": self.oob,
        "emulation_type": self.emulation_type,
        "network_pci": self.network_pci,
        "cpu_options": self.cpu_options,
        "storage_pci": self.storage_pci
    }

interfaces = [f"swp{x}" for x in range(1, 17)]


for leaf in leafs:

    leaf_obj = node(leaf, interfaces, positioning={"x": int(leafs.index(leaf)*10), "y": 20})

for spine in spines:

    spine_obj = node(spine, interfaces, positioning={"x": int(leafs.index(leaf)*10), "y": 50})

## Allocate interface on Leaf
iface = leaf.allocate_iface()

## Check if allocated OK
if iface:

    ## Allocate same interface on Spine
    spine.mark_iface(iface)

    ## Build Link Entry for Nvidia
    link = [

        {"interface": iface, "node": leaf.name, "mac": "aa:bb:cc:00:00:01", "network_pci": None},
        {"interface": iface, "node": spine.name, "mac": "aa:bb:cc:00:00:01", "network_pci": None},

    ]

#for i in leafs:
#
#    d = {
#
#        "nic_model": "virtio",
#        "cpu": 1,
#        "memory": 2048,
#        "storage": 10,
#        "positioning": {
#            "x": 10*(1+leafs.index(i)),
#            "y": 40
#        },
#        "os": "cumulus-vx-5.9.4",
#        "features": {
#            "uefi": False,
#            "tpm": False
#        },
#        "pxehost": False,
#        "secureboot": False,
#        "oob": False,
#        "emulation_type": None,
#        "network_pci": {},
#        "cpu_options": [],
#        "storage_pci": {}
#    }
#
#    nodes[i] = d

file_structure["content"]["nodes"] = nodes

with open("new.json","+w") as f:

    f.write(json.dumps(file_structure, indent=2))