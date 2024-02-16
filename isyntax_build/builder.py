import platform
from importlib import resources
from pathlib import Path

from cffi import FFI

import isyntax_build


def paths_to_strings(*paths: Path) -> list[str]:
    return [str(path) for path in paths]


def create_ffibuilder() -> FFI:
    ffibuilder = FFI()

    with resources.path(isyntax_build, "vendor") as vendor:
        libisyntax_src = vendor/"libisyntax"/"src"

        if platform.system() == "Windows":
            platform_sources = [
                libisyntax_src/"platform"/"win32_utils.c",
            ]
        else:
            platform_sources = [
                libisyntax_src/"platform"/"linux_utils.c",
            ]

        ffibuilder.set_source(
            "_pyisyntax",
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
                *platform_sources,
            ),
            include_dirs=paths_to_strings(
                libisyntax_src,
                libisyntax_src/"isyntax",
                libisyntax_src/"platform",
                libisyntax_src/"third_party",
                libisyntax_src/"utils",
            ),
        )

        header_lines = []
        with (libisyntax_src/"libisyntax.h").open() as f:
            for line in f:
                if line.startswith("#"):
                    continue
                header_lines.append(line)
        header_text = "".join(header_lines)

        ffibuilder.cdef(header_text)

    return ffibuilder


ffibuilder = create_ffibuilder()

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
