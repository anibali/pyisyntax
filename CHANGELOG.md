# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2025-04-18

### Added

- Properties `offset_x`and `offset_y` for the WSI image offset in relation to the macro image.

### Changed

- Bump the `libisyntax` submodule commit.
- Use `uv` for development environment management (was previously `conda-lock`).

## [0.1.4] - 2024-08-31

### Added

- Support for reading the slide barcode. The barcode string can be accessed via
  the `barcode` property of an `ISyntax` instance.

### Changed

- Bump the `libisyntax` submodule commit.

## [0.1.3] - 2024-03-28

### Added

- This CHANGELOG file.

### Fixed

- Gracefully exit the contextmanager when an ISyntax file fails to open
  ([#8](https://github.com/anibali/pyisyntax/issues/8)).
- Release reference to the associated cache object when an ISyntax object is closed
  so that it can be garbage collected and destroyed
  ([#9](https://github.com/anibali/pyisyntax/issues/9)).

## [0.1.2] - 2024-03-25

### Added

- Configuration option to set the cache size
  ([#5](https://github.com/anibali/pyisyntax/issues/5)).

### Changed

- Nest the `_pyisyntax` binary library file under the `isyntax` top-level
  namespace.
- Bump the `libisyntax` submodule commit and match their API changes
  (thanks @erikogabrielsson).

## [0.1.1] - 2024-03-02

### Changed

- Return `None` when an associated image/colour profile is not present.
- Reduce the number of provided wheels by using `py_limited_api`.
  Multiple Python versions will continue being tested during CI through
  the use of `tox`.

## [0.1.0] - 2024-02-26

### Added

- This is the initial release.

[unreleased]: https://github.com/anibali/pyisyntax/compare/v0.1.5...HEAD
[0.1.4]: https://github.com/anibali/pyisyntax/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/anibali/pyisyntax/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/anibali/pyisyntax/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/anibali/pyisyntax/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/anibali/pyisyntax/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/anibali/pyisyntax/releases/tag/v0.1.0
