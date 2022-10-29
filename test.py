#!/usr/bin/python3

'''tests for mdtopdf'''

import io
import os
import sys
import unittest
from typing import Callable

from mdtopdf import cli, TMP_FILE_NAME


class TestCli(unittest.TestCase):
    '''Test the cli.'''

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
            msg: message print on failure
            command: the command to test
            args: the arguments fot the command
            returncode: the expected returncode for the command
            stdout: the expected stdout
            stderr: the expected stderr
        '''
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr
        fake_stdout = io.StringIO()
        fake_stderr = io.StringIO()
        sys.stdout = fake_stdout
        sys.stderr = fake_stderr

        command_returncode = command(args)

        sys.stdout = sys_stdout
        sys.stderr = sys_stderr

        self.assertEqual(command_returncode, returncode, f'{msg}: returncode')
        self.assertEqual(stdout, fake_stdout.getvalue(), f'{msg}: stdout')
        self.assertEqual(stderr, fake_stderr.getvalue(), f'{msg}: stderr')

    def test_no_command_name(self) -> None:
        '''test with no command name'''
        self.assert_command(
            'test with no comamnd name',
            cli,
            [],
            returncode=1,
            stderr='Error: no command name\n'
        )

    def test_help(self) -> None:
        '''test help flag'''
        stdout = (
            'Usage: cli [OPTIONS] FILE\n'
            '\n'
            'Convert markdown file to pdf file using md2html and chromium.\n'
            '\n'
            'Options:\n'
            '  -h, --help              Print this help message and exit\n'
            '  -v, --version           Print the version number and exit\n'
            '  -o, --ouput-file <file> Name of output file\n'
            '  --no-css                Use the default styles of chromium\n'
            '  --colorscheme <name>    Set the colorscheme use for code blocks'
            '\n'
        )
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
        '''test version flag'''
        stdout = '1.0.0\n'
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
        '''test no arguments'''
        self.assert_command(
            'test no arguments',
            cli,
            ['cli'],
            returncode=1,
            stderr='cli: error: no input file provided\n'
        )

    def test_too_many_args(self) -> None:
        '''test too many arguments'''
        self.assert_command(
            'test too many arguments',
            cli,
            ['cli', 'file1', 'file2', 'file3'],
            returncode=1,
            stderr='cli: error: too many arguments\n'
        )

    def test_no_chromium(self) -> None:
        '''test when no chromium executable is in the path.'''
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
            stderr='cli: error: could not find chromium executable\n'
        )

    def test_unknow_option(self) -> None:
        '''test unknow argument'''
        self.assert_command(
            'test test unknow option',
            cli,
            ['cli', '--unknow-arg'],
            returncode=1,
            stderr="cli: error: unknow argument '--unknow-arg'\n"
        )

    def test_convert_file(self) -> None:
        '''test convert a file'''
        self.assert_command(
            'test convert file',
            cli,
            ['cli', 'README.md']
        )
        self.assertTrue(os.path.isfile('README.pdf'))
        self.assertFalse(os.path.exists(TMP_FILE_NAME), 'tmp file not removed')

    def test_output_file(self) -> None:
        '''test output file option'''
        self.assert_command(
            'test output file short',
            cli,
            ['cli', 'README.md', '-o', 'test_out_short.pdf']
        )
        self.assertTrue(os.path.isfile('test_out_short.pdf'))
        self.assert_command(
            'test output file long',
            cli,
            ['cli', 'README.md', '--output-file', 'test_out_long.pdf']
        )
        self.assertTrue(os.path.isfile('test_out_long.pdf'))

    def test_no_ouput_file(self) -> None:
        '''test no argument for ouput file option'''
        self.assert_command(
            'test no output file short',
            cli,
            ['cli', 'file', '-o'],
            returncode=1,
            stderr='cli: error: argument expected for the -o option\n'
        )
        self.assert_command(
            'test no output file long',
            cli,
            ['cli', 'file', '--output-file'],
            returncode=1,
            stderr=(
                'cli: error: argument expected for the --output-file option\n'
            )
        )

    def test_2_output_file(self) -> None:
        '''test 2 ouput file'''
        self.assert_command(
            'test 2 output file short',
            cli,
            ['cli', 'file', '-o', 'file1', '-o', 'file2'],
            returncode=1,
            stderr='cli: error: too many output files provided\n'
        )
        self.assert_command(
            'test 2 output file long',
            cli,
            ['cli', 'file', '--output-file', 'file1', '--output-file', 'file2'],
            returncode=1,
            stderr='cli: error: too many output files provided\n'
        )

    def test_inexistent_file(self) -> None:
        '''test inexistent file'''
        self.assert_command(
            'test inexistent file',
            cli,
            ['cli', 'file'],
            returncode=1,
            stderr="cli: error: can't open 'file': no such file or directory\n"
        )

    def test_directory(self) -> None:
        '''test convert a directory'''
        dirname: str = 'test_dir'
        os.mkdir(dirname)
        self.addCleanup(lambda: os.rmdir(dirname))
        self.assert_command(
            'test directory',
            cli,
            ['cli', dirname],
            returncode=1,
            stderr=f'cli: error: {dirname} is a directory\n'
        )

    def test_no_css(self) -> None:
        '''test no css flag'''
        self.assert_command(
            'test --no-css',
            cli,
            ['cli', 'README.md', '--no-css', '-o', 'no-css.pdf']
        )

    def test_change_colorscheme(self) -> None:
        '''test changing the colorscheme'''
        self.assert_command(
            'test change colorscheme',
            cli,
            ['cli', 'README.md', '--colorscheme', 'one-dark']
        )

    def test_unknow_colorscheme(self) -> None:
        '''test unknow colorscheme'''
        self.assert_command(
            'test unknow colorscheme',
            cli,
            ['cli', 'README.md', '--colorscheme', 'unknow colorscheme'],
            returncode=1,
            stderr='cli: error: unknow colorscheme \'unknow colorscheme\'\n'
        )

    def test_no_colorscheme(self) -> None:
        '''test give no colorscheme'''
        self.assert_command(
            'test no colorscheme',
            cli,
            ['cli', 'README.md', '--colorscheme'],
            returncode=1,
            stderr='cli: error: argument --colorscheme: expected one argument\n'
        )


if __name__ == '__main__':
    unittest.main()
