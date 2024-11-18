#!/usr/bin/python

'''Tests for mdtopdf.'''

import io
import os
import sys
import unittest
from typing import Callable

from mdtopdf import cli


USAGE_LINE: str = (
    'usage: cli [-h] [-v] [-o OUTPUT_FILE] [-c COLORSCHEME] '
    '[--list-colorschemes] [INPUT_FILE]\n'
)


class TestCli(unittest.TestCase):
    '''Test the cli function.'''

    @classmethod
    def setUpClass(cls) -> None:
        cls.clean()
        cls.addClassCleanup(cls.clean)

    @classmethod
    def clean(cls) -> None:
        '''Delete all files created during testing.'''
        files = ['test_out_short.pdf', 'test_out_long.pdf', 'README.pdf',
                 'no-css.pdf']
        for file in files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

    def assert_command(
        self,
        msg: str,
        command: Callable[[list[str]], int],
        args: list[str],
        returncode: int = 0,
        stdout: str = '',
        stderr: str = '',
    ) -> None:
        '''Fail if the returncode or the output of the command don't match.

        Args:
            msg: The message print on failure.
            command: The command to test.
            args: The arguments to pass to the command.
            returncode: The expected returncode for the command.
            stdout: The expected stdout.
            stderr: The expected stderr.
        '''
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr
        fake_stdout = io.StringIO()
        fake_stderr = io.StringIO()
        sys.stdout = fake_stdout
        sys.stderr = fake_stderr

        command_returncode: int
        try:
            command_returncode = command(args)
        except SystemExit as system_exit:
            assert isinstance(system_exit.code, int)
            command_returncode = system_exit.code

        sys.stdout = sys_stdout
        sys.stderr = sys_stderr

        self.assertEqual(command_returncode, returncode, f'{msg}: returncode')
        self.assertEqual(stdout, fake_stdout.getvalue(), f'{msg}: stdout')
        self.assertEqual(stderr, fake_stderr.getvalue(), f'{msg}: stderr')

    def test_help(self) -> None:
        '''Test help flags.'''
        # pylint: disable=line-too-long
        stdout: str = (
            'usage: cli [-h] [-v] [-o OUTPUT_FILE] [-c COLORSCHEME] [--list-colorschemes] [INPUT_FILE]\n'
            '\n'
            'Convert markdown file to pdf.\n'
            '\n'
            'positional arguments:\n'
            '    INPUT_FILE                                 the input file to be converted\n'
            '\n'
            'options:\n'
            '    -h, --help                                 show this help message and exit\n'
            '    -v, --version                              show program\'s version number and exit\n'
            '    -o OUTPUT_FILE, --output OUTPUT_FILE       the output file where the result will be saved\n'
            '    -c COLORSCHEME, --colorscheme COLORSCHEME  the colorscheme used to color code blocks (default: github-dark)\n'
            '    --list-colorschemes                        list all the available colorschemes and exit\n'
        )
        # pylint: enable=line-too-long
        self.assert_command(
            'test help short flag',
            cli,
            ['cli', '-h'],
            returncode=0,
            stdout=stdout
        )
        self.assert_command(
            'test help long flag',
            cli,
            ['cli', '--help'],
            returncode=0,
            stdout=stdout
        )

    def test_version(self) -> None:
        '''Test version flags.'''
        stdout = 'cli 1.1.1\n'
        self.assert_command(
            'test version short flag',
            cli,
            ['cli', '-v'],
            returncode=0,
            stdout=stdout
        )
        self.assert_command(
            'test version long flag',
            cli,
            ['cli', '--version'],
            returncode=0,
            stdout=stdout
        )

    def test_no_args(self) -> None:
        '''Test giving no arguments.'''
        self.assert_command(
            'test giving no arguments',
            cli,
            ['cli'],
            returncode=1,
            stderr=USAGE_LINE + \
                'cli: error: the following arguments are required: INPUT_FILE\n'
        )

    def test_too_many_args(self) -> None:
        '''Test giving too many arguments.'''
        self.assert_command(
            'test giving too many arguments',
            cli,
            ['cli', 'file1', 'file2', 'file3'],
            returncode=1,
            stderr=USAGE_LINE + \
                'cli: error: unrecognized arguments: file2 file3\n'
        )

    def test_no_chromium(self) -> None:
        '''Test when no chromium executable is in the path.'''
        path = os.environ['PATH']
        os.environ['PATH'] = ''
        def restore_path() -> None:
            os.environ['PATH'] = path
        self.addCleanup(restore_path)
        self.assert_command(
            'test no chromium',
            cli,
            ['cli', 'README.md'],
            returncode=1,
            stderr='cli: error: could not find any chromium executable\n'
        )

    def test_unknow_argument(self) -> None:
        '''Test giving unknow argument.'''
        self.assert_command(
            'test giving unknow argument',
            cli,
            ['cli', '--unknow-arg'],
            returncode=1,
            stderr=USAGE_LINE + \
                'cli: error: unrecognized arguments: --unknow-arg\n'
        )

    def test_convert_file(self) -> None:
        '''Test convert a file.'''
        self.assert_command(
            'test convert file',
            cli,
            ['cli', 'README.md']
        )
        self.assertTrue(os.path.isfile('README.pdf'))

    def test_output_file(self) -> None:
        '''Test output file arguments.'''
        self.assert_command(
            'test output file short',
            cli,
            ['cli', 'README.md', '-o', 'test_out_short.pdf']
        )
        self.assertTrue(os.path.isfile('test_out_short.pdf'))
        self.assert_command(
            'test output file long',
            cli,
            ['cli', 'README.md', '--output', 'test_out_long.pdf']
        )
        self.assertTrue(os.path.isfile('test_out_long.pdf'))

    def test_no_ouput_file(self) -> None:
        '''Test giving no argument for ouput file option.'''
        stderr: str = USAGE_LINE + \
            'cli: error: argument -o/--output: expected one argument\n'
        self.assert_command(
            'test giving no output file short',
            cli,
            ['cli', 'file', '-o'],
            returncode=1,
            stderr=stderr
        )
        self.assert_command(
            'test giving no output file long',
            cli,
            ['cli', 'file', '--output'],
            returncode=1,
            stderr=stderr
        )

    def test_inexistent_file(self) -> None:
        '''Test inexistent file.'''
        self.assert_command(
            'test inexistent file',
            cli,
            ['cli', 'file'],
            returncode=1,
            stderr="cli: error: can't open 'file': No such file or directory\n"
        )

    def test_directory(self) -> None:
        '''Test converting a directory.'''
        dirname: str = 'test_dir'
        os.mkdir(dirname)
        self.addCleanup(lambda: os.rmdir(dirname))
        self.assert_command(
            'test converting a directory',
            cli,
            ['cli', dirname],
            returncode=1,
            stderr=f'cli: error: can\'t open \'{dirname}\': Is a directory\n'
        )

    def test_save_to_directory(self) -> None:
        '''Test saving the pdf into a directory.'''
        dirname: str = 'test_dir'
        os.mkdir(dirname)
        self.addCleanup(lambda: os.rmdir(dirname))
        self.assert_command(
            'test saving the pdf into a directory',
            cli,
            ['cli', 'README.md', '-o', dirname],
            returncode=1,
            stderr=f'cli: error: can\'t save \'{dirname}\': Is a directory\n'
        )

    def test_change_colorscheme(self) -> None:
        '''Test changing the colorscheme.'''
        self.assert_command(
            'test changing the colorscheme short',
            cli,
            ['cli', 'README.md', '-c', 'one-dark']
        )
        self.assert_command(
            'test changing the colorscheme long',
            cli,
            ['cli', 'README.md', '--colorscheme', 'one-dark']
        )

    def test_unknow_colorscheme(self) -> None:
        '''Test giving an unknow colorscheme.'''
        stderr: str = (
            USAGE_LINE + 'cli: error: argument -c/--colorscheme: '
            'invalid choice: \'unknow colorscheme\'\n'
        )
        self.assert_command(
            'test giving an unknow colorscheme long',
            cli,
            ['cli', 'README.md', '-c', 'unknow colorscheme'],
            returncode=1,
            stderr=stderr
        )
        self.assert_command(
            'test giving an unknow colorscheme long',
            cli,
            ['cli', 'README.md', '--colorscheme', 'unknow colorscheme'],
            returncode=1,
            stderr=stderr
        )

    def test_no_colorscheme(self) -> None:
        '''Test giving no colorscheme.'''
        stderr: str = USAGE_LINE + \
            'cli: error: argument -c/--colorscheme: expected one argument\n'
        self.assert_command(
            'test giving no colorscheme short',
            cli,
            ['cli', 'README.md', '-c'],
            returncode=1,
            stderr=stderr
        )
        self.assert_command(
            'test giving no colorscheme long',
            cli,
            ['cli', 'README.md', '--colorscheme'],
            returncode=1,
            stderr=stderr
        )

    def test_list_colorschemes(self) -> None:
        '''Test listing available colorschemes.'''
        self.assert_command(
            'test listing available colorschemes',
            cli,
            ['cli', '--list-colorschemes'],
            returncode=0,
            stdout='abap\nalgol\nalgol_nu\narduino\nautumn\nbw\nborland\ncoffee\ncolorful\ndefault\ndracula\nemacs\nfriendly_grayscale\nfriendly\nfruity\ngithub-dark\ngruvbox-dark\ngruvbox-light\nigor\ninkpot\nlightbulb\nlilypond\nlovelace\nmanni\nmaterial\nmonokai\nmurphy\nnative\nnord-darker\nnord\none-dark\nparaiso-dark\nparaiso-light\npastie\nperldoc\nrainbow_dash\nrrt\nsas\nsolarized-dark\nsolarized-light\nstaroffice\nstata-dark\nstata-light\ntango\ntrac\nvim\nvs\nxcode\nzenburn\n'  # pylint: disable=line-too-long
        )


if __name__ == '__main__':
    unittest.main()
