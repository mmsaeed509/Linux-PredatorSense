EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'

##------------------------------##
##----Class to read/write EC----##
class ECWrite:
    def __init__(self):
        print("Setting up EC access...")
        self.ec_path = EC_IO_FILE
        self.setupEC()

    def setupEC(self):
        try:
            self.ec_file = open(self.ec_path, 'rb+')
        except PermissionError:
            print('Run with sudo')
            exit(1)
        except FileNotFoundError:
            print(ec_path, 'not found. Creating the EC IO file...')
            # from subprocess import Popen
            # Popen(['modprobe', 'ec_sys', 'write_support=1'])
            # print('EC Changed. Restarting the application may help if it is not working.')

    def ec_write(self, address, value):

        try:
            self.ec_file.read()
            self.ec_file.seek(address)
            old_value = ord(self.ec_file.read(1))
            if value != old_value:
                # print("Before: %3d\tAfter: %3d" % (old_value, value))
                self.ec_file.seek(address)
                self.ec_file.write(bytearray([value]))
            else:
                print("Value was not changed: %s, %3d" % (hex(address), value))
                print("Before: %3d\tAfter: %3d" % (old_value, value))
        except Exception as e:
            print("Error" + str(e))

    def ec_refresh(self):
        self.ec_file.read()

    def ec_read(self, address):
        self.ec_file.seek(address)
        return ord(self.ec_file.read(1))

    def shutdownEC(self):
        self.ec_file.close()