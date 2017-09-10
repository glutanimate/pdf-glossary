# -*- coding: utf-8 -*-
#
# This is a mock module that is meant to provide Anki 2.0.x
# compatibility for the reportlab library
# (Binary distributions of Anki do not ship with the
# future_builtins package)
#
# Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
# License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>

# future_builtins.ascii corresponds to repr in Python2.7
# (cf. https://docs.python.org/2.6/library/future_builtins.html)
ascii = repr