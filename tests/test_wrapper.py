from collections.abc import Iterator
from pathlib import Path

import pytest

from isyntax.wrapper import ISyntax


class TestISyntax:
    @pytest.fixture()
    def isyntax(self, sample_isyntax_file: Path) -> Iterator[ISyntax]:
        with ISyntax.open(sample_isyntax_file) as isyntax:
            yield isyntax

    def test_tile_width(self, isyntax: ISyntax) -> None:
        expected = 256
        assert isyntax.tile_width == expected

    def test_tile_height(self, isyntax: ISyntax) -> None:
        expected = 256
        assert isyntax.tile_height == expected

    def test_wsi_index(self, isyntax: ISyntax) -> None:
        expected = 0
        assert isyntax.wsi_index == expected

    def test_level_count(self, isyntax: ISyntax) -> None:
        expected = 8
        assert isyntax.level_count == expected

    def test_dimensions(self, isyntax: ISyntax) -> None:
        expected = (37382, 73222)
        assert isyntax.dimensions == expected

    def test_level_dimensions(self, isyntax: ISyntax) -> None:
        expected = [
            (37382, 73222),
            (18691, 36611),
            (9345, 18305),
            (4672, 9152),
            (2336, 4576),
            (1168, 2288),
            (584, 1144),
            (292, 572),
        ]
        assert isyntax.level_dimensions == expected

    def test_level_tiles(self, isyntax: ISyntax) -> None:
        expected = [
            (256, 384),
            (128, 192),
            (64, 96),
            (32, 48),
            (16, 24),
            (8, 12),
            (4, 6),
            (2, 3),
        ]
        assert isyntax.level_tiles == expected

    def test_level_downsamples(self, isyntax: ISyntax) -> None:
        expected = [1, 2, 4, 8, 16, 32, 64, 128]
        assert isyntax.level_downsamples == expected

    def test_mpp_x(self, isyntax: ISyntax) -> None:
        expected = 0.25
        assert isyntax.mpp_x == expected

    def test_mpp_y(self, isyntax: ISyntax) -> None:
        expected = 0.25
        assert isyntax.mpp_y == expected

    def test_read_tile(self, isyntax: ISyntax) -> None:
        rgba = isyntax.read_tile(0, 0, level=7)
        x = 97
        y = 45
        actual = tuple(rgba[y, x])
        expected = (145, 108, 87, 255)
        assert actual == expected

    def test_read_region(self, isyntax: ISyntax) -> None:
        rgba = isyntax.read_region(500, 500, 1, 1, level=4)
        actual = tuple(rgba[0, 0])
        expected = (226, 226, 229, 255)
        assert actual == expected
