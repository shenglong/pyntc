import os

from .devices import supported_devices, VENDOR_KEY, DEVICE_CLASS_KEY
from .errors import UnsupportedDeviceError, DeviceNameNotFoundError

try:
    from configparser import ConfigParser as SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

LIB_PATH_ENV_VAR = 'PYNTC_CONF'

def get_device(device_type, *args, **kwargs):
    try:
        device_class = supported_devices[device_type][DEVICE_CLASS_KEY]
        vendor = supported_devices[device_type][VENDOR_KEY]
        return device_class(*args, **kwargs)
    except KeyError:
        raise UnsupportedDeviceError(device_type)


def get_device_by_name(name, filename=None):
    config = get_config_from_file(filename=filename)
    sections = config.sections()
    for section in sections:
        if ':' in section:
            device_type_and_conn_name = section.split(':')
            device_type = device_type_and_conn_name[0]
            conn_name = device_type_and_conn_name[1]

            if name == conn_name:
                device_kwargs = dict(config.items(section))
                if 'host' not in device_kwargs:
                    device_kwargs['host'] = name

                return get_device(device_type, **device_kwargs)

    raise DeviceNameNotFoundError(name, filename)


def get_config_from_file(filename=None):
    if filename is None:
        if LIB_PATH_ENV_VAR in os.environ:
            filename = os.path.expanduser(os.environ[LIB_PATH_ENV_VAR])
        else:
            filename = os.path.expanduser('~/.ntc.conf')

    config = SafeConfigParser()
    config.read(filename)

    return config