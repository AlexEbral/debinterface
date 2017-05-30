#!/usr/bin/env python

import debinterface
import debinterface.interfaces
import debinterface.adapter
import sys

if __name__ == "__main__":
    intfile = sys.argv[1]
    interfaces = debinterface.interfaces.Interfaces(interfaces_path=intfile)
    interfaces.updateAdapters()

    adapters = interfaces.adapters
    options = {
          'hotplug'
        , 'auto'
        , 'name'
        , 'hwaddress'
        , 'address'
        , 'netmask'
        , 'network'
        , 'broadcast'
        , 'gateway'
        , 'bridge-opts'
        , 'addrFam'
        , 'source'
        , 'nameservers'
        , 'unknown'
        , 'up'
        , 'pre-up'
        , 'post-up'
        , 'down'
        , 'post-down'
    }

    print "network_managed_by_ansible: True"
    print "network_manage_devices: True"
    print "network_host_interfaces:"
    for apt in adapters:
        attrs = apt.export(options)
        if attrs['auto'] == None:
            attrs['auto'] = True
        if attrs['name'] == 'lo' and attrs['source'] == 'loopback':
            continue
        else:
            print "  - device: %s" % attrs['name']
            print "    description: %s network configs" % attrs['name']
            print "    auto: %s" % attrs['auto']
            print "    family: %s" % attrs['addrFam']
            print "    method: %s" % attrs['source']
            if attrs['address']:
                print "    address: %s" % attrs['address']
            if attrs['unknown'] and 'hwaddress' in attrs['unknown'] and attrs['unknown']['hwaddress']:
                print "    hwaddress: %s" % attrs['unknown']['hwaddress']
            if 'network' in attrs and attrs['network']:
                print "    network: %s" % attrs['network']
            if attrs['broadcast']:
                print "    broadcast: %s" % attrs['broadcast']
            if 'netmask' in attrs and attrs['netmask']:
                print "    netmask: %s" % attrs['netmask']
            if 'gateway' in attrs and attrs['gateway']:
                print "    gateway: %s" % attrs['gateway']
            if 'nameservers' in attrs and attrs['nameservers']:
                print "    nameservers:"
                for ns in attrs['nameservers']:
                    print "      - %s" % ns
            if attrs['unknown'] and 'dns-nameservers' in attrs['unknown'] and attrs['unknown']['dns-nameservers']:
                print "    nameservers: %s" % attrs['unknown']['dns-nameservers']
            if attrs['unknown']:
                if 'dns-search' in attrs['unknown'] and attrs['unknown']['dns-search']:
                    print "    dns_search: %s" % attrs['unknown']['dns-search']
                else:
                    print "    dns_search: %s" % argv[2]
            if 'up' in attrs and attrs['up']:
                print "    up:"
                for cmd in attrs['up']:
                    if cmd.startswith('ip addr add 10.'):
                        print "      - /usr/local/sbin/do_anchor_ip.sh %s" % attrs['name']
                    else:
                        print "      - %s" % cmd
            if 'pre-up' in attrs and attrs['pre-up']:
                print "    pre-up:"
                for cmd in attrs['pre-up']:
                    print "      - %s" % cmd
            if attrs['unknown'] and len(attrs['unknown']) > 0:
                bond = {}
                vlan = {}
                for key in attrs['unknown']:
                    if not key in ['hwaddress', 'address', 'netmask', 'network', 'broadcast', 'gateway', 'dns-search', 'dns-nameservers']:
                        if key.startswith('bond-'):
                            skey = key[5:]
                            bond[skey] = attrs['unknown'][key]
                        elif key.startswith('vlan-'):
                            skey = key[5:]
                            vlan[skey] = attrs['unknown'][key]
                        else:
                            print "    %s: %s ## unknown option" % (key, attrs['unknown'][key])
                if len(bond) > 0:
                    print "    bond:"
                    for key in bond:
                        print "      %s: %s" % (key, bond[key])
                if len(vlan) > 0:
                    print "    vlan:"
                    for key in vlan:
                        print "      %s: %s" % (key, vlan[key])

    if interfaces.includes:
        print "## WARNING: there are more configs for this host"
