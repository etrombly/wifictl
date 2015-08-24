#!/usr/bin/env python

import subprocess
import os

class Interface():
    def __init__(self, name, IEEEtype = None, essid = None):
        self.name = name
        self.IEEEtype = IEEEtype
        self.state = None
        self.checkState()
        if essid == "off/any":
            self.essid = None
        else:
            self.essid = essid

    def __repr__(self):
        return self.name

    def checkState(self):
        out = subprocess.check_output(["ip", "link", "show", self.name])
        out = out.decode('utf-8')
        if "DOWN" in out:
            self.state = False
        else:
            self.state = True

    def setUp(self):
        subprocess.call(["ip", "link", "set", self.name, "up"])

    def scan(self):
        try:
            out = subprocess.check_output(["iwlist", self.name, "scanning"])
            out = out.decode('utf-8')
            for cell in out.split("          Cell ")[1:]:
                for line in cell.split("\n"):
                    if "ESSID" in line:
                        essid = line.split(":")[1].strip('"')
                print(essid)
        except subprocess.CalledProcessError:
            print("could not scan", self.name)

    def findCFG(self):
        networkFile = "/etc/systemd/network/%s.network" % self.name
        wpaFile = "/etc/wpa_supplicant/wpa_supplicant-%s.conf" % self.name
        if not os.path.exists(networkFile):
            print("network config for %s does not exist, creating" % (self.name))
        if not os.path.exists(wpaFile):
            print("wpa_supplicant config for %s does not exist" % (self.name))

    def createNetworkCFG(self):
        with open("/etc/systemd/network/%s.network" % self.name, "r+") as networkFile:
            pass

    def createWPACFG(self):
        with open("/etc/wpa_supplicant/wpa_supplicant-%s.conf" % self.name, "r+") as wpaFile:
            pass

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

if __name__ == "__main__":
    interfaces = []
    findIF(interfaces)
    for interface in interfaces:
        print("found interface", interface)
        #interface.findCFG()
        if not interface.state:
            interface.setUp()
        interface.scan()
