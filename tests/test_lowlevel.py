from collections.abc import Iterator
from pathlib import Path

import pytest

from isyntax.lowlevel import libisyntax
from isyntax.lowlevel.libisyntax import (
    ISyntaxCachePtr,
    ISyntaxImagePtr,
    ISyntaxLevelPtr,
    ISyntaxPtr,
    LibISyntaxFatalError,
)


@pytest.fixture()
def isyntax(sample_isyntax_file: Path) -> Iterator[ISyntaxPtr]:
    isyntax = libisyntax.open(str(sample_isyntax_file))
    yield isyntax
    libisyntax.close(isyntax)


@pytest.fixture()
def wsi_image(isyntax: ISyntaxPtr) -> ISyntaxImagePtr:
    return libisyntax.get_image(isyntax, 0)


@pytest.fixture()
def level4(wsi_image: ISyntaxImagePtr) -> ISyntaxLevelPtr:
    return libisyntax.image_get_level(wsi_image, 4)


@pytest.fixture()
def isyntax_cache(isyntax: ISyntaxPtr) -> Iterator[ISyntaxCachePtr]:
    isyntax_cache = libisyntax.cache_create("fixture_cache", 2000)
    libisyntax.cache_inject(isyntax_cache, isyntax)
    yield isyntax_cache
    libisyntax.cache_destroy(isyntax_cache)


def test_libisyntax_open_and_close(sample_isyntax_file: Path) -> None:
    isyntax = libisyntax.open(str(sample_isyntax_file))
    libisyntax.close(isyntax)


def test_libisyntax_open_nonexistent_file() -> None:
    with pytest.raises(LibISyntaxFatalError):
        libisyntax.open("this_file_does_not_exist.isyntax")


def test_libisyntax_get_tile_width(isyntax: ISyntaxPtr) -> None:
    expected = 256
    assert libisyntax.get_tile_width(isyntax) == expected


def test_libisyntax_get_tile_height(isyntax: ISyntaxPtr) -> None:
    expected = 256
    assert libisyntax.get_tile_height(isyntax) == expected


def test_libisyntax_get_wsi_image_index(isyntax: ISyntaxPtr) -> None:
    assert libisyntax.get_wsi_image_index(isyntax) == 0


def test_libisyntax_image_get_level_count(wsi_image: ISyntaxImagePtr) -> None:
    expected = 8
    assert libisyntax.image_get_level_count(wsi_image) == expected


def test_libisyntax_level_get_scale(level4: ISyntaxLevelPtr) -> None:
    expected = 4
    assert libisyntax.level_get_scale(level4) == expected


def test_libisyntax_level_get_width_in_tiles(level4: ISyntaxLevelPtr) -> None:
    expected = 16
    assert libisyntax.level_get_width_in_tiles(level4) == expected


def test_libisyntax_level_get_height_in_tiles(level4: ISyntaxLevelPtr) -> None:
    expected = 24
    assert libisyntax.level_get_height_in_tiles(level4) == expected


def test_libisyntax_level_get_width(level4: ISyntaxLevelPtr) -> None:
    expected = 2336
    assert libisyntax.level_get_width(level4) == expected


def test_libisyntax_level_get_height(level4: ISyntaxLevelPtr) -> None:
    expected = 4576
    assert libisyntax.level_get_height(level4) == expected


def test_libisyntax_level_get_mpp_x(level4: ISyntaxLevelPtr) -> None:
    expected = 4.0
    assert libisyntax.level_get_mpp_x(level4) == expected


def test_libisyntax_level_get_mpp_y(level4: ISyntaxLevelPtr) -> None:
    expected = 4.0
    assert libisyntax.level_get_mpp_y(level4) == expected


def test_libisyntax_cache_create_destroy() -> None:
    isyntax_cache = libisyntax.cache_create("test_cache", 2000)
    libisyntax.cache_destroy(isyntax_cache)


def test_libisyntax_tile_read(isyntax: ISyntaxPtr, isyntax_cache: ISyntaxCachePtr) -> None:
    rgba = bytearray(256 * 256 * 4)
    libisyntax.tile_read(
        isyntax, isyntax_cache, 7, 0, 0, rgba, libisyntax.ISyntaxPixelFormat.RGBA)
    x = 97
    y = 45
    pos = 256 * 4 * y + 4 * x
    actual = tuple(rgba[pos:pos + 4])
    expected = (145, 108, 87, 255)
    assert actual == expected


def test_libisyntax_read_region(isyntax: ISyntaxPtr, isyntax_cache: ISyntaxCachePtr) -> None:
    rgba = bytearray(4)
    libisyntax.read_region(
        isyntax, isyntax_cache, 4, 500, 500, 1, 1, rgba, libisyntax.ISyntaxPixelFormat.RGBA)
    actual = tuple(rgba)
    expected = (226, 226, 229, 255)
    assert actual == expected
