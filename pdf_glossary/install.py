# -*- coding: utf-8 -*-

"""
This file is part of the PDF Glossary add-on for Anki

Platform-dependent binary installer

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

import sys
import os
import shutil

platform = sys.platform
sys_encoding = sys.getfilesystemencoding()
addon_path = os.path.dirname(__file__).decode(sys_encoding)

def check_platform():
    bin_config = os.path.join(addon_path, "bin", "platform")
    try:
        with open(bin_config, "r+") as f:
            old_platform = f.read()
            if platform == old_platform:
                return True
    except (IOError, OSError):
        pass
    with open(bin_config, "w") as f:
        f.write(platform)
    return False

def install_binaries():
    root_src_dir = os.path.join(addon_path, "bin", platform)
    root_dst_dir = os.path.join(addon_path, "libs")

    try:
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)
    except OSError:
        pass

if not check_platform():
    print("Installing binaries for " + platform)
    install_binaries()
