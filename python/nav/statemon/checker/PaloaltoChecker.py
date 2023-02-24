from nav.statemon.event import Event
from nav.statemon.abstractchecker import AbstractChecker
import requests

import xml.etree.ElementTree as ET
from nav.models.manage import Arp, Netbox

from datetime import datetime

# removes urllib error
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Ingest Palo Alto ARP data into NAV
"""


class PaloAlto:
    def __init__(self, ip, apikey):
        self.ip = ip
        self.apikey = apikey
        self.url = "https://{}/api/?type=op&cmd=<show><arp><entry+name+=+'all'/></arp></show>&key={}".format(
            self.ip, self.apikey
        )
        self.arp = self.get_arp()
        self.netbox = self.get_netbox()
        self.arps = self.parse_arp()
        print("Found {} ARP entries".format(len(self.arps)))

    def get_arp(self):
        """Get arp table from Palo Alto"""

        print("Fetching ARP table from {}".format(self.ip))
        arp = requests.get(self.url, verify=False)
        return arp.text

    def get_netbox(self):
        """Fetches the correct netbox"""
        netbox = Netbox.objects.get(ip=self.ip)
        return netbox

    def parse_arp(self):
        """Create mappings from arp table"""
        """XML PARSER IS SHIT AND FULL OF SECURITY VULNERABILITIES"""

        arps = []

        root = ET.fromstring(self.arp)

        entries = root[0][4]
        for entry in entries:
            status = entry[0].text
            ip = entry[1].text
            mac = entry[2].text
            ttl = entry[3].text
            interface = entry[4].text
            if status != " i ":
                if mac != "(incomplete)":
                    arps.append((ip, mac, interface, status, ttl))

        return arps

    def append(self):
        """Append arp to database"""

        for arp in self.arps:
            self.process(arp)

    def process(self, arp):
        """Processes arp table"""

        timemax = datetime.max
        timestamp = datetime.now()

        # if multiple entries (more than 1) has the same ip, mac, sysname and end_time = timemax then delete all except the newest
        record = Arp.objects.filter(
            ip=arp[0], mac=arp[1], sysname=self.netbox.sysname, end_time=timemax
        )
        if len(record) > 1:
            record = record.order_by('-start_time')
            for i in range(1, len(record)):
                record[i].delete()

        # if ip is different but mac is the same, then keep the record and mark it as inactive if it is not already marked as inactive
        record = Arp.objects.filter(mac=arp[1], sysname=self.netbox.sysname).exclude(
            ip=arp[0]
        )
        if len(record) > 0:
            if record[0].end_time == timemax:
                record.update(end_time=timestamp)
                print("Marked {} as inactive".format(record[0].ip))
                return True

        # if ip is the same and mac is the same then create a new record unless one allready exists
        record = Arp.objects.filter(
            ip=arp[0], mac=arp[1], sysname=self.netbox.sysname, end_time=timemax
        )
        if len(record) == 0:
            obj, created = Arp.objects.get_or_create(
                netbox=self.netbox,
                sysname=self.netbox.sysname,
                ip=arp[0],
                mac=arp[1],
                start_time=timestamp,
                end_time=timemax,
            )

            # if created
            if created:
                print("Created new record for {}".format(arp[0]))
                return True
        else:
            # print("Record for {} already exists".format(arp[0]))
            return True

        # if entry is not marked as inactive and not in the arp table then mark it as inactive
        record = Arp.objects.filter(
            ip=arp[0], mac=arp[1], sysname=self.netbox.sysname, end_time=timemax
        )
        if len(record) > 0:
            record.update(end_time=timestamp)
            print("Marked {} as inactive".format(arp[0]))
            return True


class PaloaltoChecker(AbstractChecker):
    IPV6_SUPPORT = True
    DESCRIPTION = 'Fetches arp tables from Paloalto network equipment'
    ARGS = (('key', 'The api key used to interface with the equipment'),)

    def execute(self):
        """Runs checker"""
        key = self.args.get('key', '')
        ip, port = self.get_address()

        instance = PaloAlto(ip, key)
        instance.append()

        processed = len(instance.arps)

        return Event.UP, f'Processed {processed} records'
