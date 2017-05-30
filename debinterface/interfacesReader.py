# A class representing the contents of /etc/network/interfaces

from adapter import NetworkAdapter
import StringIO


class InterfacesReader:
    ''' Short lived class to read interfaces file '''

    def __init__(self, interfaces_path):
        self._interfaces_path = interfaces_path
        self._reset()

    @property
    def adapters(self):
        return self._adapters

    @property
    def includes(self):
        return self._include_list

    def parse_interfaces(self):
        ''' Read /etc/network/interfaces.  '''
        self._reset()

        # Open up the interfaces file. Read only.
        with open(self._interfaces_path, "r") as interfaces:
            self._read_lines_from_file(interfaces)

        return self._parse_interfaces_impl()

    def parse_interfaces_from_string(self, data):
        self._reset()

        # Can't be used in 'with..as'
        string_file = StringIO.StringIO(data)
        self._read_lines_from_file(string_file)
        string_file.close()

        return self._parse_interfaces_impl()

    def _parse_interfaces_impl(self):
        ''' Save adapters
            Return an array of networkAdapter instances.
        '''
        for entry in self._auto_list:
            for adapter in self._adapters:
                if adapter._ifAttributes['name'] == entry:
                    adapter.setAuto(True)

        for entry in self._hotplug_list:
            for adapter in self._adapters:
                if adapter._ifAttributes['name'] == entry:
                    adapter.setHotplug(True)

        return self._adapters

    def _read_lines_from_file(self, fileObj):
        # Loop through the interfaces file.
        for line in fileObj:
            # Identify the clauses by analyzing the first word of each line.
            # Go to the next line if the current line is a comment.
            if line.strip().startswith("#") is True:
                pass
            else:
                self._parse_iface(line)
                # Ignore blank lines.
                if line.isspace() is True:
                    pass
                else:
                    self._parse_details(line)
                self._read_auto(line)
                self._read_hotplug(line)
                self._read_source(line)

    def _parse_iface(self, line):
        if line.startswith('iface'):
            sline = line.split()
            # Update the self._context when an iface clause is encountered.
            self._context += 1
            self._adapters.append(NetworkAdapter(sline[1]))
            self._adapters[self._context].setAddressSource(sline[-1])
            self._adapters[self._context].setAddrFam(sline[2])

    def _parse_details(self, line):
        sline = line.split()
        #if line[0].isspace() is True:
        if not sline[0] in {'auto', 'iface', 'allow-auto', 'allow-hotplug', 'source'}:
            if sline[0] == 'address':
                self._adapters[self._context].setAddress(sline[1])
            elif sline[0] == 'netmask':
                self._adapters[self._context].setNetmask(sline[1])
            elif sline[0] == 'gateway':
                ud = sline.pop(0)
                self._adapters[self._context].setGateway(' '.join(sline))
            elif sline[0] == 'broadcast':
                self._adapters[self._context].setBroadcast(sline[1])
            elif sline[0] == 'network':
                self._adapters[self._context].setNetwork(sline[1])
            elif sline[0].startswith('bridge') is True:
                opt = sline[0].split('_')
                sline.pop(0)
                ifs = " ".join(sline)
                self._adapters[self._context].replaceBropt(opt[1], ifs)
            elif sline[0] == 'nameservers' or sline[0] == 'dns-nameservers':
                ns = sline.pop(0)
                self._adapters[self._context].setNameservers(sline)
            elif sline[0] == 'pre-up' or sline[0] == 'up' or sline[0] == 'post-up' or sline[0] == 'down' or sline[0] == 'pre-down' or sline[0] == 'post-down':
                ud = sline.pop(0)
                cmd = ' '.join(sline)
                if ud == 'up' or ud == 'post-up':
                    self._adapters[self._context].appendUp(cmd)
                elif ud == 'down' or ud == 'pre-down':
                    self._adapters[self._context].appendDown(cmd)
                elif ud == 'pre-up':
                    self._adapters[self._context].appendPreUp(cmd)
                elif ud == 'post-down':
                    self._adapters[self._context].appendPostDown(cmd)
            else:
                # store as if so as not to loose it
                key = sline.pop(0)
                try:
                    self._adapters[self._context].setUnknown(key, ' '.join(sline))
                except:
                    pass

    def _read_auto(self, line):
        ''' Identify which adapters are flagged auto. '''
        if line.startswith('auto'):
            sline = line.split()
            for word in sline:
                if word == 'auto':
                    pass
                else:
                    self._auto_list.append(word)

    def _read_hotplug(self, line):
        ''' Identify which adapters are flagged allow-hotplug. '''
        if line.startswith('allow-hotplug'):
            sline = line.split()
            for word in sline:
                if word == 'allow-hotplug':
                    pass
                else:
                    self._hotplug_list.append(word)

    def _read_source(self, line):
        if line.startswith('source'):
            sline = line.split()
            sline.pop(0)
            self._include_list.append(' '.join(sline))

    def _reset(self):
        # Initialize a place to store created networkAdapter objects.
        self._adapters = []

        # Keep a list of adapters that have the auto or allow-hotplug flags set.
        self._auto_list = []
        self._hotplug_list = []
        self._include_list = []

        # Store the interface context.
        # This is the index of the adapters collection.
        self._context = -1
