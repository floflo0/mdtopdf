# MdToPdf

Convert markdown file to pdf file using Chromium.

## Exemple

```sh
./mdtopdf.py README.md
```

## Usage

```
usage: mdtopdf.py [-h] [-v] [-o OUTPUT_FILE] [-c COLORSCHEME] [--list-colorschemes] [INPUT_FILE]

Convert markdown file to pdf.

positional arguments:
    INPUT_FILE                                 the input file to be converted

options:
    -h, --help                                 show this help message and exit
    -v, --version                              show program's version number and exit
    -o OUTPUT_FILE, --output OUTPUT_FILE       the output file where the result will be saved
    -c COLORSCHEME, --colorscheme COLORSCHEME  the colorscheme used to color code blocks (default: github-dark)
    --list-colorschemes                        list all the available colorschemes and exit
```

## Installation

### From sources

Copy [mdtopdf.py](./mdtopdf.py) where you want to install it (in `~/.local/bin`
fro example).

```sh
install -Dm755 mdtopdf.py ~/.local/bin/mdtopdf
```

#### Dependencies

You need to have Chromium or Brave install on your system.

Install [markdown](https://pypi.org/project/Markdown):

```sh
pip install markdown
```

Install [Pygments](https://pygments.org):

```sh
pip install Pygments
```

Or

```sh
pip install -r requirements.txt
```

### Archlinux

Create the arch-package and install it.

```sh
makepkg -csfi
```

## Development


```sh
pip install -r requirements-dev.txt
```

Run the tests:

```sh
./test.sh
```

## Styles

The [css](https://github.com/sindresorhus/github-markdown-css) use for
rendering the pdf.
