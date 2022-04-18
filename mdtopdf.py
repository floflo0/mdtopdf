#!/usr/bin/env python3

'''
mdtopdf
Convert markdown file to pdf file using chromium.

Usage:
mdtopdf.py --help
'''

import os
import sys
import subprocess


__version__ = '1.0.0'


TMP_FILE_NAME = 'md2pdf_tmp_file.html'
CSS_URL = ('https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/'
           'github-markdown-light.css')


def md_to_html(markdown_file: str, output_file: str, no_css: bool) -> None:
    '''Convert the markdown file to html using md2html.

    Args:
        markdown_file: the path to the markdown file
        output_file: the path to the html file generated
    '''
    html_code = subprocess.run(
        ['md2html', markdown_file],
        check=True,
        capture_output=True
    ).stdout.decode('utf-8')
    with open(output_file, 'w', encoding='utf-8') as html_file:
        print('<!DOCTYPE html>', file=html_file)
        print('<html>', file=html_file)
        print('<head>', file=html_file)
        print('<meta charset="utf-8">', file=html_file)
        if not no_css:
            print(f'<link rel="stylesheet" href="{CSS_URL}">', file=html_file)
        print('</head>', file=html_file)
        print('<body class="markdown-body">', file=html_file)
        print(html_code, file=html_file)
        print('</body>', file=html_file)
        print('</html>', file=html_file)


def html_to_pdf(html_file: str, output_file: str) -> None:
    '''Convert the html file to pdf using chromium.

    Args:
       html_file: the path to the html file
       output_file: the path to the pdf file
    '''
    subprocess.run([
        'chromium', '--headless', '--disable-gpu',
        f'--print-to-pdf={output_file}', '--print-to-pdf-no-header', html_file
    ], check=True, capture_output=True)


def md_to_pdf(file: str, output_file: str, no_css: bool) -> None:
    '''Convert the markdown file to pdf.

    Args:
        markdown_file: the path to the markdown file
        output_file: the path to the pdf file generated
    '''
    md_to_html(file, TMP_FILE_NAME, no_css)
    html_to_pdf(TMP_FILE_NAME, output_file)
    os.remove(TMP_FILE_NAME)


def error(msg: str) -> None:
    '''Print a formated error message in stderr.

    Args:
        msg: the message to print
    '''
    print(f'Error: {msg}', file=sys.stderr)


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
    print('  --no-css                Use the default appearance of chromium')


def cli(args: list[str]) -> int:
    '''The command line interface for the app.

    Args:
        args: the argument from the command line

    Return 0 on success.
    '''
    if not args:
        error('no command name')
        return 1

    command_name = args.pop(0)
    help_flag = False
    version_flag = False
    file_path: str | None = None
    output_file: str | None = None
    no_css = False

    while args:
        arg = args.pop(0)
        match arg:
            case '-h' | '--help':
                help_flag = True
            case '-v' | '--version':
                version_flag = True
            case '-o' | '--output-file':
                if not args:
                    error(f'argument expected for the {arg} option')
                    return 1
                if output_file is not None:
                    error('too many output files provided')
                    return 1
                output_file = args.pop(0)
            case '--no-css':
                no_css = True
            case _:
                if arg and arg[0] == '-':
                    error(f'unknow argument {repr(arg)}')
                    return 1
                if file_path is not None:
                    error('too many arguments')
                    return 1
                file_path = arg

    if help_flag:
        usage(command_name)
        return 0

    if version_flag:
        print(__version__)
        return 0

    if file_path is None:
        error('no input file provided')
        return 1

    if output_file is None:
        output_file = file_path
        if file_path[-3:] == '.md':
            output_file = output_file[:-3]
        output_file += '.pdf'

    if not os.path.exists(file_path):
        error(f"can't open {repr(file_path)}: no such file or directory")
        return 1

    if os.path.isdir(file_path):
        error(f'{file_path} is a directory')
        return 1

    try:
        md_to_pdf(file_path, output_file, no_css)
    except subprocess.CalledProcessError:
        error('Impossble to generate pdf')
        return 1

    return 0


def main() -> None:
    '''Run the cli with the argument from the command line.'''
    sys.exit(cli(sys.argv))


if __name__ == '__main__':
    main()
