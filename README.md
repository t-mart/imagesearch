# imagesearch

![Build](https://github.com/t-mart/imagesearch/workflows/Build/badge.svg?branch=master)

`imagesearch` measures visual similiarity between a reference image and a set of other
images. This can be used to search for a similar image in a large/deep directory structure.

## Installation

    pip install imagesearch

## Examples

- Compare a reference image to all images in a search path:

        > imagesearch needle.jpg haystack\
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

        > imagesearch needle.jpg haystack\1.jpg
        38       haystack\1.jpg

- Only return images with similarity less than or equal to 10:

        > imagesearch needle.jpg haystack\ --threshold 10
        0       haystack\6.jpg
        5       haystack\8.jpg

- Return the first image found under the threshold (0, in this case) and stop searching immediately:

        > imagesearch needle.jpg haystack\ -t 0 -1
        0       haystack\6.jpg

- Specify a different algorithm:

        > imagesearch needle.jpg haystack\ --algorithm colorhash
        ...

- Get more help:

        > imagesearch --help
        ...

## Visual Similiarity

`imagesearch` returns a nonnegative integer that quantifies the visual similarity between the
reference image and another image. It does this by creating an image fingerprint and looking at the
difference between them.

A critical feature of these fingerprints is that they can be numerically compared (by Hamming Distance).
Images that are different will have large differences in their fingerprints, and vice versa

**A `0` value indicates the highest level of similarity, or possibly a true match.**

Values should be treated as opaque and relative. It is dependent on the algorithm
used to create the fingerprints and your subjective criteria for what "similar" is.

This project uses the
[imagehash](https://github.com/JohannesBuchner/imagehash) library to produce these fingerprints, and
more information about the techniques can be found there.

## Algorithms

All the fingerprinting algorithms in `imagesearch` come from [imagehash](https://github.com/JohannesBuchner/imagehash). In `imagesearch`, you may specify which algorithm to use by passing the appropriate option value to the `-a` or `--algorithm` flag:

- `ahash`: Average hashing (aHash)
- `phash`: 2-axis perceptual hashing (pHash)
- `phash-simple`: 1-axis perceptual hashing (pHash)
- `dhash`: Horizontal difference hashing (dHash)
- `dhash-vert`: Vertical difference hashing (dHash)
- `whash-haar`: Haar wavelet hashing (wHash)
- `whash-db4`: Daubechies wavelet hashing (wHash)
- `colorhash`: HSV color hashing (colorhash)

See
[this section of the imagehash documentation](https://github.com/JohannesBuchner/imagehash#example-results)
for examples of **different methods producing the same fingerprint for different images**. These
are the analog to cryptographic hash collosions, so it's important to understand what kinds of
scenarios may cause this!
