#-------------------------------------------------------------------------------
# This file is part of PyMad.
#
# Copyright (c) 2011, CERN. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------

# Make sure setuptools is available. NOTE: the try/except hack is required to
# make installation work with pip: If an older version of setuptools is
# already imported, `use_setuptools()` will just exit the current process.
try:
    import pkg_resources
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, Extension
from distutils.util import get_platform

import sys
from os import path

# Version of pymad (major,minor):
PYMADVERSION=(0, 9)


# setuptools.Extension automatically converts all '.pyx' extensions to '.c'
# extensions if detecting that neither Cython nor Pyrex is available. Early
# versions of setuptools don't know about Cython. Since we don't use Pyrex
# in this module, this leads to problems in the two cases where Cython is
# available and Pyrex is not or vice versa. Therefore, setuptools.Extension
# needs to be patched to match our needs:
try:
    # Use Cython if available:
    from Cython.Build import cythonize
except ImportError:
    # Otherwise, always use the distributed .c instead of the .pyx file:
    def cythonize(extensions):
        def pyx_to_c(source):
            return source[:-4]+'.c' if source.endswith('.pyx') else source
        for ext in extensions:
            ext.sources = list(map(pyx_to_c, ext.sources))
            missing_sources = [s for s in ext.sources if not path.exists(s)]
            if missing_sources:
                raise OSError(('Missing source file: {0[0]!r}. '
                               'Install Cython to resolve this problem.')
                              .format(missing_sources))
        return extensions
else:
    orig_Extension = Extension
    class Extension(orig_Extension):
        """Extension that *never* replaces '.pyx' by '.c' (using Cython)."""
        def __init__(self, name, sources, *args, **kwargs):
            orig_Extension.__init__(self, name, sources, *args, **kwargs)
            self.sources = sources

# Let's just use the default system headers:
include_dirs = []
library_dirs = []

# Parse command line option: --madxdir=/path/to/madxinstallation. We could
# use build_ext.user_options instead, but then the --madxdir argument can
# be passed only to the 'build_ext' command, not to 'build' or 'install',
# which is a minor nuisance.
for arg in sys.argv[:]:
    if arg.startswith('--madxdir='):
        sys.argv.remove(arg)
        prefix = path.expanduser(arg.split('=', 1)[1])
        lib_path_candidates = [path.join(prefix, 'lib'),
                               path.join(prefix, 'lib64')]
        include_dirs += [path.join(prefix, 'include')]
        library_dirs += list(filter(path.isdir, lib_path_candidates))

# required libraries
if get_platform() == "win32" or get_platform() == "win-amd64":
    libraries = ['madx', 'stdc++', 'ptc', 'gfortran', 'msvcrt']
else:
    libraries = ['madx', 'stdc++', 'c']

# Common arguments for the Cython extensions:
extension_args = dict(
    define_macros=[('MAJOR_VERSION', PYMADVERSION[0]),
                   ('MINOR_VERSION', PYMADVERSION[1])],
    libraries=libraries,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    runtime_library_dirs=library_dirs,
    extra_compile_args=['-std=c99'],
)

# Compose a long description for PyPI:
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('COPYING.rst').read()
    long_description += '\n' + open('CHANGES.rst').read()
except IOError:
    pass

setup(
    name='cern-cpymad',
    version='.'.join(map(str, PYMADVERSION)),
    description='Cython binding to MAD-X',
    long_description=long_description,
    url='http://pymad.github.io/cpymad',
    package_dir={
        '': 'src'   # look for packages in src/ subfolder
    },
    ext_modules = cythonize([
        Extension('cern.cpymad.libmadx',
                  sources=["src/cern/cpymad/libmadx.pyx"],
                  **extension_args),
    ]),
    namespace_packages=[
        'cern'
    ],
    packages = [
        "cern",
        "cern.resource",
        "cern.cpymad",
    ],
    include_package_data=True, # include files matched by MANIFEST.in
    author='PyMAD developers',
    author_email='pymad@cern.ch',
    setup_requires=[
    ],
    install_requires=[
        'setuptools',
        'numpy',
        'PyYAML',
    ],
    license = 'CERN Standard Copyright License'
)

