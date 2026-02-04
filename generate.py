
import json
from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict
from netaddr import *
import random
mac = ':'.join(['{:02x}'.format(0) for _ in range(6)])

file_structure = {

    "format": "JSON",
    "title": "interpod_new",
#    "ztp": "#!/bin/bash\n# Created by Topology-Converter v4.7.1\n#    Template Revision: v4.7.1\n\nfunction error() {\n  echo -e \"e[0;33mERROR: The Zero Touch Provisioning script failed while running the command $BASH_COMMAND at line $BASH_LINENO.e[0m\" >&2\n}\ntrap error ERR\n\nSSH_URL=\"http://192.168.200.1/authorized_keys\"\n# Uncomment to setup SSH key authentication for Ansible\n# mkdir -p /home/cumulus/.ssh\n# wget -q -O /home/cumulus/.ssh/authorized_keys $SSH_URL\n\n# Uncomment to unexpire and change the default cumulus user password\npasswd -x 99999 cumulus\necho 'cumulus:Lab123' | chpasswd\n\n# Uncomment to make user cumulus passwordless sudo\necho \"cumulus ALL=(ALL) NOPASSWD:ALL\" > /etc/sudoers.d/10_cumulus\n\n# Uncomment to enable all debian sources & netq apps3 repo\nsed -i 's/#deb/deb/g' /etc/apt/sources.list\nwget -q -O pubkey https://apps3.cumulusnetworks.com/setup/cumulus-apps-deb.pubkey\napt-key add pubkey\nrm pubkey\n\n# Uncomment to allow NTP to make large steps at service restart\necho \"tinker panic 0\" >> /etc/ntp.conf\nsystemctl enable ntp@mgmt\n\nexit 0\n#CUMULUS-AUTOPROVISIONING\n#CUMULUS-AUTOPROVISIONING",
    "content": {
        "nodes": {},
        "links": [],
        "oob": False,
        "netq": False

    },

}


nodes = {}

leaf_count = 200
spine_count = 200

leafs = [f"leaf{x}" for x in range(1,leaf_count)]
spines = [f"spine{x}" for x in range(1,spine_count)]

interfaces = 16

iface_index = 0
used_endpoints = set()
links = []
mac_counter = 1
interfaces = [f"swp{x}" for x in range(1, 500)]

leaf_objects = []
spine_objects = []

@dataclass
class Link:
    interface_a: str
    node_a: str
    interface_b: str
    node_b: str
    mac_a: str = field(default_factory=lambda: ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)]))
    mac_b: str = field(default_factory=lambda: ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)]))
    network_pci_a: None = None
    network_pci_b: None = None
    interface_role_b: None = None
    scalable_unit: None = None

    def mac_generate(self, prefix) -> str:

        mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
        return mac

    def to_list_dict(self) -> list:
        return [
            {
                "interface": self.interface_a,
                "node": self.node_a,
#                "mac": self.mac_a,
                "network_pci": self.network_pci_a,
                "interface_role": self.interface_role_b,
                "scalable_unit": self.scalable_unit

            },
            {
                "interface": self.interface_b,
                "node": self.node_b,
#                "mac": self.mac_b,
                "network_pci": self.network_pci_b
            }
        ]

@dataclass
class Node:
    name: str
    interfaces: List[str]
    nic_model: str = "virtio"
    cpu: int = 1
    memory: int = 1024
    storage: int = 10
    positioning: Dict = field(default_factory=dict)
    features: Dict = field(default_factory=lambda: {"uefi": False, "tpm": False})
    pxehost: bool = False
    secureboot: bool = False
    oob: bool = False
    emulation_type: None = None
    network_pci: Dict = field(default_factory=dict)
    cpu_options: List = field(default_factory=list)
    storage_pci: Dict = field(default_factory=dict)
    used_ifaces: List[str] = field(default_factory=list)
    config_ifaces: List = field(default_factory=list)

    def allocate_iface(self, *args) -> Optional[str]:
        if len(args)>0:
            if args[0] and args[0] not in self.used_ifaces and args[0] in self.interfaces:
                self.used_ifaces.append(args[0])
                return args[0]
        else:
            for x in self.interfaces:
                if x not in self.used_ifaces:
                    self.used_ifaces.append(x)
                    return x
        return None

    def mark_iface(self, iface: str) -> None:
        if iface not in self.used_ifaces:
            self.used_ifaces.append(iface)


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





for leaf in leafs:

    leaf_obj = Node(leaf, interfaces, positioning={"x": int((leafs.index(leaf)+1)*200), "y": 20})

    nodes[leaf] = leaf_obj


for spine in spines:

    spine_obj = Node(spine, interfaces, positioning={"x": int((spines.index(spine)+1)*200), "y": 200})

    nodes[spine] = spine_obj

node_links = {(spine, leaf) for spine in spines for leaf in leafs}

for spine, leaf in node_links:

    # Allocate interface on leaf
    leaf_iface = nodes[leaf].allocate_iface()

    # If the leaf has no free interfaces, skip or raise
    if leaf_iface is None:
        raise RuntimeError(f"No free interface available for node {leaf}")

    # Allocate independent interface on the corresponding spine node
    spine_iface = nodes[spine].allocate_iface()

    if spine_iface is None:
        raise RuntimeError(f"No free interface available for node {spine}")

    link_obj = Link(leaf_iface, leaf, spine_iface, spine)

    links.append(link_obj)




file_structure["content"]["nodes"] = {name: node.to_dict() for name, node in nodes.items()}


#print(links[0].to_list_dict())

file_structure["content"]["links"] = [x.to_list_dict() for x in links]

#print(nodes.items())

with open("new.json","+w") as f:

    f.write(json.dumps(file_structure, indent=2))