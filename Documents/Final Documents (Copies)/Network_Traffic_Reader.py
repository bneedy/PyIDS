from scapy.all import *

class Network_Traffic_Reader(object):
    """A class to read network traffic 
        and package it for the PyIDS"""

    def __init__(self):
        self.showData = ""
        self.nextPacketData = []
        self.flagsDict = {
            'F': 'FIN',
            'S': 'SYN',
            'R': 'RST',
            'P': 'PSH',
            'A': 'ACK',
            'U': 'URG',
            'E': 'ECE',
            'C': 'CWR',
        }

    def getNextPacket(self):
        self.nextPacketData = []
        while not self.nextPacketData:
            self.recvNextPacket()
        return self.nextPacketData

    def getSinglePacket(self):
        while self.showData == "":
            self.recvNextPacket()
        return self.showData

    def recvNextPacket(self):
        packets = sniff(count=1, prn=self.parseData)
        self.currentPacket = packets

    def parseData(self, pkt):
        data = ""

        ip_src = ""
        ip_dst = ""
        src_port = ""
        dst_port = ""
        type = ""
        flags = "SF"
        land = "0"

        if IP in pkt:
            ip_src=pkt[IP].src
            ip_dst=pkt[IP].dst

        if TCP in pkt:
            src_port=pkt[TCP].sport
            dst_port=pkt[TCP].dport
            flags=str(pkt.sprintf('%TCP.flags%'))
            type = "TCP"

        elif UDP in pkt:
            src_port=pkt[UDP].sport
            dst_port=pkt[UDP].dport
            type = "UDP"
        
        if type == "TCP" or type == "UDP":
            data += "Type: " + str(type) + "\n"
            data += "Flags: " + str(flags) + "\n"
            data += "IP SRC: " + str(ip_src) + "\nIP DST: " + str(ip_dst) + "\n"
            data += "SRC PORT: " + str(src_port) + "\nDST PORT: " + str(dst_port) + "\n"
            if ip_src == ip_dst and src_port == dst_port:
                land = "1"
            data += "LAND: " + land + "\n"

        self.showData = data

        if type != "":
            self.nextPacketData.append(str(type).lower())
            self.nextPacketData.append(str(flags))
            self.nextPacketData.append(str(land))
        else:
            self.nextPacketData = []