# xarray `CombinedLock` can invert netCDF lock order

Proposed upstream issue for `pydata/xarray`. Prepared 2026-09-26; not submitted.

## Problem

`CombinedLock.__init__` deduplicates with `tuple(set(locks))`. Set iteration can
order shared locks differently in two combinations. `combine_locks` also
flattens an existing `CombinedLock`, so a netCDF read lock containing the HDF5
and netCDF-C locks can acquire them in the reverse order from a write lock
containing those same locks plus a file lock. Two threads can then each hold one
shared lock while waiting for the other.

In xarray 2026.4.0, our test process hung with two readers and one writer in
`CombinedLock.__enter__`, and its main thread in `as_completed`. The relevant
frames from the faulthandler dump were:

```text
reader 1: xarray/backends/locks.py:66 SerializableLock.__enter__
          xarray/backends/locks.py:229 CombinedLock.__enter__
          xarray/backends/netCDF4_.py open_dataset / get_attrs
reader 2: xarray/backends/locks.py:66 SerializableLock.__enter__
          xarray/backends/locks.py:229 CombinedLock.__enter__
          xarray/backends/netCDF4_.py open_dataset / get_attrs
writer:   xarray/backends/locks.py:66 SerializableLock.__enter__
          xarray/backends/locks.py:229 CombinedLock.__enter__
          xarray/backends/netCDF4_.py NetCDF4DataStore.open / to_netcdf
main:     concurrent/futures/_base.py:243 as_completed
```

The complete log is in CI run `36179897121` of `tanerumit/blueearth_cst`
(potentially private, so the excerpt above is self-contained). A separate process
probe found the read/write shared-lock order disagreed in 22 of 120 fresh
Python interpreters. All 22 disagreements occurred when the two shared locks'
hashes collided modulo 8; 98 interpreters agreed. This is a lock-order proof,
not a deterministic reproduction of the test hang.

## Minimal order probe

```python
import threading

from xarray.backends.locks import HDF5_LOCK, NETCDFC_LOCK, combine_locks

read = combine_locks([NETCDFC_LOCK, HDF5_LOCK])
write = combine_locks([read, threading.Lock()])

def order(combined):
    return "".join(
        "H" if lock is HDF5_LOCK else "N"
        for lock in combined.locks
        if lock is HDF5_LOCK or lock is NETCDFC_LOCK
    )

print(order(read), order(write))
```

Run this in fresh interpreters, since singleton lock identities and set order
are stable within one process. Both `HN NH` and matching orders are possible.
When the orders disagree, two threads entering `read` and `write` can deadlock.

## Expected behavior

Every combination containing the same underlying locks acquires them in one
consistent order. Deduplication should preserve that invariant; preserving
input order alone would not suffice if callers pass combinations in different
orders. A stable ordering key or another shared ordering rule is needed.

## Local mitigation and limits

We serialized each `netcdf_glob` file's open, clip, write, and close unit in
`dev/scripts/stage_data.py`, with synchronous Dask execution inside the unit.
`test_netcdf_glob_units_never_overlap` asserts peak occupancy of one. This
removes concurrent netCDF access in that path. It does not change xarray and
does not establish the cause of a separate hydromt staticmaps write stall.

The latter occurred in a call already wrapped by
`dask.config.set(scheduler="synchronous")`, so attributing it to Dask worker
threads would need a complete thread dump from that process.
