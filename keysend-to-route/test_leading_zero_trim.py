from pyln.proto.primitives import varint_encode

from primitives import noleading_zeros_int_encode


def test_leading_zero_0():
    assert noleading_zeros_int_encode(0) == b''


def test_leading_zero_1b():
    assert noleading_zeros_int_encode(255) == b'\xff'


def test_leading_zero_2b():
    assert noleading_zeros_int_encode(65535) == b'\xff\xff'



