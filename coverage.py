from array import array
from collections import defaultdict
import itertools
import json


class Coverage(object):
    array_factory = staticmethod(lambda: array('L'))

    def __init__(self):
        self._data = defaultdict(self.array_factory)

    def __getitem__(self, key):
        # TODO this acts like a defaultdict, returning an array for unknown keys
        #      is that what I want?
        return self._data[key]

    def __setitem__(self, key):
        # TODO better exception class
        raise Exception('Cannot set item on Coverage')

    def keys(self):
        return self._data.keys()

    def to_file(self, fh):
        # Note that in python 2.x, fh _must_ be a true file,
        # i.e. isinstance(fh, types.FileType) == True
        # otherwise array.tofile() will give an error "arg1 must be open file"
        #
        # I stumbled across this when trying to use GzipFile,
        # which is a subclass of IOBase and not types.FileType.
        #
        # Looks like python 3 reworked things so that gzip works.

        # Build index of reference names and sizes
        index = [(key, len(counts)) for key, counts in self._data.items()]

        # Convert index to JSON and write it to the file
        index_json = json.dumps(index)
        fh.write(index_json + '\n')

        # Write all counts arrays to the file
        for counts in self._data.values():
            counts.tofile(fh)

    def from_file(self, fh):
        # Note that in python 2.x, fh _must_ be a true file,
        # i.e. isinstance(fh, types.FileType) == True
        #
        # I stumbled across this when trying to use GzipFile,
        # which is a subclass of IOBase instead.
        #
        # Looks like python 3 reworked things so that gzip works.

        # Load the index
        index_json = fh.readline()
        index = json.loads(index_json)

        # Read all the counts into an array
        all_counts = self.array_factory()
        total = sum(length for key, length in index)
        all_counts.fromfile(fh, total)

        # Break the all_counts array up into the separate references
        offset = 0
        for key, length in index:
            self._data[key] = all_counts[offset:offset + length]
            offset += length

    @classmethod
    def merge(cls, *coverages):

        merged = cls()

        # Get unique set of reference names.
        refs = set()

        for coverage in coverages:
            if not isinstance(coverage, Coverage):
                # TODO better error message
                raise TypeError('invalid operands: can only update from Coverage instances')

            refs.update(coverage.keys())

        # For every reference, merge the coverage counts for that reference
        for ref in refs:

            # Get the coverage counts for this reference from each coverage file 
            ref_covs = [cov[ref] for cov in coverages]

            # Now merge those
            zipped = itertools.izip_longest(*ref_covs, fillvalue=0)
            merged[ref].extend(sum(row) for row in zipped)

        return merged


    def __add__(self, other):
        if not isinstance(other, Coverage):
            # TODO better error message
            raise TypeError('invalid operands: can only add Coverage instances')

        return Coverage.merge(self, other)
