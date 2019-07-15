import sys
import os

from setuptools import find_packages, setup
from setuptools.command.test import test


here_dir = os.path.abspath(os.path.dirname(__file__))


# require python-3.5+, since we only support the native coroutine 'async def'
# style for tests that were introduced in python 3.5.
if sys.version_info < (3, 5):
    print("pytest-tornasync requires Python 3.5 or newer")
    sys.exit(1)


def read(*filenames):
    buf = []
    for filename in filenames:
        filepath = os.path.join(here_dir, filename)
        try:
            with open(filepath) as f:
                buf.append(f.read())
        except FileNotFoundError:
            pass
    return '\n\n'.join(buf)


class PyTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        status = pytest.main(self.test_args)
        sys.exit(status)


_reqs = ['pytest>=3.0', 'tornado>=5.0']


setup(
    name='pytest-tornasync',
    version='0.6.0.post2',
    license='http://www.opensource.org/licenses/mit-license.php',
    url='https://github.com/eukaryote/pytest-tornasync',
    description='py.test plugin for testing Python 3.5+ Tornado code',
    long_description=read('README.rst', 'CHANGES.rst'),
    keywords='testing py.test tornado',
    author='Calvin Smith',
    author_email='sapientdust+pytest-tornasync@gmail.com',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    platforms='any',
    cmdclass={'test': PyTest},
    install_requires=_reqs,
    tests_require=_reqs,
    test_suite='test',
    data_files=[("", ["LICENSE"])],
    entry_points={
        'pytest11': ['tornado = pytest_tornasync.plugin'],
    },
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Framework :: Pytest',
        'Topic :: Software Development :: Testing',
    ] + [
       ("Programming Language :: Python :: %s" % x)
       for x in "3 3.5 3.6 3.7".split()
    ]
)
