# MdToPdf

Convert markdown file to pdf file using chromium.

## Exemple

```sh
./mdtopdf.py README.pdf
```

## Usage

```sh
./mdtopdf.py --help
```

## Installation

### From sources

Copy [mdtopdf.py](./mdtopdf.py) where you want to install it.

You need to have chromium install on your system.

Install [markdown](https://pypi.org/project/Markdown) :

```sh
pip install markdown
```

### Archlinux

Create the arch-package and install it.

```sh
makepkg -cfi
```

### Ubuntu

Create the deb package adn install it.

```sh
./package-deb.sh
sudo apt install ./mdtopdf.deb
```

## Developpement

Install markdown library types for mypy :

```sh
sudo python3 -m pip install types-Markdown
```

Run the tests :

```sh
./test.sh
```

## Styles

The [css](https://github.com/sindresorhus/github-markdown-css)  use for rendering the pdf.
