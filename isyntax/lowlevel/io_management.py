from collections.abc import Iterator
from dataclasses import dataclass
from io import BufferedIOBase, RawIOBase
from typing import Generic, NewType, TypeVar

from isyntax._pyisyntax import ffi, lib

VoidPtr = NewType("VoidPtr", object)
T = TypeVar("T")


@dataclass
class SizedIO:
    #: The IO object.
    f: RawIOBase | BufferedIOBase
    #: The complete length of the IO object's data (in bytes).
    n_bytes: int


class ByHandleRegistry(Generic[T]):
    class _EmptySlot:
        pass

    def __init__(self) -> None:
        """Creates a registry of objects keyed by integer handles.

        Handles start at 1, autoincrement, and will automatically be recycled
        once objects are removed from the registry.
        """
        self._list = []
        self._n_free = 0
        self._empty_slot = self._EmptySlot()

    def pop(self, handle: int) -> T:
        element = self._list[handle - 1]
        self._list[handle - 1] = self._empty_slot
        self._n_free += 1
        if len(self._list) == handle:
            while len(self._list) > 0 and self._list[-1] is self._empty_slot:
                self._list.pop()
                self._n_free -= 1
        return element

    def add(self, element: T) -> int:
        if self._n_free == 0:
            self._list.append(element)
            return len(self._list)
        index = self._list.index(self._empty_slot)
        self._list[index] = element
        self._n_free -= 1
        # Handles start at 1.
        return index + 1

    def __getitem__(self, handle: int) -> T:
        return self._list[handle - 1]

    def items(self) -> Iterator[tuple[int, T]]:
        for i, element in enumerate(self._list):
            if element is not self._empty_slot:
                yield i + 1, element


_io_registry = ByHandleRegistry[SizedIO]()


def init_python_io_hooks() -> None:
    @ffi.def_extern()
    def python_file_set_pos(handle: int, offset: int) -> bool:
        _io_registry[handle].f.seek(offset)
        return True


    @ffi.def_extern()
    def python_file_read_into(handle: int, dest: VoidPtr, bytes_to_read: int) -> int:
        bytes_read = _io_registry[handle].f.readinto(ffi.buffer(dest, bytes_to_read))
        if bytes_read is None:
            raise RuntimeError
        return max(bytes_read, 1)


    @ffi.def_extern()
    def python_file_get_size(handle: int) -> int:
        return _io_registry[handle].n_bytes


    @ffi.def_extern()
    def python_file_close(handle: int) -> None:
        _io_registry.pop(handle).f.close()


    lib.init_python_platform_utils(
        lib.python_file_set_pos,
        lib.python_file_read_into,
        lib.python_file_get_size,
        lib.python_file_close,
    )


def register_io(f: RawIOBase | BufferedIOBase, n_bytes: int) -> int:
    """Registers a Python IO object for use with the underlying C library.

    Args:
        f: IO object to register.
        n_bytes: Size of the IO object's data (in bytes).

    Raises:
        RuntimeError: When the IO object is not readable.

    Returns:
        New handle assigned to the IO object.
    """
    if not f.readable:
        msg = "IO object must be readable"
        raise RuntimeError(msg)
    return _io_registry.add(SizedIO(f, n_bytes))
