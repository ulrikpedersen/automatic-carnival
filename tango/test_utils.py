"""Test utilities"""

import sys
import six
import enum
try:
    import collections.abc as collections_abc  # python 3.3+
except ImportError:
    import collections as collections_abc

# Local imports
from . import DevState, GreenMode
from .server import Device
from .test_context import MultiDeviceTestContext, DeviceTestContext
from . import DeviceClass, LatestDeviceImpl, DevLong64, SCALAR, READ

# Conditional imports
try:
    import pytest
except ImportError:
    pytest = None

try:
    import numpy.testing
except ImportError:
    numpy = None

__all__ = (
    'MultiDeviceTestContext',
    'DeviceTestContext',
    'SimpleDevice',
    'ClassicAPISimpleDeviceImpl',
    'ClassicAPISimpleDeviceClass'
)

PY3 = sys.version_info >= (3,)

# char \x00 cannot be sent in a DevString. All other 1-255 chars can
ints = tuple(range(1, 256))
bytes_devstring = bytes(ints) if PY3 else ''.join(map(chr, ints))
str_devstring = bytes_devstring.decode('latin-1')

# Test devices

class SimpleDevice(Device):
    def init_device(self):
        self.set_state(DevState.ON)


class ClassicAPISimpleDeviceImpl(LatestDeviceImpl):
    def __init__(self, cls, name):
        LatestDeviceImpl.__init__(self, cls, name)
        ClassicAPISimpleDeviceImpl.init_device(self)

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.attr_attr1_read = 100

    def read_attr1(self, attr):
        attr.set_value(self.attr_attr1_read)


class ClassicAPISimpleDeviceClass(DeviceClass):
    attr_list = {"attr1": [[DevLong64, SCALAR, READ]]}


# Test enums

class GoodEnum(enum.IntEnum):
    START = 0
    MIDDLE = 1
    END = 2


class BadEnumNonZero(enum.IntEnum):
    START = 1
    MIDDLE = 2
    END = 3


class BadEnumSkipValues(enum.IntEnum):
    START = 0
    MIDDLE = 2
    END = 4


class BadEnumDuplicates(enum.IntEnum):
    START = 0
    MIDDLE = 1
    END = 1


# Helpers

# Note on Tango properties using the Tango File database:
# Tango file database cannot handle properties with '\n'. It doesn't
# handle '\' neither. And it cuts ASCII extended characters. That is
# why you will find that all property related tests are truncated to
# the first two values of the arrays below

TYPED_VALUES = {
    int: (1, 2, -65535, 23),
    float: (2.71, 3.14, -34.678e-10, 12.678e+15),
    str: ('hey hey', 'my my', bytes_devstring, str_devstring),
    bool: (False, True, True, False),
    (int,): ([1, 2, 3], [9, 8, 7], [-65535, 2224], [0, 0]),
    (float,): ([0.1, 0.2, 0.3], [0.9, 0.8, 0.7], [-6.3232e-3], [0.0, 12.56e+12]),
    (str,): (['ab', 'cd', 'ef'], ['gh', 'ij', 'kl'], 10*[bytes_devstring], 10*[str_devstring]),
    (bool,): ([False, False, True], [True, False, False], [False], [True])}

# these sets to test Device Server input arguments

OS_SYSTEMS = ['linux', 'win']

#    os_system, in string, out arguments list, raised exception
DEVICE_SERVER_ARGUMENTS = (
    (['linux', 'win'], 'MyDs instance --nodb --port 1234',
     ['MyDs', 'instance', '-nodb', '-ORBendPoint', 'giop:tcp::1234']),
    (['linux', 'win'], 'MyDs -port 1234 -host myhost instance',
     ['MyDs', 'instance', '-ORBendPoint', 'giop:tcp:myhost:1234']),
    (['linux', 'win'], 'MyDs instance --ORBendPoint giop:tcp::1234',
     ['MyDs', 'instance', '-ORBendPoint', 'giop:tcp::1234']),
    (['linux', 'win'], 'MyDs instance -nodb -port 1000 -dlist a/b/c;d/e/f',
     ['MyDs', 'instance', '-ORBendPoint', 'giop:tcp::1000', '-nodb', '-dlist', 'a/b/c;d/e/f']),
    (['linux', 'win'], 'MyDs instance -file a/b/c',
     ['MyDs', 'instance', '-file=a/b/c']),
    ([], 'MyDs instance -nodb', []),  # this test should always fail
    ([], 'MyDs instance -dlist a/b/c;d/e/f', []),  # this test should always fail

# the most complicated case: verbose
    (['linux', 'win'], 'MyDs instance -vvvv', ['MyDs', 'instance', '-v4']),
    (['linux', 'win'], 'MyDs instance --verbose --verbose --verbose --verbose', ['MyDs', 'instance', '-v4']),
    (['linux', 'win'], 'MyDs instance -v4', ['MyDs', 'instance', '-v4']),
    (['linux', 'win'], 'MyDs instance -v 4', ['MyDs', 'instance', '-v4']),

# some options can be only in win, in linux should be error
    (['win'], 'MyDs instance -dbg -i -s -u', ['MyDs', 'instance', '-dbg', '-i', '-s', '-u']),

# variable ORB options
    (['linux', 'win'], 'MyDs instance -ORBtest1 test1 --ORBtest2 test2',
     ['MyDs', 'instance', '-ORBtest1', 'test1', '-ORBtest2', 'test2']),
    (['linux', 'win'], 'MyDs ORBinstance -ORBtest myORBparam',
     ['MyDs', 'ORBinstance', '-ORBtest', 'myORBparam']),
    (['linux', 'win'], 'MyDs instance -nodb -ORBendPoint giop:tcp:localhost:1234 -ORBendPointPublish giop:tcp:myhost.local:2345',
     ['MyDs', 'instance', '-nodb', '-ORBendPoint', 'giop:tcp:localhost:1234', '-ORBendPointPublish', 'giop:tcp:myhost.local:2345']),
    ([], 'MyDs instance -ORBtest1 test1 --orbinvalid value', []),  # lowercase "orb" should fail
)

def repr_type(x):
    if not isinstance(x, tuple):
        return x.__name__
    return '({},)'.format(x[0].__name__)


# Numpy helpers

if numpy and pytest:

    def assert_close(a, b):
        if isinstance(a, six.string_types):
            assert a == b
            return
        if isinstance(a, collections_abc.Sequence) and len(a) and isinstance(a[0], six.string_types):
            assert list(a) == list(b)
            return
        try:
            assert a == pytest.approx(b)
        except ValueError:
            numpy.testing.assert_allclose(a, b)

# Pytest fixtures

if pytest:

    def create_result(dtype, value):
        if dtype == str:
            if PY3:
                if isinstance(value, six.binary_type):
                    return value.decode('latin-1')
            else:
                if isinstance(value, six.text_type):
                    return value.encode('latin-1')
        elif dtype == (str,):
            return [create_result(str, v) for v in value]
        return value

    @pytest.fixture(params=DevState.values.values())
    def state(request):
        return request.param

    @pytest.fixture(
        params=list(TYPED_VALUES.items()),
        ids=lambda x: repr_type(x[0]))
    def typed_values(request):
        dtype, values = request.param
        expected = lambda v: create_result(dtype, v)
        return dtype, values, expected

    @pytest.fixture(params=GreenMode.values.values())
    def green_mode(request):
        return request.param

    @pytest.fixture(params=[
        GreenMode.Synchronous,
        GreenMode.Asyncio,
        GreenMode.Gevent])
    def server_green_mode(request):
        return request.param

    @pytest.fixture(params=['linux', 'win'])
    def os_system(request):
        original_platform = sys.platform
        sys.platform = request.param
        yield
        sys.platform = original_platform
