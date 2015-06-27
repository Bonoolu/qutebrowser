#!/usr/bin/env python3
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2015 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""cx_Freeze script for qutebrowser.

Builds a standalone executable.
"""


import os
import os.path
import sys
import distutils

import cx_Freeze as cx  # pylint: disable=import-error
# cx_Freeze is hard to install (needs C extensions) so we don't check for it.

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
from scripts import setupcommon


BASEDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       os.path.pardir)


def get_egl_path():
    """Get the path for PyQt5's libEGL.dll."""
    if not sys.platform.startswith('win'):
        return None
    return os.path.join(distutils.sysconfig.get_python_lib(),
                        r'PyQt5\libEGL.dll')


def get_build_exe_options(skip_html=False):
    """Get the options passed as build_exe_options to cx_Freeze.

    If either skip_html or --qute-skip-html as argument is given, doesn't
    freeze the documentation.
    """
    if '--qute-skip-html' in sys.argv:
        skip_html = True
        sys.argv.remove('--qute-skip-html')

    include_files = [
        ('qutebrowser/javascript', 'javascript'),
        ('qutebrowser/git-commit-id', 'git-commit-id'),
        ('qutebrowser/utils/testfile', 'utils/testfile'),
    ]

    if not skip_html:
        include_files += [
            ('qutebrowser/html', 'html'),
            ('qutebrowser/html/doc', 'html/doc'),
        ]

    egl_path = get_egl_path()
    if egl_path is not None:
        include_files.append((egl_path, 'libEGL.dll'))

    return {
        'include_files': include_files,
        'include_msvcr': True,
        'includes': [],
        'excludes': ['tkinter'],
        'packages': ['pygments'],
    }


bdist_msi_options = {
    # random GUID generated by uuid.uuid4()
    'upgrade_code': '{a7119e75-4eb7-466c-ae0d-3c0eccb45196}',
    'add_to_path': False,
}

bdist_dmg_options = {
    'applications_shortcut': True,
}

bdist_mac_options = {
    'qt_menu_nib': os.path.join(BASEDIR, 'misc', 'qt_menu.nib'),
    'iconfile': os.path.join(BASEDIR, 'icons', 'qutebrowser.icns'),
    'bundle_name': 'qutebrowser',
}

if sys.platform.startswith('win'):
    base = 'Win32GUI'
    target_name = 'qutebrowser.exe'
else:
    base = None
    target_name = 'qutebrowser'

executable = cx.Executable('qutebrowser/__main__.py', base=base,
                           targetName=target_name,
                           shortcutName='qutebrowser',
                           shortcutDir='ProgramMenuFolder',
                           icon=os.path.join(BASEDIR, 'icons',
                                             'qutebrowser.ico'))


if __name__ == '__main__':
    try:
        setupcommon.write_git_file()
        cx.setup(
            executables=[executable],
            options={
                'build_exe': get_build_exe_options(),
                'bdist_msi': bdist_msi_options,
                'bdist_mac': bdist_mac_options,
                'bdist_dmg': bdist_dmg_options,
            },
            **setupcommon.setupdata
        )
    finally:
        path = os.path.join(BASEDIR, 'qutebrowser', 'git-commit-id')
        if os.path.exists(path):
            os.remove(path)
