#!/usr/bin/env python
#grabbed db2dbm and quality regexs from https://github.com/rockymeza/wifi

import subprocess
import configparser
import os
import re

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
        self.networkConfig = configparser.ConfigParser()
        self.networkConfig.optionxform=str
        self.networks = []
        self.qualityPatterns = {'dBm': re.compile(r'Quality=(\d+/\d+).*Signal level=(-\d+) dBm'),
                   'relative': re.compile(r'Quality=(\d+/\d+).*Signal level=(\d+/\d+)'),
                   'absolute': re.compile(r'Quality:(\d+).*Signal level:(\d+)')}

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
                aps.append(AP(*self.parseCell(cell)))
        except subprocess.CalledProcessError:
            print("could not scan", self.name)
        return aps
    
    def parseCell(self, cell):
        
        for line in cell.splitlines():
            if "ESSID" in line:
                essid = line.split(":")[1].strip('"')
            elif "Protocol" in line:
                protocol = line.split(":")[1].replace("IEEE ", "")
            elif "Quality" in line:
                for re_name, quality_re in self.qualityPatterns.items():
                    match_result = quality_re.search(line)
                    if match_result is not None:
                        quality, signal = match_result.groups()
                        if re_name == 'relative':
                            actual, total = map(int, signal.split('/'))
                            signal = self.db2dbm(int((actual / total) * 100))
                        elif re_name == 'absolute':
                            quality = quality + '/100'
                            signal = self.db2dbm(int(signal))
                        else:
                            signal = int(signal)
                        break
        return essid, protocol, quality, signal
                            
    def loadCFG(self):
        networkFile = "/etc/systemd/network/%s.network" % self.name
        wpaFile = "/etc/wpa_supplicant/wpa_supplicant-%s.conf" % self.name
        try:
            self.networkConfig.readfp(open(networkFile))
        except FileNotFoundError:
            print("network config for %s does not exist, creating" % (self.name))
            self.writeNetworkCFG()
        try:
            with open(wpaFile) as wpaConfig:
                networks = wpaConfig.read().split("network={\n")[1:]
            self.networks = []
            for network in networks:
                self.networks.append(Network(*self.parseNetwork(network)))
        except IOError:
            print("wpa_supplicant config for %s does not exist" % (self.name))

    def parseNetwork(self, network):
        for line in network.splitlines():
            line = line.lstrip()
            if not line.startswith("#") and not line == "}":
                if line.startswith("ssid="):
                    ssid = line.split("ssid=")[1].strip('"')
                if line.startswith("psk="):
                    psk = line.split("psk=")[1].strip('"')
        return ssid, psk

    def writeNetworkCFG(self):
        #test for now
        self.networkConfig.add_section("Match")
        self.networkConfig.set("Match", "Name", self.name)
        self.networkConfig.add_section("Network")
        self.networkConfig.set("Network", "DHCP", "ipv4")
        self.networkConfig.write(open("/etc/systemd/network/%s.network" % self.name, 'w+'), space_around_delimiters=False)

    def writeWPACFG(self):
        with open("/etc/wpa_supplicant/wpa_supplicant-%s.conf" % self.name, 'w+') as wpaFile:
            pass

    def findIF(self = None):
        command = ["iwconfig"]
        if self:
            command.append(self.name)
        out = subprocess.check_output(command, stderr = subprocess.DEVNULL)
        out = out.decode('utf-8')
        result = []
        interfaces = out.split('\n\n')
        interfaces = [x for x in interfaces if x]
        for interface in interfaces:
            for line in interface.splitlines():
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
    
    def db2dbm(self, quality):
        """
        Converts the Radio (Received) Signal Strength Indicator (in db) to a dBm
        value.  Please see http://stackoverflow.com/a/15798024/1013960
        """
        dbm = int((quality / 2) - 100)
        return min(max(dbm, -100), -50)

class AP():
    def __init__(self, name, protocol, quality, signal):
        self.name = name
        self.protocol = protocol
        self.quality = quality
        self.signal = signal

    def __repr__(self):
        return "ESSID: %s PROTO: %s SIG: %i dBm" % (self.name, self.protocol, self.signal)

class Network():
    def __init__(self, ssid, psk):
        self.ssid = ssid
        self.psk = psk
    
    def __repr__(self):
        return "ssid: %s" % (self.ssid)

if __name__ == "__main__":
    interfaces = Interface.findIF()
    for interface in interfaces:
        print("found interface %s, connected to %s" % (interface, interface.essid))
        interface.loadCFG()
        print("wpa_supplicant configured networks")
        for network in interface.networks:
            print("\t", network)
        #if not interface.state:
        #    interface.setUp()
        aps = interface.scan()
        print("scanned access points")
        for ap in aps:
            print("\t", ap)
