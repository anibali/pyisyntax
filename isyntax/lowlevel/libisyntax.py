import os
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, NewType

from isyntax._pyisyntax import ffi, lib
from isyntax.lowlevel.io_management import init_python_io_hooks, register_io

if TYPE_CHECKING:
    from cffi import FFI
    from typing_extensions import Buffer


Pointer = NewType("Pointer", "FFI.CData")
ISyntaxPtr = NewType("ISyntaxPtr", Pointer)
ISyntaxImagePtr = NewType("ISyntaxImagePtr", Pointer)
ISyntaxLevelPtr = NewType("ISyntaxLevelPtr", Pointer)
ISyntaxCachePtr = NewType("ISyntaxCachePtr", Pointer)


LIBISYNTAX_OK = 0
# Generic error that the user should not expect to recover from.
LIBISYNTAX_FATAL = 1
# One of the arguments passed to a function is invalid.
LIBISYNTAX_INVALID_ARGUMENT = 2


class ISyntaxPixelFormat(IntEnum):
    RGBA = lib.LIBISYNTAX_PIXEL_FORMAT_RGBA
    BGRA = lib.LIBISYNTAX_PIXEL_FORMAT_BGRA


class LibISyntaxError(Exception):
    pass


class LibISyntaxFatalError(LibISyntaxError):
    pass


class LibISyntaxInvalidArgumentError(LibISyntaxError):
    pass


class LibISyntaxUnknownError(LibISyntaxError):
    pass


class NullPointerError(Exception):
    pass


def check_error(status: int) -> None:
    if status == LIBISYNTAX_OK:
        return
    if status == LIBISYNTAX_FATAL:
        raise LibISyntaxFatalError
    if status == LIBISYNTAX_INVALID_ARGUMENT:
        raise LibISyntaxInvalidArgumentError
    raise LibISyntaxUnknownError


def free(ptr: Pointer) -> None:
    lib.free(ptr)


def _do_init() -> None:
    check_error(lib.libisyntax_init())
    init_python_io_hooks()


def init() -> None:
    ffi.init_once(_do_init, "libisyntax_init")


def open_from_registered_handle(handle: int, *, is_init_allocators: bool = False) -> ISyntaxPtr:
    init()

    isyntax = ffi.new("isyntax_t**")
    check_error(lib.libisyntax_open(
        ffi.new("char[]", str(handle).encode("utf-8")),
        is_init_allocators,
        isyntax,
    ))
    return isyntax[0]


def open_from_filename(filename: str | Path, *, is_init_allocators: bool = False) -> ISyntaxPtr:
    filename = Path(filename)
    f = filename.open("rb")
    handle = register_io(f, os.fstat(f.fileno()).st_size)
    return open_from_registered_handle(handle, is_init_allocators=is_init_allocators)


def close(isyntax: ISyntaxPtr) -> None:
    # If a null pointer gets through the program will segfault.
    if isyntax == ffi.NULL:
        raise NullPointerError
    lib.libisyntax_close(isyntax)


def get_tile_width(isyntax: ISyntaxPtr) -> int:
    return lib.libisyntax_get_tile_width(isyntax)


def get_tile_height(isyntax: ISyntaxPtr) -> int:
    return lib.libisyntax_get_tile_height(isyntax)


def get_wsi_image(isyntax: ISyntaxPtr) -> ISyntaxImagePtr:
    return lib.libisyntax_get_wsi_image(isyntax)


def get_label_image(isyntax: ISyntaxPtr) -> ISyntaxImagePtr:
    return lib.libisyntax_get_label_image(isyntax)


def get_macro_image(isyntax: ISyntaxPtr) -> ISyntaxImagePtr:
    return lib.libisyntax_get_macro_image(isyntax)


def image_get_level_count(wsi_image: ISyntaxImagePtr) -> int:
    return lib.libisyntax_image_get_level_count(wsi_image)


def image_get_level(wsi_image: ISyntaxImagePtr, index: int) -> ISyntaxLevelPtr:
    return lib.libisyntax_image_get_level(wsi_image, index)


def level_get_scale(level: ISyntaxLevelPtr) -> int:
    return lib.libisyntax_level_get_scale(level)


def level_get_width_in_tiles(level: ISyntaxLevelPtr) -> int:
    return lib.libisyntax_level_get_width_in_tiles(level)


def level_get_height_in_tiles(level: ISyntaxLevelPtr) -> int:
    return lib.libisyntax_level_get_height_in_tiles(level)


def level_get_width(level: ISyntaxLevelPtr) -> int:
    return lib.libisyntax_level_get_width(level)


def level_get_height(level: ISyntaxLevelPtr) -> int:
    return lib.libisyntax_level_get_height(level)


def level_get_mpp_x(level: ISyntaxLevelPtr) -> float:
    return lib.libisyntax_level_get_mpp_x(level)


def level_get_mpp_y(level: ISyntaxLevelPtr) -> float:
    return lib.libisyntax_level_get_mpp_y(level)


def cache_create(debug_name: str | None, cache_size: int) -> ISyntaxCachePtr:
    isyntax_cache = ffi.new("isyntax_cache_t**")
    if debug_name is None:
        debug_name_or_null = ffi.NULL
    else:
        debug_name_or_null = ffi.new("char[]", debug_name.encode("utf-8"))
    check_error(lib.libisyntax_cache_create(
        debug_name_or_null,
        cache_size,
        isyntax_cache,
    ))
    return isyntax_cache[0]


def cache_inject(isyntax_cache: ISyntaxCachePtr, isyntax: ISyntaxPtr) -> None:
    check_error(lib.libisyntax_cache_inject(isyntax_cache, isyntax))


def cache_destroy(isyntax_cache: ISyntaxCachePtr) -> None:
    if isyntax_cache == ffi.NULL:
        raise NullPointerError
    lib.libisyntax_cache_destroy(isyntax_cache)


def tile_read(
    isyntax: ISyntaxPtr,
    isyntax_cache: ISyntaxCachePtr,
    level: int,
    tile_x: int,
    tile_y: int,
    pixels_buffer: "Buffer | FFI.buffer",
    pixel_format: ISyntaxPixelFormat,
) -> None:
    check_error(lib.libisyntax_tile_read(
        isyntax,
        isyntax_cache,
        level,
        tile_x,
        tile_y,
        ffi.from_buffer("uint32_t[]", pixels_buffer, require_writable=True),
        pixel_format,
    ))


def read_region(
    isyntax: ISyntaxPtr,
    isyntax_cache: ISyntaxCachePtr,
    level: int,
    x: int,
    y: int,
    width: int,
    height: int,
    pixels_buffer: "Buffer | FFI.buffer",
    pixel_format: ISyntaxPixelFormat,
) -> None:
    check_error(lib.libisyntax_read_region(
        isyntax,
        isyntax_cache,
        level,
        x,
        y,
        width,
        height,
        ffi.from_buffer("uint32_t[]", pixels_buffer, require_writable=True),
        pixel_format,
    ))


def read_label_image_jpeg(isyntax: ISyntaxPtr) -> memoryview:
    jpeg_buffer_ptr = ffi.new("uint8_t**")
    jpeg_size_ptr = ffi.new("uint32_t*")
    check_error(lib.libisyntax_read_label_image_jpeg(
        isyntax,
        jpeg_buffer_ptr,
        jpeg_size_ptr,
    ))
    jpeg_buffer = ffi.gc(jpeg_buffer_ptr[0], free)
    jpeg_size = jpeg_size_ptr[0]
    return memoryview(ffi.buffer(jpeg_buffer, jpeg_size))


def read_macro_image_jpeg(isyntax: ISyntaxPtr) -> memoryview:
    jpeg_buffer_ptr = ffi.new("uint8_t**")
    jpeg_size_ptr = ffi.new("uint32_t*")
    check_error(lib.libisyntax_read_macro_image_jpeg(
        isyntax,
        jpeg_buffer_ptr,
        jpeg_size_ptr,
    ))
    jpeg_buffer = ffi.gc(jpeg_buffer_ptr[0], free)
    jpeg_size = jpeg_size_ptr[0]
    return memoryview(ffi.buffer(jpeg_buffer, jpeg_size))


def read_icc_profile(isyntax: ISyntaxPtr, image: ISyntaxImagePtr) -> memoryview:
    profile_buffer_ptr = ffi.new("uint8_t**")
    profile_size_ptr = ffi.new("uint32_t*")
    check_error(lib.libisyntax_read_icc_profile(
        isyntax,
        image,
        profile_buffer_ptr,
        profile_size_ptr,
    ))
    profile_buffer = ffi.gc(profile_buffer_ptr[0], free)
    profile_size = profile_size_ptr[0]
    return memoryview(ffi.buffer(profile_buffer, profile_size))
