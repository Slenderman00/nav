# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 UNINETT AS
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
"""ipdevpoll plugin to collect module information from ENTITY-MIB.

This will collect anything that looks like a field-replaceable module
with a serial number from the entPhysicalTable.  If a module has a
name that can be interpreted as a number, it will have its
module_number field set to this number.

entAliasMappingTable is collected; mappings between any physical
entity and an interface from IF-MIB is kept.  For each mapping found,
the interface will have its module set to be whatever the ancestor
module of the physical entity is.
"""

import logging
import pprint
from datetime import datetime

from twisted.internet import defer, threads
from twisted.python.failure import Failure

from nav.mibs.entity_mib import EntityMib
from nav.ipdevpoll import Plugin, FatalPluginError
from nav.ipdevpoll import storage, shadows
from nav.models import manage

class Modules(Plugin):
    @classmethod
    def can_handle(cls, netbox):
        return True

    def __init__(self, *args, **kwargs):
        super(Modules, self).__init__(*args, **kwargs)
        self.alias_mapping = {}

    @defer.deferredGenerator
    def handle(self):
        self.logger.debug("Collecting ENTITY-MIB module data")
        entitymib = EntityMib(self.job_handler.agent)

        dw = defer.waitForDeferred(entitymib.retrieve_table('entPhysicalTable'))
        yield dw
        physical_table = entitymib.translate_result(dw.getResult())

        dw = defer.waitForDeferred(entitymib.retrieve_column('entAliasMappingIdentifier'))
        yield dw
        alias_mapping = dw.getResult()

        self.alias_mapping = self._process_alias_mapping(alias_mapping)
        self._process_entities(physical_table)


    def _error(self, failure):
        """Errback for SNMP failures."""
        if failure.check(defer.TimeoutError):
            # Transform TimeoutErrors to something else
            self.logger.error(failure.getErrorMessage())
            # Report this failure to the waiting plugin manager (RunHandler)
            exc = FatalPluginError("Cannot continue due to device timeouts")
            failure = Failure(exc)
        self.deferred.errback(failure)


    def _process_entities(self, result):
        """Process the list of collected entities."""
        def device_from_entity(ent):
            device = self.job_handler.container_factory(
                shadows.Device, key=ent['entPhysicalSerialNum'])
            device.serial = ent['entPhysicalSerialNum'].strip()
            if ent['entPhysicalHardwareRev']:
                device.hardware_version = ent['entPhysicalHardwareRev'].strip()
            if ent['entPhysicalSoftwareRev']:
                device.software_version = ent['entPhysicalSoftwareRev'].strip()
            if ent['entPhysicalFirmwareRev']:
                device.firmware_version = ent['entPhysicalFirmwareRev'].strip()
            device.active = True
            return device

        def module_from_entity(ent):
            module = self.job_handler.container_factory(
                shadows.Module, key=ent['entPhysicalSerialNum'])
            module.netbox = netbox
            module.model = ent['entPhysicalModelName'].strip()
            module.description = ent['entPhysicalDescr'].strip()
            module.up = "y"
            module.name = ent['entPhysicalName'].strip()
            if module.name.strip().isdigit():
                module.module_number = int(module.name.strip())
            module.parent = None
            return module

        ###

        # be able to look up all entities using entPhysicalIndex
        entities = EntityTable(result)
        
        # map entity indexes to module containers
        module_containers = {}

        modules = entities.get_modules()
        ports = entities.get_ports()
        netbox = self.job_handler.container_factory(shadows.Netbox, key=None)
        
        for ent in modules:
            entity_index = ent[0]
            device = device_from_entity(ent)
            module = module_from_entity(ent)
            module.device = device

            module_containers[entity_index] = module
            self.logger.debug("module (entPhysIndex=%s): %r", entity_index, module)

        # Map interfaces to modules, if possible
        module_ifindex_map = {} #just for logging debug info
        for port in ports:
            entity_index = port[0]
            if entity_index in self.alias_mapping:
                module_entity = entities.get_nearest_module_parent(port)

                if module_entity and module_entity[0] in module_containers:
                    module = module_containers[ module_entity[0] ]
                    indices = self.alias_mapping[entity_index]
                    for ifindex in indices:
                        interface = self.job_handler.container_factory(
                            shadows.Interface, key=ifindex)
                        interface.netbox = netbox
                        interface.ifindex = ifindex
                        interface.module = module

                        if module.name in module_ifindex_map:
                            module_ifindex_map[module.name].append(ifindex)
                        else:
                            module_ifindex_map[module.name] = [ifindex]

        if module_ifindex_map:
            self.logger.debug("module/ifindex mapping: %r", 
                              module_ifindex_map)

    def _process_alias_mapping(self, alias_mapping):
        mapping = {}
        for (phys_index, logical), row in alias_mapping.items():
            # Last element is ifindex. Preceding elements is an OID.
            ifindex = row.pop()

            if phys_index not in mapping:
                mapping[phys_index] = []
            mapping[phys_index].append(ifindex)

        self.logger.debug("alias mapping: %r", mapping)
        return mapping


class EntityTable(dict):
    """Represent the contents of the entPhysicalTable as a dictionary"""
    def __init__(self, mibresult):
        # want single integers, not oid tuples as keys/indexes
        super(EntityTable, self).__init__()
        for row in mibresult.values():
            index = row[0][0]
            row[0] = index
            self[index] = row

    def is_module(self, e):
        return e['entPhysicalClass'] == 'module' and \
            e['entPhysicalIsFRU'] and \
            e['entPhysicalSerialNum']

    def is_port(self, e):
        return e['entPhysicalClass'] == 'port'

    def get_modules(self):
        """Return the subset of entities that are modules.

        A module is defined as an entity with class=module, being a
        field replaceable unit and having a non-empty serial number.

        Return value is a list of table rows.

        """

        modules = [entity for entity in self.values()
                   if self.is_module(entity)]
        return modules

    def get_ports(self):
        """Return the subset of entities that are physical ports.

        A port is defined as en entity class=port.

        Return value is a list of table rows.

        """
        ports = [entity for entity in self.values()
                 if self.is_port(entity)]
        return ports

    def get_nearest_module_parent(self, entity):
        """Traverse the entity hierarchy to find a suitable parent module.

        Returns a module row if a parent is found, else None is returned.

        """
        parent_index = entity['entPhysicalContainedIn']
        if parent_index in self:
            parent = self[parent_index]
            if self.is_module(parent):
                return parent
            else:
                return self.get_nearest_module_parent(parent)

