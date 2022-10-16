EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'

try:
    open(EC_IO_FILE, 'rb')
except PermissionError:
    print('Run with sudo')
    exit(1)
except FileNotFoundError:
    print(EC_IO_FILE, 'not found. Creating the EC IO file...')
    from subprocess import Popen
    Popen(['modprobe', 'ec_sys', 'write_support=1'])
    print('EC Changed. Restarting the application may help if it is not working.')


def ec_write(address, value):
    with open(EC_IO_FILE, "rb+") as f:
        f.seek(address)
        old_value = ord(f.read(1))
        if value != old_value:
            print("Before: %3d\nAfter: %3d" % (old_value, value))
            f.seek(address)
            f.write(bytearray([value]))
        else:
            print("Value was not changed: %3d" % value)


def ec_read(address):
    with open(EC_IO_FILE, "rb") as f:
        f.seek(address)
        return ord(f.read(1))
