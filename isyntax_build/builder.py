import os
from importlib import resources
from pathlib import Path

from cffi import FFI

import isyntax_build

cdef_extra = """
extern "Python" {
    bool python_file_set_pos(int, int64_t);
    int64_t python_file_read_into(int, void*, size_t);
    int64_t python_file_get_size(int);
    void python_file_close(int);
}

void free(void *ptr);
"""


def paths_to_strings(*paths: Path) -> list[str]:
    return [str(path) for path in paths]


def create_ffibuilder() -> FFI:
    ffibuilder = FFI()

    project_dir = Path(__file__).parent.parent

    vendor = project_dir/"isyntax_build"/"vendor"
    src = project_dir/"isyntax_build"/"src"
    libisyntax_src = vendor/"libisyntax"/"src"

    if os.name == "nt":
        platform_sources = [
            src/"win32_utils.c",
        ]
        extra_compile_args = ["/std:c11"]
        libraries = ["winmm"]
    else:
        platform_sources = []
        extra_compile_args = []
        libraries = []

    ffibuilder.set_source(
        "isyntax._pyisyntax",
        resources.read_text(isyntax_build, "pyisyntax.c"),
        sources=paths_to_strings(
            libisyntax_src/"libisyntax.c",
            libisyntax_src/"isyntax"/"isyntax.c",
            libisyntax_src/"isyntax"/"isyntax_reader.c",
            libisyntax_src/"utils"/"timerutils.c",
            libisyntax_src/"utils"/"block_allocator.c",
            libisyntax_src/"utils"/"benaphore.c",
            libisyntax_src/"platform"/"platform.c",
            libisyntax_src/"platform"/"work_queue.c",
            libisyntax_src/"third_party"/"yxml.c",
            libisyntax_src/"third_party"/"ltalloc.cc",
            src/"python_platform_utils.c",
            *platform_sources,
        ),
        include_dirs=paths_to_strings(
            libisyntax_src,
            libisyntax_src/"isyntax",
            libisyntax_src/"platform",
            libisyntax_src/"third_party",
            libisyntax_src/"utils",
            src,
        ),
        extra_compile_args=extra_compile_args,
        libraries=libraries,
    )

    header_lines = []
    with (libisyntax_src/"libisyntax.h").open() as f:
        for line in f:
            if line.startswith("#"):
                continue
            header_lines.append(line)
    header_lines.append("\n")
    with (src/"python_platform_utils.h").open() as f:
        for line in f:
            if line.startswith("#"):
                continue
            header_lines.append(line)
    header_text = "".join(header_lines)
    header_text += "\n\n"
    header_text += cdef_extra

    ffibuilder.cdef(header_text)

    return ffibuilder


ffibuilder = create_ffibuilder()

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
