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
        aps = []
        try:
            out = subprocess.check_output(["iwlist", self.name, "scan"])
            out = out.decode('utf-8')
            for cell in out.split("          Cell ")[1:]:
                for line in cell.split("\n"):
                    if "ESSID" in line:
                        essid = line.split(":")[1].strip('"')
                aps.append(AP(essid))
        except subprocess.CalledProcessError:
            print("could not scan", self.name)
        return aps

    def loadCFG(self):
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

    def __repr__(self):
        return self.name

def findIF():
    out = subprocess.check_output(["iwconfig"], stderr = open("/dev/null"))
    out = out.decode('utf-8')
    result = []
    interfaces = out.split('\n\n')
    interfaces = [x for x in interfaces if x]
    for interface in interfaces:
        for line in interface.split("\n"):
            if not line.startswith(" "):
                name = line.split()[0]
                try:
                    IEEEtype = line.split("IEEE ")[1].split()[0]
                except IndexError:
                    IEEEtype = None
                try:
                    essid = line.split('ESSID:"')[1].split('"')[0]
                except IndexError:
                    essid = None
                result.append(Interface(name, IEEEtype, essid))
    return result

if __name__ == "__main__":
    interfaces = findIF()
    for interface in interfaces:
        print("found interface", interface)
        #interface.loadCFG()
        if not interface.state:
            interface.setUp()
        aps = interface.scan()
        print(aps)
