from array import array
from tempfile import NamedTemporaryFile

from nose.tools import eq_

from coverage import Coverage


def test_to_file_and_from_file():

    cov = Coverage()
    cov['foo'].extend(range(1, 11))
    cov['bar'].extend(range(1, 3))
    cov['baz']

    temp_write_fh = NamedTemporaryFile()
    cov.to_file(temp_write_fh.file)
    temp_write_fh.file.flush()

    temp_read_fh = open(temp_write_fh.name)
    loaded = Coverage()
    loaded.from_file(temp_read_fh)

    x = array('L')
    x.extend(range(1, 11))

    eq_(loaded['foo'], x)

    x = array('L')
    x.extend(range(1, 3))

    eq_(loaded['bar'], x)

    x = array('L')

    eq_(loaded['baz'], x)


def test_merge():

    a = Coverage()
    a['foo'].extend([1, 2, 3, 4])
    a['bar'].extend([1, 2, 3, 4])

    b = Coverage()
    b['foo'].extend([1, 2, 3, 4])
    b['bar'].extend([2, 2, 3, 4])

    c = a + b

    x = array('L')
    x.extend([2, 4, 6, 8])
    eq_(c['foo'], x)

    x = array('L')
    x.extend([3, 4, 6, 8])
    eq_(c['bar'], x)
