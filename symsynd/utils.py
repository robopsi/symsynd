import os
import time
import threading
from contextlib import contextmanager
from symsynd._compat import int_types


def parse_addr(x):
    if x is None:
        return 0
    if isinstance(x, int_types):
        return x
    if isinstance(x, basestring):
        if x[:2] == '0x':
            return int(x[2:], 16)
        return int(x)
    raise ValueError('Unsupported address format %r' % (x,))


_timeit = os.environ.get('SYMSYND_ENABLE_TIMERS') == '1'
if _timeit:
    _timers = {}
    _indentations = {}
    _local = threading.local()
    _last_print = time.time()


@contextmanager
def timedsection(key):
    if not _timeit:
        yield
        return

    try:
        _local.indent = _local.indent + 1
    except AttributeError:
        _local.indent = 0
    storage = _timers.setdefault(key, [])
    _indentations[key] = _local.indent
    now = time.time()
    try:
        yield
    finally:
        _local.indent -= 1
        dt = time.time() - now
        storage.append(dt)
        del storage[1000:]

        if _last_print < time.time() - 1:
            print_timers()


def print_timers():
    if not _timeit:
        return

    global _last_print
    for key, storage in sorted(_timers.items()):
        if not storage:
            dt = 0
        else:
            dt = sum(storage) / len(storage) * 1000
        print('%s%s: %.3fms' % (
            ' ' * (_indentations.get(key, 0) * 2),
            key,
            dt
        ))
    print('')
    _last_print = time.time()
