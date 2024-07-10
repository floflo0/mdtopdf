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

Install [pygments](https://pygments.org)

```sh
pip install pygments
```

### Archlinux

Create the arch-package and install it.

```sh
makepkg -cfi
```

## Developpement

Install markdown and pygments libraries types for mypy :

```sh
pip install types-Markdown types-Pygments
```

Run the tests :

```sh
./test.sh
```

## Styles

The [css](https://github.com/sindresorhus/github-markdown-css) use for
rendering the pdf.
