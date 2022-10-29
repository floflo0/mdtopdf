#!/usr/bin/python3

"""mdtopdf
Convert markdown file to pdf file using chromium.

Usage:
mdtopdf.py --help
"""

import os
import shutil
import subprocess
import sys

import markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.styles import get_all_styles, get_style_by_name
from pygments.token import Text


__version__ = "1.0.0"


TMP_FILE_NAME: str = 'mdtopdf_tmp_file.html'
CSS_URL: str = ('https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/'
                '5.1.0/github-markdown-light.css')
DEFAULT_COLORSCHEME: str = 'dracula'
CSS_CLASS: str = 'codehilite'


def error(command_name: str, message: str) -> None:
    '''Print a formated error message in stderr.

    Args:
        message: the error message to print
    '''
    assert command_name is not None, 'command_name is not defined'
    sys.stderr.write(f'{command_name}: error: {message}\n')


def md_to_html(markdown_file_path: str, html_file_path: str, no_css: bool,
               colorscheme: str) -> None:
    '''Convert the markdown file to html.

    Args:
        markdown_file_path: the path to the markdown file
        html_file_path: the path to the html file generated
    '''
    extensions: list[str | Extension] = ['fenced_code']
    if not no_css:
        extensions.append(CodeHiliteExtension(noclasses=True,
                          pygments_style=colorscheme, css_class=CSS_CLASS))

    with open(markdown_file_path, 'r', encoding='utf-8') as markdown_file:
        html_code = markdown.markdown(markdown_file.read(),
                                      extensions=extensions)

    with open(html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write('<!DOCTYPE html>\n')
        html_file.write('<html>\n')
        html_file.write('<head>\n')
        html_file.write('<meta charset="utf-8">\n')
        if not no_css:
            # use the background color of the syntax hilighting colorscheme and
            # not from the css
            background = get_style_by_name(colorscheme).background_color
            # set default color depending on the colorscheme for the code blocks
            color = get_style_by_name(colorscheme).styles[Text]
            html_file.write(f'<link rel="stylesheet" href="{CSS_URL}">\n')
            html_file.write('<style>\n')
            html_file.write(f'.{CSS_CLASS} {{\n')
            html_file.write('background: unset !important;\n')
            html_file.write('}\n')
            html_file.write('pre {\n')
            html_file.write(f'background: {background} !important;\n')
            html_file.write(f'color: {color};\n')
            html_file.write('}\n')
            html_file.write('</style>\n')
        html_file.write('</head>\n')
        html_file.write('<body class="markdown-body">\n')
        html_file.write(f'{html_code}\n')
        html_file.write('</body>\n')
        html_file.write('</html>\n')


def find_chromium_name() -> str:
    '''Return the chromium executable name or an empty string if no chromium
    executable is find.'''
    for name in ['chromium', 'chromium-browser']:
        if shutil.which(name) is not None:
            return name

    return ''


def html_to_pdf(html_file_path: str, pdf_file_path: str, chromium: str,
                command_name: str) -> None:
    '''Convert the html file to pdf using chromium.

    Args:
        html_file_path: the path to the html file
        pdf_file_path: the path to the pdf file
        chromium: the path to the chromium executable to use.
    '''
    chromium = find_chromium_name()
    if not chromium:
        error(command_name, 'could not find chromium executable')

    subprocess.run([
        chromium, '--headless', '--disable-gpu',
        f'--print-to-pdf={pdf_file_path}', '--print-to-pdf-no-header',
        html_file_path
    ], check=True, capture_output=True)


def md_to_pdf(markdown_file_path: str, pdf_file_path: str, no_css: bool,
              colorscheme: str, chromium: str, command_name: str) -> None:
    '''Convert the markdown file to pdf.

    Args:
        markdown_file_path: the path to the markdown file
        pdf_file_path: the path to the pdf file generated
        chromium: the path to the chromium executable to use.
    '''
    md_to_html(markdown_file_path, TMP_FILE_NAME, no_css, colorscheme)
    html_to_pdf(TMP_FILE_NAME, pdf_file_path, chromium, command_name)
    os.remove(TMP_FILE_NAME)


def usage(command_name: str) -> None:
    '''Print the help message of the cli.

    Arg:
        command_name: the name of the programme to print
    '''
    print(f'Usage: {command_name} [OPTIONS] FILE')
    print()
    print('Convert markdown file to pdf file using md2html and chromium.')
    print()
    print('Options:')
    print('  -h, --help              Print this help message and exit')
    print('  -v, --version           Print the version number and exit')
    print('  -o, --ouput-file <file> Name of output file')
    print('  --no-css                Use the default styles of chromium')
    print('  --colorscheme <name>    Set the colorscheme use for code blocks')


def cli(args: list[str]) -> int:
    '''The command line interface for the app.

    Args:
        args: the argument from the command line

    Return 0 on success.
    '''
    if not args:
        sys.stderr.write('Error: no command name\n')
        return 1

    command_name = args.pop(0)
    help_flag = False
    version_flag = False
    file_path: str | None = None
    output_file: str | None = None
    no_css = False
    colorscheme: str | None = None

    while args:
        arg = args.pop(0)
        match arg:
            case '-h' | '--help':
                help_flag = True
            case '-v' | '--version':
                version_flag = True
            case '-o' | '--output-file':
                if not args:
                    error(command_name,
                          f'argument expected for the {arg} option')
                    return 1
                if output_file is not None:
                    error(command_name, 'too many output files provided')
                    return 1
                output_file = args.pop(0)
            case '--no-css':
                no_css = True
            case '--colorscheme':
                if not args:
                    error(command_name,
                          'argument --colorscheme: expected one argument')
                    return 1
                colorscheme = args.pop(0)
                if colorscheme not in get_all_styles():
                    error(command_name,
                          f'unknow colorscheme {repr(colorscheme)}')
                    return 1
            case _:
                if arg and arg[0] == '-':
                    error(command_name, f'unknow argument {repr(arg)}')
                    return 1
                if file_path is not None:
                    error(command_name, 'too many arguments')
                    return 1
                file_path = arg

    if help_flag:
        usage(command_name)
        return 0

    if version_flag:
        print(__version__)
        return 0

    if file_path is None:
        error(command_name, 'no input file provided')
        return 1

    if output_file is None:
        output_file = file_path
        if file_path[-3:] == '.md':
            output_file = output_file[:-3]
        output_file += '.pdf'

    if os.path.isdir(file_path):
        error(command_name, f'{file_path} is a directory')
        return 1

    if not os.path.exists(file_path):
        error(command_name,
              f'can\'t open {repr(file_path)}: no such file or directory')
        return 1

    if colorscheme is None:
        colorscheme = DEFAULT_COLORSCHEME

    chromium = find_chromium_name()
    if not chromium:
        error(command_name, 'could not find chromium executable')
        return 1

    try:
        md_to_pdf(file_path, output_file, no_css, colorscheme, chromium,
                  command_name)
    except subprocess.CalledProcessError:
        error(command_name, 'impossble to generate the pdf')
        return 1

    return 0


def main() -> None:
    '''Run the cli with the argument from the command line.'''
    sys.exit(cli(sys.argv))


if __name__ == '__main__':
    main()
