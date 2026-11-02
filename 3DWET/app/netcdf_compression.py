"""Optional lossless compression for completed GETM result files."""
from __future__ import annotations

from contextlib import nullcontext
from itertools import product
import os
from pathlib import Path
import tempfile
import time
import math

import numpy as np
from netCDF4 import Dataset


_CLASSIC_MODELS = {"NETCDF3_CLASSIC", "NETCDF3_64BIT_OFFSET", "NETCDF4_CLASSIC"}
_TARGET_CHUNK_BYTES = 1024 * 1024
# netCDF4's default chunk cache is 64 MiB *per variable*. A 3D result may
# contain hundreds of variables, so leaving the default in place can consume
# several GiB during a lossless whole-file copy or verification pass.
_TARGET_VARIABLE_CACHE_BYTES = 128 * 1024
_TARGET_VARIABLE_CACHE_SLOTS = 1009


class _CompressionCancelled(Exception):
    pass


def format_compression_result(result):
    """Describe post-run compression and verification without implying solver time."""
    status = result.get("status", "failed")
    elapsed = result.get("elapsed_seconds")
    if isinstance(elapsed, (int, float)) and math.isfinite(elapsed) and elapsed >= 0:
        duration = f"{elapsed:.1f} 秒"
    else:
        duration = "未知"

    original = result.get("original_bytes")
    compressed = result.get("compressed_bytes")
    valid_original = isinstance(original, (int, float)) and math.isfinite(original) and original >= 0
    valid_compressed = isinstance(compressed, (int, float)) and math.isfinite(compressed) and compressed >= 0
    original_text = f"{original / (1024 * 1024):.1f} MiB" if valid_original else "未知"
    if status == "compressed":
        outcome = "无损压缩并逐值核验通过，已替换原文件"
        candidate_text = f"新文件 {compressed / (1024 * 1024):.1f} MiB" if valid_compressed else "新文件大小未知"
        sizes = f"原始 {original_text} → {candidate_text}"
        if valid_original and valid_compressed:
            saved_bytes = original - compressed
            savings = (f"实际节省 {saved_bytes} bytes；比例不适用（原文件为 0）"
                       if original == 0 else f"实际节省 {saved_bytes} bytes（{saved_bytes * 100 / original:.1f}%）")
        else:
            savings = "实际节省无法计算"
    elif status == "not_smaller":
        outcome = "压缩及逐值核验完成，未采用候选文件，未替换原文件"
        candidate_text = f"候选文件 {compressed / (1024 * 1024):.1f} MiB（核验后未采用）" if valid_compressed else "候选文件大小未知"
        sizes = f"原始 {original_text}；{candidate_text}"
        if valid_original:
            savings = ("实际节省 0 bytes；比例不适用（原文件为 0）" if original == 0
                       else "实际节省 0 bytes（0.0%）")
        else:
            savings = "实际节省无法计算"
    elif status == "cancelled":
        outcome = "压缩/核验已取消，未替换原文件"
        candidate_text = f"候选文件 {compressed / (1024 * 1024):.1f} MiB（未完成）" if valid_compressed else "候选文件大小未知"
        sizes = f"原始 {original_text}；{candidate_text}"
        savings = ("实际节省 0 bytes；比例不适用（原文件为 0）" if valid_original and original == 0
                   else "实际节省 0 bytes（0.0%）" if valid_original
                   else "实际节省无法计算")
    elif status == "skipped":
        outcome = "跳过压缩，未生成候选文件，未替换原文件"
        sizes = f"原始 {original_text}"
        savings = ("实际节省 0 bytes；比例不适用（原文件为 0）" if valid_original and original == 0
                   else "实际节省 0 bytes（0.0%）" if valid_original
                   else "实际节省无法计算")
    else:
        outcome = "压缩/核验失败，未替换原文件，候选文件已清理"
        candidate_text = f"候选文件 {compressed / (1024 * 1024):.1f} MiB（未验证并已清理）" if valid_compressed else "候选文件大小未知"
        sizes = f"原始 {original_text}；{candidate_text}"
        savings = ("实际节省 0 bytes；比例不适用（原文件为 0）" if valid_original and original == 0
                   else "实际节省 0 bytes（0.0%）" if valid_original
                   else "实际节省无法计算")
    error = result.get("error")
    detail = f"；原因：{error}" if error else ""
    timing = "压缩处理耗时" if status == "skipped" else "压缩及逐值核验耗时"
    return f"{outcome}；{timing} {duration}；{sizes}；{savings}{detail}。"


def compression_chunksizes(dimensions, shape, dtype,
                           max_chunk_bytes=_TARGET_CHUNK_BYTES):
    """Plan chunks for frame/layer maps and time series within a byte budget."""
    if len(dimensions) != len(shape):
        raise ValueError("dimension and shape lengths differ")
    if not shape:
        return None
    if isinstance(max_chunk_bytes, bool) or int(max_chunk_bytes) < 1:
        raise ValueError("max_chunk_bytes must be positive")
    chunks = []
    for dim, length in zip(dimensions, shape):
        length = max(1, int(length))
        if dim == "time":
            chunks.append(min(4, length))
        elif dim == "sigma":
            chunks.append(min(2, length))
        elif dim in ("yc", "xc"):
            chunks.append(min(128, length))
        else:
            chunks.append(min(64, length))
    itemsize = max(1, np.dtype(dtype).itemsize)
    while int(np.prod(chunks, dtype=np.int64)) * itemsize > int(max_chunk_bytes):
        candidates = [i for i, size in enumerate(chunks) if size > 1]
        if not candidates:
            break
        axis = max(candidates, key=lambda i: chunks[i])
        chunks[axis] = max(1, (chunks[axis] + 1) // 2)
    return tuple(chunks)


def _block_slices(shape, chunks):
    if not shape:
        yield Ellipsis
        return
    axes = [range(0, int(length), int(chunk))
            for length, chunk in zip(shape, chunks)]
    for starts in product(*axes):
        yield tuple(slice(start, min(int(length), start + int(chunk)))
                     for start, length, chunk in zip(starts, shape, chunks))


def _values_equal(left, right):
    left, right = np.ma.asarray(left), np.ma.asarray(right)
    if left.shape != right.shape:
        return False
    if not np.array_equal(np.ma.getmaskarray(left), np.ma.getmaskarray(right)):
        return False
    a, b = np.asarray(left.filled(0)), np.asarray(right.filled(0))
    if a.dtype.kind in "fc" or b.dtype.kind in "fc":
        return np.array_equal(a, b, equal_nan=True)
    return np.array_equal(a, b)


def _attribute_equal(left, right):
    a, b = np.asarray(left), np.asarray(right)
    if a.shape != b.shape:
        return False
    if a.dtype.kind in "fc" or b.dtype.kind in "fc":
        return np.array_equal(a, b, equal_nan=True)
    return np.array_equal(a, b)


def _guard(lock):
    return lock if lock is not None else nullcontext()


def _cancel_if_requested(cancelled):
    if cancelled is not None and cancelled():
        raise _CompressionCancelled()


def _limit_variable_chunk_cache(variable):
    """Bound a chunked variable's cache during bulk compression/verification.

    Classic NetCDF variables are contiguous and do not support this setting.
    Keep this local to the compression operation; normal interactive result
    reads retain netCDF4's usual cache behavior.
    """
    chunking = variable.chunking()
    if chunking is None or chunking == "contiguous":
        return
    variable.set_var_chunk_cache(
        size=_TARGET_VARIABLE_CACHE_BYTES,
        nelems=_TARGET_VARIABLE_CACHE_SLOTS,
        preemption=0.75,
    )


def _copy_dataset(source, destination, *, lock, cancelled):
    src = dst = None
    try:
        with _guard(lock):
            src = Dataset(str(source), "r")
            if src.data_model not in _CLASSIC_MODELS:
                return "unsupported", f"source format {src.data_model} is not classic"
            globals_ = {name: src.getncattr(name) for name in src.ncattrs()}
            dimensions = [(name, len(dim), dim.isunlimited())
                          for name, dim in src.dimensions.items()]
            variable_names = list(src.variables)
            schema = {}
            for name in variable_names:
                var = src.variables[name]
                _limit_variable_chunk_cache(var)
                schema[name] = {
                    "dimensions": tuple(var.dimensions),
                    "shape": tuple(var.shape),
                    "dtype": var.dtype,
                    "attributes": {attr: var.getncattr(attr) for attr in var.ncattrs()},
                }
            dst = Dataset(str(destination), "w", format="NETCDF4_CLASSIC")
            for name, value in globals_.items():
                dst.setncattr(name, value)
            for name, length, unlimited in dimensions:
                dst.createDimension(name, None if unlimited else length)
            for name in variable_names:
                _cancel_if_requested(cancelled)
                info = schema[name]
                attributes = info["attributes"]
                kwargs = {}
                if "_FillValue" in attributes:
                    kwargs["fill_value"] = attributes["_FillValue"]
                if info["shape"]:
                    chunks = compression_chunksizes(info["dimensions"], info["shape"], info["dtype"])
                    kwargs.update(zlib=True, complevel=3, shuffle=True, chunksizes=chunks)
                out = dst.createVariable(name, info["dtype"], info["dimensions"], **kwargs)
                _limit_variable_chunk_cache(out)
                for attr, value in attributes.items():
                    if attr != "_FillValue":
                        out.setncattr(attr, value)

        for name in variable_names:
            _cancel_if_requested(cancelled)
            info = schema[name]
            _limit_variable_chunk_cache(src.variables[name])
            _limit_variable_chunk_cache(dst.variables[name])
            shape = info["shape"]
            chunks = compression_chunksizes(info["dimensions"], shape, info["dtype"])
            for block in _block_slices(shape, chunks):
                _cancel_if_requested(cancelled)
                with _guard(lock):
                    values = src.variables[name][block]
                    dst.variables[name][block] = values
        return "copied", None
    finally:
        if dst is not None:
            with _guard(lock):
                dst.close()
        if src is not None:
            with _guard(lock):
                src.close()


def _verify_dataset(source, destination, *, lock, cancelled):
    src = dst = None
    try:
        with _guard(lock):
            src, dst = Dataset(str(source), "r"), Dataset(str(destination), "r")
            if dst.data_model != "NETCDF4_CLASSIC":
                raise ValueError("compressed file is not NETCDF4_CLASSIC")
            if list(src.dimensions) != list(dst.dimensions):
                raise ValueError("dimension names or order changed")
            if list(src.variables) != list(dst.variables):
                raise ValueError("variable names or order changed")
            if set(src.ncattrs()) != set(dst.ncattrs()):
                raise ValueError("global attribute names changed")
            for attr in src.ncattrs():
                if not _attribute_equal(src.getncattr(attr), dst.getncattr(attr)):
                    raise ValueError(f"global attribute changed: {attr}")
            dimensions = [(name, len(dim), dim.isunlimited())
                          for name, dim in src.dimensions.items()]
            other_dimensions = [(name, len(dim), dim.isunlimited())
                                for name, dim in dst.dimensions.items()]
            if dimensions != other_dimensions:
                raise ValueError("dimension lengths or unlimited flags changed")
            variable_names = list(src.variables)
            schema = {}
            for name in variable_names:
                left, right = src.variables[name], dst.variables[name]
                _limit_variable_chunk_cache(left)
                _limit_variable_chunk_cache(right)
                if (left.dimensions, left.shape, left.dtype) != (right.dimensions, right.shape, right.dtype):
                    raise ValueError(f"variable schema changed: {name}")
                left_attrs, right_attrs = set(left.ncattrs()), set(right.ncattrs())
                if left_attrs != right_attrs:
                    raise ValueError(f"variable attributes changed: {name}")
                for attr in left_attrs:
                    if not _attribute_equal(left.getncattr(attr), right.getncattr(attr)):
                        raise ValueError(f"variable attribute changed: {name}.{attr}")
                schema[name] = (tuple(left.shape), compression_chunksizes(
                    left.dimensions, left.shape, left.dtype))

        for name in variable_names:
            _cancel_if_requested(cancelled)
            shape, chunks = schema[name]
            for block in _block_slices(shape, chunks):
                _cancel_if_requested(cancelled)
                with _guard(lock):
                    if not _values_equal(src.variables[name][block], dst.variables[name][block]):
                        raise ValueError(f"data values or mask changed: {name}")
        return True
    finally:
        if dst is not None:
            with _guard(lock):
                dst.close()
        if src is not None:
            with _guard(lock):
                src.close()


def compress_netcdf_file(path, *, cancelled=None, lock=None):
    """Atomically replace a classic result with verified lossless compression.

    The source remains in place until the compressed sibling has passed a full
    block-by-block schema, attribute, mask, and value comparison. Any error or
    cancellation removes only the staging file and leaves the source untouched.
    """
    path = Path(path)
    started = time.perf_counter()
    if not path.is_file():
        return {"status": "failed", "error": "source file does not exist",
                "elapsed_seconds": time.perf_counter() - started}
    original_bytes = path.stat().st_size
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".compress.tmp",
                                     dir=path.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        status, reason = _copy_dataset(path, temp, lock=lock, cancelled=cancelled)
        if status == "unsupported":
            return {"status": "skipped", "error": reason, "original_bytes": original_bytes,
                    "elapsed_seconds": time.perf_counter() - started}
        _cancel_if_requested(cancelled)
        _verify_dataset(path, temp, lock=lock, cancelled=cancelled)
        compressed_bytes = temp.stat().st_size
        if compressed_bytes >= original_bytes:
            return {"status": "not_smaller", "original_bytes": original_bytes,
                    "compressed_bytes": compressed_bytes,
                    "elapsed_seconds": time.perf_counter() - started}
        source_stat = path.stat()
        if os.name != "nt":
            os.chmod(temp, source_stat.st_mode)
        os.utime(temp, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
        with _guard(lock):
            _cancel_if_requested(cancelled)
            os.replace(temp, path)
        if os.name == "nt":
            try:
                os.chmod(path, source_stat.st_mode)
            except OSError:
                pass
        return {"status": "compressed", "original_bytes": original_bytes,
                "compressed_bytes": compressed_bytes,
                "elapsed_seconds": time.perf_counter() - started}
    except _CompressionCancelled:
        return {"status": "cancelled", "original_bytes": original_bytes,
                "elapsed_seconds": time.perf_counter() - started}
    except Exception as error:
        try:
            staged_bytes = temp.stat().st_size if temp.exists() else None
        except OSError:
            staged_bytes = None
        return {"status": "failed", "original_bytes": original_bytes,
                "compressed_bytes": staged_bytes,
                "error": str(error), "elapsed_seconds": time.perf_counter() - started}
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
