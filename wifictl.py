#!/usr/bin/env python

import subprocess
import os

class Interface():
    def __init__(self, name, IEEEtype = None, essid = None):
        self.name = name
        self.IEEEtype = IEEEtype
        if essid == "off/any":
            self.essid = None
        else:
            self.essid = essid
    
    def __repr__(self):
        return self.name

class AP():
    def __init__(self, name):
        self.name = name

def findIF(interfaces):
    out = subprocess.check_output(["iwconfig"], stderr = open("/dev/null"))
    out = out.decode('utf-8')
    inters = out.split('\n\n')
    for inter in inters:
        if inter:
            for line in inter.split("\n"):
                if not line.startswith(" "):
                    split = line.split()
                    if split:
                        name = split[0]
                        IEEEtype = split[2]
                        essid = " ".join(split[3:]).replace("ESSID:", "").strip('"')
                        interfaces.append(Interface(name, IEEEtype, essid))

def findCFG(interface):
    networkFile = "/etc/systemd/network/%s.network" % interface
    wpaFile = "/etc/wpa_supplicant/wpa_supplicant-%s.conf" % interface
    if not os.path.exists(networkFile):
        print("network config for %s does not exist, creating" % (interface))
    if not os.path.exists(wpaFile):
        print("wpa_supplicant config for %s does not exist" % (interface))

def createNetworkCFG(interface):
    with open("/etc/systemd/network/%s.network" % interface, "r+") as networkFile:
        pass

def createWPACFG(interface):
    with open("/etc/wpa_supplicant/wpa_supplicant-%s.conf" % interface, "r+") as wpaFile:
        pass

def scan(interface):
    out = subprocess.check_output(["iwlist", interface.name, "scanning"])
    print(out)

if __name__ == "__main__":
    interfaces = []
    findIF(interfaces)
    for interface in interfaces:
        print("found interface", interface)
        findCFG(interface)
        scan(interface)