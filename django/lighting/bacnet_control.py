#!/usr/bin/python

"""These functions wrap the bacnet command line apps from http://bacnet.sourceforge.net/
In your django settings you'll need a BACNET_BIN_DIR with the full path to the directory containing the compiled apps.
Like so (no slash on the end, please):
BACNET_BIN_DIR = '/usr/local/src/bacnet-stack-0.5.3/bin'
"""

import os, sys, subprocess
from django.conf import settings
import logging

USAGE_MESSAGE = 'usage: bacnet_control <read-ao|write-ao> <device id> <property id> [<value>]'

class BacnetControl:
    def __init__(self, bin_dir_path, bacnet_port=47809):
        self.bin_dir_path = bin_dir_path
        self.bacnet_port = bacnet_port
    def run_command(self, args):
        os.environ['BACNET_IP_PORT'] = '%s' % self.bacnet_port
        #args = ['/var/www/Art-Server/art_server/bacnet_bins/bacrp 77000 2 1 85'] #[' '.join(args)]
        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.bin_dir_path)
        output = ''
        for line in proc.stdout:
            #if line == '' and proc.poll() != None: break
            output = '%s%s' % (output, line)
        err_output = ''
        for line in proc.stderr:
            err_output = '%s%s' % (err_output, line)
        proc.wait()
        return (proc.returncode, output, err_output)

    def get_bin_path(self, bin_name):
        bin_name = '%s%s' % (bin_name, settings.BACNET_EXECUTABLE_EXTENSION)
        bin_path = os.path.join(self.bin_dir_path, bin_name)
        if not os.path.exists(bin_path):
            raise IOError('Bacnet bin does not exist: %s' % bin_path)
        return bin_path

    def read_analog_output(self, device_id, property_id):
        """Returns the Present-Value of an Analog Output property"""
        bin_path = self.get_bin_path('bacrp')
        # bacrp device-instance object-type object-instance property [index]
        # bacrp 100 2 23 1 85
        args = [bin_path, '%s' % int(device_id), '2', '%s' % int(property_id), '85']
        return self.run_command(args)

    def write_analog_output_int(self, device_id, property_id, value):
        """Returns the Present-Value of an Analog Output property"""
        bin_path = self.get_bin_path('bacwp')
        # bacwp device-instance object-type object-instance property priority index tag value [tag value...]
        # bacwp 77000 2 1 85 0 -1 4 99.0
        args = [bin_path, '%s' % int(device_id), '2', '%s' % int(property_id), '85', '0', '-1', '4', '%s' % value]
        print args
        return self.run_command(args)

def main():
    try:
        action = sys.argv[1]
        device_id = sys.argv[2]
        property_id = sys.argv[3]
    except IndexError:
        print USAGE_MESSAGE
        return

    control = BacnetControl(settings.BACNET_BIN_DIR)
    if action == 'read-ao':
        print control.read_analog_output(device_id, property_id)
    elif action == 'write-ao':
        try:
            value = sys.argv[4]
        except IndexError:
            print USAGE_MESSAGE
            return
        print control.write_analog_output_int(device_id, property_id, value)
    else:
        print USAGE_MESSAGE
        return

if __name__ == '__main__':
    main()
