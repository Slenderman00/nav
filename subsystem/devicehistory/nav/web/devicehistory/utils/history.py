# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

import time
from datetime import date
from django.db.models import Q

from nav.models.manage import Room, Location, Netbox, Module
from nav.models.event import AlertHistory, AlertHistoryVariable, AlertHistoryMessage, AlertType

GROUP_BY_LOCATION = 'group_by_locations'
GROUP_BY_ROOM = 'group_by_room'
GROUP_BY_NETBOX_AND_MODULE = 'group_by_netbox_and_module'
GROUP_BY_NETBOX = 'group_by_netbox'
GROUP_BY_MODULE = 'group_by_module'
GROUP_BY_DEVICE = 'group_by_device'

def get_history(**kwargs):
    location_ids = kwargs.pop('locations', [])
    room_ids = kwargs.pop('rooms', [])
    netbox_ids = kwargs.pop('netboxes', [])
    module_ids = kwargs.pop('modules', [])
    device_ids = kwargs.pop('devices', [])

    start_time = kwargs.pop('start_time', date.fromtimestamp(time.time() - 7 * 24 * 60 * 60))
    end_time = kwargs.pop('end_time', date.today())
    types = kwargs.pop('types', None)
    group_by = kwargs.pop('group_by', GROUP_BY_NETBOX_AND_MODULE)

    for key in kwargs.keys():
        raise TypeError('__init__() got an unexpected keyword argument %s' % key)

    time_limit = [
        Q(start_time__lte=self.end_time) &
        (
            Q(end_time__gte=self.start_time) |
            (
                Q(end_time__isnull=True) &
                Q(start_time__gte=self.start_time)
            )
        )
    ]
    
    def location_history():
        pass

    def room_history():
        pass

    def netbox_history():
        pass

    def module_history():
        pass

    def device_history():
        pass


class History:
    locations = []
    rooms = []
    netboxes = []
    modules = []

    start_time = []
    end_time = []
    types = []

    def __init__(self, **kwargs):
        selection = kwargs.pop('selection', [])
        self.start_time = kwargs.pop('start_time', date.fromtimestamp(time.time() - 7 * 24 * 60 * 60))
        self.end_time = kwargs.pop('end_time', date.today())
        self.types = kwargs.pop('types', None)

        for key in kwargs.keys():
            raise TypeError('__init__() got an unexpected keyword argument %s' % key)

        self.locations = selection.get('location', [])
        self.rooms = selection.get('room', [])
        self.netboxes = selection.get('netbox', [])
        self.modules = selection.get('module', [])

        self.time_limit = [
            Q(start_time__lte=self.end_time) &
            (
                Q(end_time__gte=self.start_time) |
                (
                    Q(end_time__isnull=True) &
                    Q(start_time__gte=self.start_time)
                )
            )
        ]

    def get_location_history(self):
        alert_history = AlertHistory.objects.select_related(
            'event_type', 'alert_type', 'device'
        ).filter(
            Q(device__netbox__room__location__id__in=self.locations),
            *self.time_limit
        ).extra(
            select={
                'location_id': 'location.locationid',
                'location_name': 'location.descr',
            },
            tables=['location'],
            where=['location.locationid=room.locationid']
        ).order_by('location_name', '-start_time', '-end_time')

        if self.types['event']:
            alert_history = alert_history.filter(event_type__in=self.types['event'])
        if self.types['alert']:
            alert_history = alert_history.filter(alert_type__in=self.types['alert'])

        msgs = AlertHistoryMessage.objects.filter(
            alert_history__in=alert_history,
            language='en',
            type='sms',
        )

        history = {}
        for a in alert_history:
            a.extra_messages = []
            for m in msgs:
                if m.alert_history_id == a.id:
                    a.extra_messages.append(m)
            if a.location_id not in history:
                history[a.location_id] = {
                    'description': a.location_name,
                    'alerts': []
                }
            history[a.location_id]['alerts'].append(a)
        return history

    def get_room_history(self):
        alert_history = AlertHistory.objects.select_related(
            'event_type', 'alert_type', 'device'
        ).filter(
            Q(device__netbox__room__id__in=self.rooms),
            *self.time_limit
        ).extra(
            select={
                'room_id': 'room.roomid',
                'room_descr': 'room.descr',
           },
           tables=['room'],
           where=['room.roomid=netbox.roomid']
        ).order_by('alerthistoryvariable__value', '-start_time', '-end_time')

        if self.types['event']:
            alert_history = alert_history.filter(event_type__in=self.types['event'])
        if self.types['alert']:
            alert_history = alert_history.filter(alert_type__in=self.types['alert'])

        msgs = AlertHistoryMessage.objects.filter(
            alert_history__in=alert_history,
            language='en',
            type='sms',
        )

        history = {}
        for a in alert_history:
            a.extra_messages = []
            for m in msgs:
                if m.alert_history_id == a.id:
                    a.extra_messages.append(m)
            if a.room_id not in history:
                if not isinstance(a.room_id, unicode):
                    a.room_id = unicode(a.room_id)
                if not isinstance(a.room_descr, unicode):
                    a.room_descr = unicode(a.room_descr)
                history[a.room_id] = {
                    'description': a.room_id + ' (' + a.room_descr + ')',
                    'alerts': []
                }

            history[a.room_id]['alerts'].append(a)

        return history

    def get_netbox_history(self):
        alert_history = AlertHistory.objects.select_related(
            'event_type', 'alert_type', 'device'
        ).filter(
            Q(device__netbox__id__in=self.netboxes),
            *self.time_limit
        ).extra(
            select={
                'netbox_id': 'netbox.netboxid',
                'netbox_name': 'netbox.sysname',
            },
            tables=['netbox'],
            where=['netbox.deviceid=device.deviceid']
        ).order_by('-start_time')

        if self.types['event']:
            alert_history = alert_history.filter(event_type__in=self.types['event'])
        if self.types['alert']:
            alert_history = alert_history.filter(alert_type__in=self.types['alert'])

        msgs = AlertHistoryMessage.objects.filter(
            alert_history__in=alert_history,
            language='en',
            type='sms',
        )

        history = {}
        for a in alert_history:
            a.extra_messages = []
            for m in msgs:
                if m.alert_history_id == a.id:
                    a.extra_messages.append(m)
            if a.netbox_id not in history:
                history[a.netbox_id] = {
                    'description': a.netbox_name,
                    'alerts': []
                }
            history[a.netbox_id]['alerts'].append(a)
        return history

    def get_module_history(self):
        alert_history = AlertHistory.objects.select_related(
            'event_type', 'alert_type', 'device'
        ).filter(
            Q(device__module__id__in=self.modules),
            *self.time_limit
        ).extra(
            select={
                'module': 'module.module',
                'netbox_name': 'netbox.sysname',
            },
            tables=['module', 'netbox'],
            where=['module.deviceid=device.deviceid', 'netbox.netboxid=module.netboxid']
        ).order_by('-start_time')

        if self.types['event']:
            alert_history = alert_history.filter(event_type__in=self.types['event'])
        if self.types['alert']:
            alert_history = alert_history.filter(alert_type__in=self.types['alert'])

        msgs = AlertHistoryMessage.objects.filter(
            alert_history__in=alert_history,
            language='en',
            type='sms',
        )

        history = {}
        for a in alert_history:
            a.extra_messages = []
            for m in msgs:
                if m.alert_history_id == a.id:
                    a.extra_messages.append(m)
            if a.module not in history:
                history[a.module] = {
                    'description': u'Module %i in %s' %  (a.module, a.netbox_name),
                    'alerts': []
                }
            history[a.module]['alerts'].append(a)
        return history

    def get_device_history(self):
        netboxes = Netbox.objects.select_related(
            'device'
        ).filter(id__in=self.netboxes)
        modules = Module.objects.select_related(
            'device'
        ).filter(id__in=self.modules)

        devices = []
        for box in netboxes,modules:
            for d in box:
                if d.device.serial and d.device not in devices:
                    devices.append(d.device)

        alert_history = AlertHistory.objects.select_related(
            'event_type', 'alert_type', 'device'
        ).filter(
            Q(device__in=devices),
            *self.time_limit
        ).order_by('-start_time')

        if self.types['event']:
            alert_history = alert_history.filter(event_type__in=self.types['event'])
        if self.types['alert']:
            alert_history = alert_history.filter(alert_type__in=self.types['alert'])

        msgs = AlertHistoryMessage.objects.filter(
            alert_history__in=alert_history,
            language='en',
            type='sms',
        )

        history = {}
        for a in alert_history:
            a.extra_messages = []
            for m in msgs:
                if m.alert_history_id == a.id:
                    a.extra_messages.append(m)
            if a.device.serial not in history:
                history[a.device.serial] = {
                    'description': a.device.serial,
                    'alerts': [],
                }
            history[a.device.serial]['alerts'].append(a)
        return history
