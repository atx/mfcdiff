mfcdiff
=======

Utility for creating diffs between Mifare Classic dumps

#### Installation

```
git clone https://github.com/atalax/mfcdiff.git
cd mfcdiff
./setup.py install
```

#### Usage
```
$ mfcdiff -h
usage: mfcdiff [-h] [-p] [-a] [-s] [-m] dumps [dumps ...]

positional arguments:
  dumps                 List of .mfd files

optional arguments:
  -h, --help            show this help message and exit
  -p, --no-pager        Use pager to display the output
  -a, --ascii           Display ASCII instead of hex
  -s, --no-space        Do not put spaces between bytes
  -m, --mad             Dump the MAD descriptors
```

To do a simple diff:

```
mfcdiff tag.mfd card.mfd
```

![mfcdiff](https://cloud.githubusercontent.com/assets/3966931/6166969/e9446190-b2b5-11e4-9cbd-61bf676f1b85.png)

You can also diff more than two files:

```
mfcdiff tag.mfd card.mfd sticker.mfd
```

![mfcdiff](https://cloud.githubusercontent.com/assets/3966931/6201393/f90ace78-b4a6-11e4-82ab-c7c9c6a8d584.png)

Or if you want ASCII:

```
mfcdiff -as tag.mfd card.mfd
```
![mfcdiff](https://cloud.githubusercontent.com/assets/3966931/6201398/20ca3bf6-b4a7-11e4-90a9-40504987f12c.png)

