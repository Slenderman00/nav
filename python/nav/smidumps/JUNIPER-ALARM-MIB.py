# python version 1.0						DO NOT EDIT
#
# Generated by smidump version 0.4.8:
#
#   smidump -f python JUNIPER-ALARM-MIB

FILENAME = "./JUNIPER-ALARM-MIB.mib"

MIB = {
    "moduleName" : "JUNIPER-ALARM-MIB",

    "JUNIPER-ALARM-MIB" : {
        "nodetype" : "module",
        "language" : "SMIv2",
        "organization" :    
            """Juniper Networks, Inc.""",
        "contact" : 
            """        Juniper Technical Assistance Center
Juniper Networks, Inc.
1194 N. Mathilda Avenue
Sunnyvale, CA 94089
E-mail: support@juniper.net""",
        "description" :
            """This is Juniper Networks' implementation of enterprise
specific MIB for alarms from the router chassis box.""",
        "revisions" : (
            {
                "date" : "2003-07-18 21:53",
                "description" :
                    """[Revision added by libsmi due to a LAST-UPDATED clause.]""",
            },
        ),
        "identity node" : "jnxAlarms",
    },

    "imports" : (
        {"module" : "SNMPv2-SMI", "name" : "MODULE-IDENTITY"},
        {"module" : "SNMPv2-SMI", "name" : "OBJECT-TYPE"},
        {"module" : "SNMPv2-SMI", "name" : "Gauge32"},
        {"module" : "SNMPv2-TC", "name" : "TimeStamp"},
        {"module" : "JUNIPER-SMI", "name" : "jnxMibs"},
    ),

    "nodes" : {
        "jnxAlarms" : {
            "nodetype" : "node",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4",
            "status" : "current",
        }, # node
        "jnxCraftAlarms" : {
            "nodetype" : "node",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2",
        }, # node
        "jnxAlarmRelayMode" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.1",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Enumeration",
                    "other" : {
                        "nodetype" : "namednumber",
                        "number" : "1"
                    },
                    "passOn" : {
                        "nodetype" : "namednumber",
                        "number" : "2"
                    },
                    "cutOff" : {
                        "nodetype" : "namednumber",
                        "number" : "3"
                    },
                },
            },
            "access" : "readonly",
            "description" :
                """The alarm relay mode of the craft interface
panel for both yellow and red alarms.

Both yellow and red alarms could be cut off 
by a front panel Alarm Cutoff / Lamp Test 
(ACO/LT) button.

In the pass-on mode, the alarm relay will be 
activated to pass on the yellow or red alarms.
In the cut-off mode, both yellow and red alarms
will be cut off from the alarm relays which are 
normally connected to audible sirens or visual 
flashing devices.""",
        }, # scalar
        "jnxYellowAlarms" : {
            "nodetype" : "node",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.2",
        }, # node
        "jnxYellowAlarmState" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.2.1",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Enumeration",
                    "other" : {
                        "nodetype" : "namednumber",
                        "number" : "1"
                    },
                    "off" : {
                        "nodetype" : "namednumber",
                        "number" : "2"
                    },
                    "on" : {
                        "nodetype" : "namednumber",
                        "number" : "3"
                    },
                },
            },
            "access" : "readonly",
            "description" :
                """The yellow alarm state on the craft interface 
panel.

The yellow alarm is on when there is some 
system warning such as maintenance alert or 
significant temperature increase.

This yellow alarm state could be turned off 
by the ACO/LT (Alarm Cut Off / Lamp Test) button
on the front panel module.""",
        }, # scalar
        "jnxYellowAlarmCount" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.2.2",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-SMI", "name" : "Gauge32"},
            },
            "access" : "readonly",
            "description" :
                """The number of currently active and non-silent 
yellow alarms.

This object is independent of the ACO/LT (Alarm
Cut Off / Lamp Test) button.""",
        }, # scalar
        "jnxYellowAlarmLastChange" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.2.3",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-TC", "name" : "TimeStamp"},
            },
            "access" : "readonly",
            "description" :
                """The value of sysUpTime when the yellow alarm
last changed - either from off to on or vice
versa. 	Zero if unknown or never changed since
the agent was up.""",
        }, # scalar
        "jnxRedAlarms" : {
            "nodetype" : "node",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.3",
        }, # node
        "jnxRedAlarmState" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.3.1",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "Enumeration",
                    "other" : {
                        "nodetype" : "namednumber",
                        "number" : "1"
                    },
                    "off" : {
                        "nodetype" : "namednumber",
                        "number" : "2"
                    },
                    "on" : {
                        "nodetype" : "namednumber",
                        "number" : "3"
                    },
                },
            },
            "access" : "readonly",
            "description" :
                """The red alarm indication on the craft interface 
panel.

The red alarm is on when there is some system 
failure or power supply failure or the system 
is experiencing a hardware malfunction or some 
threshold is being exceeded.

This red alarm state could be turned off by the
ACO/LT (Alarm Cut Off / Lamp Test) button on the
front panel module.""",
        }, # scalar
        "jnxRedAlarmCount" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.3.2",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-SMI", "name" : "Gauge32"},
            },
            "access" : "readonly",
            "description" :
                """The number of currently active and non-silent 
red alarms.

This object is independent of the ACO/LT (Alarm
Cut Off / Lamp Test) button.""",
        }, # scalar
        "jnxRedAlarmLastChange" : {
            "nodetype" : "scalar",
            "moduleName" : "JUNIPER-ALARM-MIB",
            "oid" : "1.3.6.1.4.1.2636.3.4.2.3.3",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-TC", "name" : "TimeStamp"},
            },
            "access" : "readonly",
            "description" :
                """The value of sysUpTime when the red alarm
last changed - either from off to on or vice
versa. 	Zero if unknown or never changed since
the agent was up.""",
        }, # scalar
    }, # nodes

}
