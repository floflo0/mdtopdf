#!/usr/bin/python

"""mdtopdf
Convert markdown file to pdf.
"""

import argparse
import errno
import os
import shutil
import subprocess
import sys
import tempfile
from typing import NoReturn

import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.styles import get_all_styles, get_style_by_name
from pygments.token import Token


__version__ = '1.0.1'


CSS_URL: str = 'https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.6.1/github-markdown-light.min.css'  # pylint: disable=line-too-long
DEFAULT_COLORSCHEME: str = 'github-dark'
CODE_HILITE_CSS_CLASS: str = 'codehilite'

EXIT_SUCCESS: int = 0
EXIT_FAILURE: int = 1


class ChromiumNotFoundException(Exception):
    '''Exception raised when no chromium executable has been found on the
    system.'''


def find_chromium_executable() -> str:
    '''Returns the chromium executable.

    Raises:
        ChromiumNotFoundException: No chromium executable has been found.
    '''
    for name in ['chromium', 'chromium-browser', 'brave']:
        if shutil.which(name) is not None:
            return name

    raise ChromiumNotFoundException()


def md_to_pdf(markdown_file_path: str, pdf_file_path: str,
              colorscheme: str) -> None:
    '''Convert a markdown file to pdf.

    Args:
        markdown_file_path: The path to the markdown file to convert.
        pdf_file_path: The path to save the generated pdf file.
        colorscheme: The colorscheme used to color code blocks.

    Raises:
        ChromiumNotFoundException: No chromium executable has been found.
    '''
    html_file_fd: int
    html_file_path: str
    html_file_fd, html_file_path = tempfile.mkstemp(suffix='.html')

    with open(markdown_file_path, 'r', encoding='utf-8') as markdown_file:
        markdown_content: str = markdown_file.read()

    html_code: str = markdown.markdown(
        markdown_content,
        extensions=[
            FencedCodeExtension(),
            TocExtension(),
            CodeHiliteExtension(
                noclasses=True,
                pygments_style=colorscheme,
                use_pygments=True,
                css_class=CODE_HILITE_CSS_CLASS
            )
        ]
    )

    style = get_style_by_name(colorscheme)
    background: str = style.background_color
    color: str = style.styles[Token]
    title: str = os.path.basename(pdf_file_path)
    with os.fdopen(html_file_fd, 'w', encoding='utf-8') as html_file:
        html_file.write(f'''\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{CSS_URL}">
    <title>{title}</title>
    <style>
        .{CODE_HILITE_CSS_CLASS} {{
            background: unset !important;
        }}
        pre {{
            background: {background} !important;
            color: {color} !important;
        }}
    </style>
</head>
<body class="markdown-body">
    {html_code}
</body>
</html>
''')

    chromium: str = find_chromium_executable()

    subprocess.run([
        chromium,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        f'--print-to-pdf={pdf_file_path}',
        '--no-pdf-header-footer',
        '--run-all-compositor-stages-before-draw',
        html_file_path
    ], check=True, capture_output=False)

    os.remove(html_file_path)


class ArgumentParser(argparse.ArgumentParser):
    '''Custom ArgumentParser that change exit code to 1 on error.'''

    def exit(self, status: int = EXIT_SUCCESS, message: str | None = None
             ) -> NoReturn:
        if message:
            self._print_message(message, sys.stderr)
        if status != EXIT_SUCCESS:
            status = EXIT_FAILURE
        sys.exit(status)


def error(program_name: str, message: str) -> NoReturn:
    '''Print the message to stderr and exit the error code.

    Args:
        program_name: The name of the program.
        message: The error message to print.
    '''
    print(f'{program_name}: error: {message}',
          file=sys.stderr)
    sys.exit(EXIT_FAILURE)


def cli(argv: list[str]) -> int:
    '''The command line interface for this application.

    Args:
        argv: The arguments from the command line.

    Returns the exit code of the application.
    '''
    colorschemes: list[str] = list(get_all_styles())

    def formatter(prog: str) -> argparse.HelpFormatter:
        return argparse.HelpFormatter(prog, indent_increment=4,
                                      max_help_position=500)

    prog: str = os.path.basename(argv[0])
    parser: ArgumentParser = ArgumentParser(
        prog=prog,
        description='Convert markdown file to pdf.',
        formatter_class=formatter
    )

    filename_metavar: str = 'INPUT_FILE'
    parser.add_argument(
        'filename',
        nargs='?',
        metavar=filename_metavar,
        help='the input file to be converted'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '-o',
        '--output',
        metavar='OUTPUT_FILE',
        help='the output file where the result will be saved'
    )

    def colorscheme_type(arg: str) -> str:
        if arg not in colorschemes:
            raise argparse.ArgumentTypeError(f'invalid choice: {repr(arg)}')
        return arg

    parser.add_argument(
        '-c',
        '--colorscheme',
        choices=colorschemes,
        default=DEFAULT_COLORSCHEME,
        metavar='COLORSCHEME',
        type=colorscheme_type,
        help=(
            'the colorscheme used to color code blocks'
            f' (default: {DEFAULT_COLORSCHEME})'
        )
    )
    parser.add_argument( '--list-colorschemes', action='store_true',
        help='list all the available colorschemes and exit'
    )

    args: argparse.Namespace = parser.parse_args(argv[1:])

    filename: str | None = args.filename
    list_colorschemes: bool = args.list_colorschemes
    output_file: str | None = args.output
    colorscheme: str = args.colorscheme

    if list_colorschemes:
        print('\n'.join(colorschemes))
        return EXIT_SUCCESS

    if filename is None:
        parser.error(
            f'the following arguments are required: {filename_metavar}'
        )

    if output_file is None:
        output_file = filename
        if filename[-3:].lower() == '.md':
            output_file = output_file[:-3]
        output_file += '.pdf'

    if not os.path.exists(filename):
        error(prog,
              f'can\'t open {repr(filename)}: {os.strerror(errno.ENOENT)}')

    if os.path.isdir(filename):
        error(prog,
              f'can\'t open {repr(filename)}: {os.strerror(errno.EISDIR)}')

    if os.path.isdir(output_file):
        error(prog,
              f'can\'t save {repr(output_file)}: {os.strerror(errno.EISDIR)}')

    try:
        md_to_pdf(filename, output_file, colorscheme)
    except ChromiumNotFoundException:
        error(prog, 'could not find any chromium executable')

    return EXIT_SUCCESS


def main() -> None:
    '''Run the cli with the arguments from the command line.'''
    sys.exit(cli(sys.argv))


if __name__ == '__main__':
    main()
