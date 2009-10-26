# -*- coding: utf-8 -*-
#
# Copyright (C) 2008, 2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""ipdevpoll plugin to poll IP prefix information.

This plugin will use the IF-MIB, IP-MIB, IPv6-MIB and
CISCO-IETF-IP-MIB to poll prefix information for both IPv4 and IPv6.

A revised version of the IP-MIB contains the IP-version-agnostic
ipAddressTable which is queried first, although not much equipment
supports this table yet.  It then falls back to the original IPv4-only
ipAddrTable, followed by the IPv6-MIB (which has been superseded by
the updated IP-MIB).  It also tries a Cisco proprietary
CISCO-IETF-IP-MIB, which is based on a draft that later became the
revised IP-MIB.

An interface with an IP address whose name matches the VLAN_PATTERN
will cause the corresponding prefix to be associated with the VLAN id
parsed from the interface name.  Not all dot1q enabled routers name
their interfaces like this, but routing switches from several vendors
do.

TODO: Guesstimate an appropriate nettype for each VLAN
TODO: Parse router port descriptions according to conventions

"""
import re

from twisted.internet import defer
from twisted.python.failure import Failure

from IPy import IP

from nav.mibs import reduce_index
from nav.mibs.if_mib import IfMib
from nav.mibs.ip_mib import IpMib, IndexToIpException
from nav.mibs.ipv6_mib import Ipv6Mib
from nav.mibs.cisco_ietf_ip_mib import CiscoIetfIpMib

from nav.ipdevpoll import Plugin, FatalPluginError
from nav.ipdevpoll import storage, shadows

VLAN_PATTERN = re.compile("Vl(an)?(?P<vlan>\d+)", re.IGNORECASE)

class Prefix(Plugin):
    """
    ipdevpoll-plugin for collecting prefix information from monitored
    equipment.
    """
    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.deferred = defer.Deferred()

    @classmethod
    def can_handle(cls, netbox):
        """
        This plugin handles netboxes
        """
        return True

    @defer.deferredGenerator
    def handle(self):


        self.logger.debug("Collecting prefixes")
        netbox = self.job_handler.container_factory(shadows.Netbox, key=None)

        ipmib = IpMib(self.job_handler.agent)
        ciscoip = CiscoIetfIpMib(self.job_handler.agent)

        # Retrieve interface names and keep those who match a VLAN
        # naming pattern
        dw = defer.waitForDeferred(self.get_vlan_interfaces())
        yield dw
        vlan_interfaces = dw.getResult()

        # Traverse ipAddressTable and cIpAddressTable as more or less
        # identical tables, but skip the Cisco MIB if the first gives
        # results.
        for mib, ifindex_col, prefix_col in (
            (ipmib, 'ipAddressIfIndex', 'ipAddressPrefix'),
            (ciscoip, 'cIpAddressIfIndex', 'cIpAddressPrefix'),
            ):
            self.logger.debug("Trying address table from %s",
                              mib.mib['moduleName'])
            df = mib.retrieve_columns((ifindex_col, prefix_col))
            dw = defer.waitForDeferred(df)
            yield dw

            addresses = dw.getResult()

            for index, row in addresses.items():
                ip = ipmib.address_index_to_ip(index)
                if not ip:
                    continue

                prefix = ipmib.prefix_index_to_ip(row[prefix_col])
                ifindex = row[ifindex_col]

                self.create_containers(netbox, ifindex, prefix, ip,
                                       vlan_interfaces)

        self.logger.debug("Trying original ipAddrTable")
        df = ipmib.retrieve_columns(('ipAdEntIfIndex',
                                     'ipAdEntAddr',
                                     'ipAdEntNetMask'))
        dw = defer.waitForDeferred(df)
        yield dw

        result = dw.getResult()

        for row in result.values():
            ip = IP(row['ipAdEntAddr'])
            ifindex = row['ipAdEntIfIndex']
            net_prefix = ip.make_net(row['ipAdEntNetMask'])

            self.create_containers(netbox, ifindex, net_prefix, ip,
                                   vlan_interfaces)


    def create_containers(self, netbox, ifindex, net_prefix, ip,
                          vlan_interfaces):
        """
        Utitilty method for creating the shadow-objects
        """
        interface = self.job_handler.container_factory(shadows.Interface, key=ifindex)
        interface.ifindex = ifindex
        interface.netbox = netbox

        # No use in adding the GwPortPrefix unless we actually found a prefix
        if net_prefix:
            port_prefix = self.job_handler.container_factory(
                shadows.GwPortPrefix, key=ip)
            port_prefix.interface = interface
            port_prefix.gw_ip = str(ip)

            prefix = self.job_handler.container_factory(shadows.Prefix,
                                                        key=net_prefix)
            prefix.net_address = str(net_prefix)
            port_prefix.prefix = prefix

            # Always associate prefix with a VLAN record, but set a
            # VLAN number if we can.
            # TODO: Some of this logic should actually be in a storage class, not in this plugin.
            vlan = self.job_handler.container_factory(shadows.Vlan,
                                                      key=net_prefix)
            if ifindex in vlan_interfaces:
                vlan.vlan = vlan_interfaces[ifindex]

            if not vlan.net_type:
                vlan.net_type = self.guesstimate_net_type(net_prefix)
                self.logger.debug("VLAN %s TYPE IS: %r", vlan.vlan, vlan.net_type)

            prefix.vlan = vlan

    @defer.deferredGenerator
    def get_vlan_interfaces(self):
        """Get all virtual VLAN interfaces.

        Any interface whose ifName matches the VLAN_PATTERN regexp
        will be included in the result.

        Return value:

          A deferred whose result is a dictionary: { ifindex: vlan }

        """
        ifmib = IfMib(self.job_handler.agent)
        dw = defer.waitForDeferred(ifmib.retrieve_column('ifName'))
        yield dw
        interfaces = reduce_index(dw.getResult())

        vlan_ifs = {}
        for ifindex, ifname in interfaces.items():
            match = VLAN_PATTERN.match(ifname)
            if match:
                vlan = int(match.group('vlan'))
                vlan_ifs[ifindex] = vlan

        yield vlan_ifs

    def get_net_type(self, net_type_id):
        """Return a storage container for the given net_type id."""
        net_type = self.job_handler.container_factory(
            shadows.NetType, key=net_type_id)
        net_type.id = net_type_id
        return net_type

    def guesstimate_net_type(self, prefix):
        """Guesstimate a net type for the given prefix.

        Various algorithms may be used (and the database may be
        queried).

        Arguments:

         prefix -- An IPy.IP object representing the prefix.

        Returns:

          A NetType storage container, suitable for assigment to
          Vlan.net_type.

        """
        net_type = 'unknown'
        if prefix.version() == 6 and prefix.prefixlen() == 128:
            net_type = 'loopback'
        elif prefix.version() == 4:
            if prefix.prefixlen() == 32:
                net_type = 'loopback'
            elif prefix.prefixlen() == 30:
                net_type = 'link'

        return self.get_net_type(net_type)

    def error(self, failure):
        """
        Return a failure to the ipdevpoll-deamon
        """
        if failure.check(defer.TimeoutError):
            # Transform TimeoutErrors to something else
            self.logger.error(failure.getErrorMessage())
            # Report this failure to the waiting plugin manager (RunHandler)
            exc = FatalPluginError("Cannot continue due to device timeouts")
            failure = Failure(exc)
        self.deferred.errback(failure)
