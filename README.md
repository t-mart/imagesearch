# imagesearch

![PyPI](https://img.shields.io/pypi/v/imagesearch)
![Build](https://github.com/t-mart/imagesearch/workflows/Build/badge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/t-mart/imagesearch/badge.svg?branch=master)](
https://coveralls.io/github/t-mart/imagesearch?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imagesearch)

`imagesearch` performs visual comparison operations on images.

The `compare` command measures visual similiarity between a reference image and a set of other
images. This can be used to search for a similar image that you know among a deep directory
structure of images that you don't want to manually scan.

The `dupe` command finds images which have identical visual fingerprints in a search path. This
can be used to identify images which you can delete later.

## Installation

    pip install imagesearch

See [imagesearch on PyPI](https://pypi.org/project/imagesearch/).

## Examples

- Get help:

        > imagesearch --help
        ...

## Commands

`imagesearch` functionality is broken up into subcommands provided on the command line.

While the subcommands may have unique arguments, others are common among them:

- Algorithm arguments, which specify which fingerprint algorithm to use. For help in choosing, see
  the section below. For example, to use "average hashing", specify `--ahash`. **If no algorithm is
  specified, `--dhash` is implied.**

  - These algorithms can take in additional parameters to tune their performance. See the help
    output for what these parameters are. They should be given in a comma-separated list, joining
    each argument name to its value with an equals sign. For example:

    ```
    > imagesearch dupe images/ --whash --algo-params hash_size=8,mode=db4
    > imagesearch dupe --help  # for more detail
    ```

- `-f`/`-format` specifies the output format of results. This can be either `text` or `json` (the
  default). `json` should be used when the results are to be read by another program because
  eccentricities in filenames will be properly encoded. _(All examples below use `text` for
  clarity.)_

### `search` Command

**A `0` value indicates the highest level of similarity, or possibly a true match.**

- Compare a reference image to all images in a search path:

        > imagesearch search needle.jpg haystack\ --format text
        28      haystack\0.jpg
        38      haystack\1.jpg
        12      haystack\2.jpg
        18      haystack\3.jpg
        32      haystack\4.jpg
        29      haystack\5.jpg
        0       haystack\6.jpg
        29      haystack\7.jpg
        5       haystack\8.jpg
        28      haystack\9.jpg

    In this example, `haystack\6.jpg` is most similar.

- Compare against a single image:

        > imagesearch search needle.jpg haystack\1.jpg --format text
        38       haystack\1.jpg

- Only return images with similarity less than or equal to 10:

        > imagesearch search needle.jpg haystack\ --threshold 10 --format text
        0       haystack\6.jpg
        5       haystack\8.jpg

- Return the first image found under the threshold (0, in this case) and stop searching immediately:

        > imagesearch search needle.jpg haystack\ -t 0 --stop-on-first-match --format text
        0       haystack\6.jpg

- Specify a different algorithm:

        > imagesearch search needle.jpg haystack\ --colorhash --format text
        ...

- Get more help:

        > imagesearch search --help
        ...

### `dupe` Command

- Find all visually similar images in a search path:

        > imagesearch dupe images\ --format text
        fff7db9f03030203
                images\file-123.jpg
                images\deep\subdir\foo.jpeg
        fcf8f0fae2c6c400
                images\a\file-987.jpg
                images\subdir\bar.png

    Each set of paths that are similar is prefixed with its hash.

- Get more help:

        > imagesearch dupe --help
        ...

## Visual Similiarity

At its core, `imagesearch` creates image fingerprints and compares them to other fingerprints. A
critical feature of these fingerprints is that they can be numerically compared. **Images that are
different will have large differences in their fingerprints, and vice versa.**

Unless you have a good understanding of the algorihms used, values should be treated as opaque and
subjective. It is dependent on the algorithm used to create the fingerprints and your criteria for
what "similar" is.

This project uses the
[imagehash](https://github.com/JohannesBuchner/imagehash) library to produce these fingerprints, and
more information about the techniques can be found there.

## Algorithms

All the fingerprinting algorithms in `imagesearch` come from
[imagehash](https://github.com/JohannesBuchner/imagehash). In `imagesearch`, you may specify which
algorithm to use by giving an argument in one of the following forms:

- `--ahash`: Average hashing (aHash)
- `--phash`: 2-axis perceptual hashing (pHash)
- `--phash-simple`: 1-axis perceptual hashing (pHash)
- `--dhash`: Horizontal difference hashing (dHash)
- `--dhash-vert`: Vertical difference hashing (dHash)
- `--whash`: Wavelet hashing (wHash), can specify either Haar (`mode=haar`) or Daubechies
  (`mode=db4`)
- `--colorhash`: HSV color hashing (colorhash)

## Collisions
These algorithms trade away accuracy for speed and size, usually with acceptable results. Instead of
producing an artifact that exactly identifies an image, there's analysis done on some more abstract
quality of the image, such as it's luminance or
[signal frequency](https://en.wikipedia.org/wiki/Discrete_cosine_transform). This allows us
to:
- do less processing
- get a fingerprint with a small size
- get a fingerprint that exists in a linear space for comparison

However, because the exact image analysis is abstract and produces a fixed-size fingerprint, it's
absolutely possible for 2 different images to have the same fingerprint.

This is sort of an analog to cryptographic hash collosions, so it's important to understand what
kinds of scenarios may cause this!

See
[this section of the imagehash documentation](
https://github.com/JohannesBuchner/imagehash#example-results) for examples of different images that
produce the same fingerprint. The source code of that project also references other pages that
explain the workings of the algorithm.

### Tuning
If you notice collisions for images you expect to hash differently, try changing the algorithm
parameters. One easy way to do this is to increase the hash size, done for example by:

```
imagesearch dupe images/ --dhash --algo-params hash_size=16
```

See the subcommand help for more details and any constraints that may be on the value.

# Contributing

## Features TODO

- whitelist file paths by extension (currently tries to open every file in the path, which
  hurts for directories with other big files in them. Not sure if `PIL.Image.open` is smart enough
  to failfast on unknown data.) Something like `--ext .jpg --ext .png --ext .jpeg`.
  - set whitelist of popular extensions with something like `--only-popular-extensions`.
- asyncio for reading? look at `aiofile` project and Image.open(BytesIO(...data...)). Would this
  even help though? Is there harddisk read parallelism to leverage?
- algorithm parameter parsing uses it's own little sublanguage (comma-separated key=value pairs).
  This could be a first-order argparse task instead. Would have to inspect each `Algorithm` and
  auto-generate acceptable arguments. `argparse.ArgumentParser` has a nice `parse_known_args`
  method that could chomp away at non-algorithm-specific arguments first, and then parse
  algorithm-specific ones once the algorithm is known. How would we generate help text for this
  though?

## Bug Fixes/Features

Submit a PR from an appropriately named feature branch off of master.

## Releasing

1. Bump the version with `poetry run bumpversion [patch|minor|major]`. This will update the version
number around the project, commit and tag it.
2. Push the repo. A Github release will be made and published to PyPI.
