"""
Fernando H. Barreiro Megino
"""

import os

from ConfigParser import SafeConfigParser
from threading import Lock

class BadConfigurationError(Exception):
    pass


_config = SafeConfigParser()
try:
    _config.read(['/etc/sls_monitoring.cfg'])
except Exception, e:
    raise BadConfigurationError('Could not parse configuration files due to error [%s]' % e)


# configuration objects
_params = {}
_lock = Lock()
   

def get_config(param, type=str, mandatory=False, section='siteservices'):
    """
    Read setting from configuration file.
   
    @param param: The parameter name to read.
    @param type: If specified, validates against python type.
    @param mandatory: Flag indicating whether parameter must be present.
    @param section: If specified, overrides default configuration file section.
    """
    _lock.acquire()
    try:
        if section in _params and param in _params[section]:
            return _params[section][param]
        value = None
        try:
            value = _config.get(section, param)
        except Exception, e:
            pass
        if not value and mandatory:
            raise BadConfigurationError("Mandatory parameter '%s' missing from configuration file section [%s]" % (param, section))
        try:
            if not value: # empty string is None
                value = None
            elif value and type:
                if type == int:
                    value = int(value)
                    assert(isinstance(value, int))
                elif type == long:
                    value = long(value)
                    assert(isinstance(value, long))
                elif type == bool:
                    value = value.strip()
                    if str(value).upper() in ['ON', 'TRUE', 'T', 'Y', 'YES', '1']:
                        value = True
                    elif str(value).upper() in ['OFF', 'FALSE', 'F', 'N', 'NO', '0']:
                        value = False
                    assert(isinstance(value, bool))                    
                elif type == str:
                    value = value.strip()
                    assert(isinstance(value, str))
                elif type == float:
                    value = float(value)
                    assert(isinstance(value, float))
                elif type == list:
                    value = value.strip().split(',')
                    assert(isinstance(value, list))
                    while True:
                        try: value.remove('')
                        except ValueError: break
        except Exception, e:
            raise BadConfigurationError('Error reading parameter from configuration file [%s]' % param)
        _params.setdefault(section, {})
        _params[section][param] = value
        return value
    finally:
        _lock.release()
