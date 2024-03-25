# pyisyntax

A Python library for working with pathology images in the iSyntax file format,
powered by [libisyntax](https://github.com/amspath/libisyntax).

## Installation

```console
$ pip install pyisyntax
```

## Usage

Read and display a region of the WSI via
[Pillow](https://pillow.readthedocs.io/).

```python
from isyntax import ISyntax
import PIL.Image

with ISyntax.open("my_file.isyntax") as isyntax:
    # Read pixels from the specified region into a numpy array
    pixels = isyntax.read_region(500, 500, 400, 200, level=4)
    # Convert numpy array into a PIL image
    pil_image = PIL.Image.fromarray(pixels)
    # Show the image
    pil_image.show()
```

Extract and save the associated macro image.

```python
from isyntax import ISyntax

with ISyntax.open("my_file.isyntax") as isyntax:
    # The macro image will be returned as compressed JPEG data.
    jpeg_data = isyntax.read_macro_image_jpeg()
    # This JPEG data can be written directly to a file.
    with open("macro_image.jpg", "wb") as f:
        f.write(jpeg_data)
    # Alternatively, you could decompress the data using Pillow:
    # pil_image = PIL.Image.open(io.BytesIO(jpeg_data), formats=["JPEG"])
```

## Development

### Dependency management

To set up a development environment from the lock file:

1. Ensure that you have
   [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)
   installed.
2. Create the environment:
   ```console
   $ micromamba create -n pyisyntax -f conda-lock.yml --category main --category dev
   ```
3. Activate the environment:
   ```console
   $ micromamba activate pyisyntax
   ```

To modify pyisyntax project dependencies:

1. Edit pyproject.toml.
2. Update the lock file using conda-lock:
   ```console
   $ conda-lock lock -f pyproject.toml -p linux-64 --micromamba
   ```
