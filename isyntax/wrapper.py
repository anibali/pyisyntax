import os
from collections.abc import Iterator
from io import BufferedIOBase, RawIOBase
from pathlib import Path
from types import TracebackType

import numpy as np

from isyntax.lowlevel import libisyntax
from isyntax.lowlevel.io_management import register_io


class ISyntaxCache:
    def __init__(self, debug_name: str | None = None, cache_size: int = 2000) -> None:
        self.ptr = libisyntax.cache_create(debug_name, cache_size)
        self.destroyed = False

    def inject(self, isyntax: "ISyntax") -> None:
        libisyntax.cache_inject(self.ptr, isyntax.ptr)

    def destroy(self) -> None:
        libisyntax.cache_destroy(self.ptr)
        self.destroyed = True

    def __del__(self) -> None:
        if not self.destroyed:
            self.destroy()


class ISyntaxLevel:
    def __init__(self, ptr: libisyntax.ISyntaxLevelPtr) -> None:
        self.ptr = ptr

    @property
    def scale(self) -> int:
        return libisyntax.level_get_scale(self.ptr)

    @property
    def width_in_tiles(self) -> int:
        return libisyntax.level_get_width_in_tiles(self.ptr)

    @property
    def height_in_tiles(self) -> int:
        return libisyntax.level_get_height_in_tiles(self.ptr)

    @property
    def width(self) -> int:
        return libisyntax.level_get_width(self.ptr)

    @property
    def height(self) -> int:
        return libisyntax.level_get_height(self.ptr)

    @property
    def mpp_x(self) -> float:
        return libisyntax.level_get_mpp_x(self.ptr)

    @property
    def mpp_y(self) -> float:
        return libisyntax.level_get_mpp_y(self.ptr)


class ISyntaxImage:
    def __init__(self, ptr: libisyntax.ISyntaxImagePtr) -> None:
        self.ptr = ptr

    @property
    def level_count(self) -> int:
        return libisyntax.image_get_level_count(self.ptr)

    def get_level(self, level_index: int) -> ISyntaxLevel:
        return ISyntaxLevel(libisyntax.image_get_level(self.ptr, level_index))

    @property
    def levels(self) -> Iterator[ISyntaxLevel]:
        for i in range(self.level_count):
            yield self.get_level(i)


class ISyntax:
    def __init__(self, f: RawIOBase | BufferedIOBase, n_bytes: int, cache_size: int = 2000) -> None:
        self.io_handle = register_io(f, n_bytes)
        self.ptr = libisyntax.open_from_registered_handle(self.io_handle, is_init_allocators=False)
        self.closed = False
        self._cache_size = cache_size
        self._cache = None

    @classmethod
    def open(cls: type["ISyntax"], filename: str | Path, cache_size: int = 2000) -> "ISyntax":
        filename = Path(filename)
        f = filename.open("rb")
        n_bytes = os.fstat(f.fileno()).st_size
        return cls(f, n_bytes, cache_size)

    def close(self) -> None:
        if self.closed:
            return
        libisyntax.close(self.ptr)
        self.closed = True

    @property
    def tile_width(self) -> int:
        return libisyntax.get_tile_width(self.ptr)

    @property
    def tile_height(self) -> int:
        return libisyntax.get_tile_height(self.ptr)

    @property
    def wsi(self) -> ISyntaxImage:
        return ISyntaxImage(libisyntax.get_wsi_image(self.ptr))

    def get_cache(self) -> ISyntaxCache:
        if self._cache is None:
            self._cache = ISyntaxCache(cache_size=self._cache_size)
            self._cache.inject(self)
        return self._cache

    def read_tile(self, tile_x: int, tile_y: int, level: int = 0) -> np.ndarray:
        """Reads RGBA pixel data from the specified tile.

        Args:
            tile_x: Tile column.
            tile_y: Tile row.
            level: Level number. Defaults to 0.

        Returns:
            Region RGBA pixel data in a [tile_height, tile_width, 4] array.
        """
        cache = self.get_cache()
        buf = np.empty((self.tile_height, self.tile_width, 4), dtype=np.uint8)
        libisyntax.tile_read(self.ptr, cache.ptr, level, tile_x, tile_y,
            buf.data, libisyntax.ISyntaxPixelFormat.RGBA)
        return buf

    def read_region(self, x: int, y: int, width: int, height: int, level: int = 0) -> np.ndarray:
        """Reads RGBA pixel data from the specified region.

        Args:
            x: Left edge position of the region in the target level reference frame.
            y: Top edge position of the region in the target level reference frame.
            width: Width of the region.
            height: Height of the region.
            level: Level number. Defaults to 0.

        Returns:
            Region RGBA pixel data in a [height, width, 4] array.
        """
        cache = self.get_cache()
        buf = np.empty((height, width, 4), dtype=np.uint8)
        libisyntax.read_region(self.ptr, cache.ptr, level, x, y, width, height,
            buf.data, libisyntax.ISyntaxPixelFormat.RGBA)
        return buf

    def read_label_image_jpeg(self) -> memoryview | None:
        """Reads the associated label image as a JPEG-compressed image.

        Returns:
            Compressed JPEG image data, or None if it can't be read.
        """
        try:
            return libisyntax.read_label_image_jpeg(self.ptr)
        except libisyntax.LibISyntaxFatalError:
            return None

    def read_macro_image_jpeg(self) -> memoryview | None:
        """Reads the associated macro image as a JPEG-compressed image.

        Returns:
            Compressed JPEG image data, or None if it can't be read.
        """
        try:
            return libisyntax.read_macro_image_jpeg(self.ptr)
        except libisyntax.LibISyntaxFatalError:
            return None

    def read_icc_profile(self) -> memoryview | None:
        """Reads the ICC color profile for an image.

        Returns:
            The ICC color profile, or None if it can't be read.
        """
        try:
            return libisyntax.read_icc_profile(self.ptr, self.wsi.ptr)
        except libisyntax.LibISyntaxFatalError:
            return None

    @property
    def level_count(self) -> int:
        return self.wsi.level_count

    @property
    def dimensions(self) -> tuple[int, int]:
        level0 = self.wsi.get_level(0)
        return (level0.width, level0.height)

    @property
    def level_dimensions(self) -> list[tuple[int, int]]:
        return [(level.width, level.height) for level in self.wsi.levels]

    @property
    def level_downsamples(self) -> list[int]:
        return [1 << level.scale for level in self.wsi.levels]

    @property
    def level_tiles(self) -> list[tuple[int, int]]:
        return [(level.width_in_tiles, level.height_in_tiles) for level in self.wsi.levels]

    @property
    def mpp_x(self) -> float:
        level0 = self.wsi.get_level(0)
        return level0.mpp_x

    @property
    def mpp_y(self) -> float:
        level0 = self.wsi.get_level(0)
        return level0.mpp_y

    def __enter__(self) -> "ISyntax":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()
