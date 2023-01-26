"""Test utilities"""

import enum
import numpy as np

# Local imports
from . import DevState, GreenMode, AttrDataFormat
from .server import Device
from .test_context import MultiDeviceTestContext, DeviceTestContext
from .utils import is_non_str_seq
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
    'ClassicAPISimpleDeviceClass',
    'state',
    'command_typed_values',
    'attribute_typed_values',
    'server_green_mode',
    'attr_data_format'
)

# char \x00 cannot be sent in a DevString. All other 1-255 chars can
ints = tuple(range(1, 256))
bytes_devstring = bytes(ints)
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

GENERAL_TYPED_VALUES = {
    int: (1, 2, -65535, 23),
    float: (2.71, 3.14, -34.678e-10, 12.678e+15),
    str: ('hey hey', 'my my', bytes_devstring, str_devstring),
    bool: (False, True, True, False),
    (int,): (np.array([1, 2]), [1, 2, 3], [9, 8, 7], [-65535, 2224], [0, 0], ),
    (float,): (np.array([0.1, 0.2]), [0.1, 0.2, 0.3], [0.9, 0.8, 0.7], [-6.3232e-3], [0.0, 12.56e+12]),
    (str,): (np.array(['foo', 'bar']), ['ab', 'cd', 'ef'], ['gh', 'ij', 'kl'], 10*[bytes_devstring], 10*[str_devstring]),
    (bool,): (np.array([True, False]), [False, False, True], [True, False, False], [False], [True]),
}

IMAGE_TYPED_VALUES = {
    ((int,),): (np.vstack((np.array([1, 2]), np.array([3, 4]))),
                [[1, 2, 3], [4, 5, 6]], [[-65535, 2224], [-65535, 2224]],),
    ((float,),): (np.vstack((np.array([0.1, 0.2]), np.array([0.3, 0.4]))),
                  [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]], [[-6.3232e-3, 0.0], [0.0, 12.56e+12]],),
    ((str,),): (np.vstack((np.array(['hi-hi', 'ha-ha']), np.array(['hu-hu', 'yuhuu']))),
                [['ab', 'cd', 'ef'], ['gh', 'ij', 'kl']], [10*[bytes_devstring],10*[bytes_devstring]],
                [10*[str_devstring], 10*[str_devstring]],),
    ((bool,),): (np.vstack((np.array([True, False]), np.array([False, True]))),
                 [[False, False, True], [True, False, False]], [[False]], [[True]],)
}

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
    if isinstance(x, (list, tuple)):
        return f'({repr_type(x[0])},)'
    return f'{x.__name__}'


# Numpy helpers

if numpy and pytest:

    def __assert_all_types(a, b):
        if isinstance(a, str):
            assert a == b
            return

        try:
            assert a == pytest.approx(b)
        except (ValueError, TypeError):
            numpy.testing.assert_allclose(a, b)

    def assert_close(a, b):
        if is_non_str_seq(a):
            assert len(a) == len(b)
            for _a, _b in zip(a, b):
                assert_close(_a, _b)
        else:
            __assert_all_types(a, b)


# Pytest fixtures

if pytest:

    def __convert_value(value):
        if isinstance(value, bytes):
            return value.decode('latin-1')
        return value

    def create_result(dtype, value):
        if isinstance(dtype, (list, tuple)):
            dtype = dtype[0]
            return [create_result(dtype, v) for v in value]

        return __convert_value(value)

    @pytest.fixture(params=DevState.values.values())
    def state(request):
        return request.param

    @pytest.fixture(
        params=list(GENERAL_TYPED_VALUES.items()),
        ids=lambda x: repr_type(x[0]))
    def command_typed_values(request):
        dtype, values = request.param
        expected = lambda v: create_result(dtype, v)
        return dtype, values, expected

    @pytest.fixture(
        params=list({**GENERAL_TYPED_VALUES, **IMAGE_TYPED_VALUES}.items()),
        ids=lambda x: repr_type(x[0]))
    def attribute_typed_values(request):
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

    @pytest.fixture(params=[
        AttrDataFormat.SCALAR,
        AttrDataFormat.SPECTRUM,
        AttrDataFormat.IMAGE])
    def attr_data_format(request):
        return request.param
