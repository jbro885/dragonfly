#
# This file is part of Dragonfly.
# (c) Copyright 2007, 2008 by Christo Butcher
# Licensed under the LGPL.
#
#   Dragonfly is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU Lesser General Public License as published 
#   by the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version.
#
#   Dragonfly is distributed in the hope that it will be useful, but 
#   WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public 
#   License along with Dragonfly.  If not, see 
#   <http://www.gnu.org/licenses/>.
#

"""
Paste action
============================================================================

"""

import sys

from ..actions.action_base import DynStrActionBase
from ..actions.action_key import Key
from ..windows.clipboard import Clipboard


if sys.platform.startswith("win"):
    from win32con import CF_UNICODETEXT, CF_TEXT
    from pywintypes import error as clipboard_manipulation_error
else:
    clipboard_manipulation_error = RuntimeError

    # Use hardcoded values to allow Paste to work on multiple platforms.
    CF_UNICODETEXT = 13
    CF_TEXT = 1


#---------------------------------------------------------------------------

class Paste(DynStrActionBase):

    """
        Paste-from-clipboard action.

        Constructor arguments:
         - *contents* (*str*) -- contents to paste
         - *format* (*int*, Win32 clipboard format) --
           clipboard format
         - *paste* (instance derived from *ActionBase*) --
           paste action
         - *static* (boolean) --
           flag indicating whether the
           specification contains dynamic elements

        This action inserts the given *contents* into the Windows system 
        clipboard, and then performs the *paste* action to paste it into 
        the foreground application.  By default, the *paste* action is the 
        :kbd:`Control-v` keystroke.  The default clipboard format to use 
        is the *Unicode* text format.

    """

    _default_format = CF_UNICODETEXT

    # Default paste action.
    _default_paste = Key("s-insert/20")

    def __init__(self, contents, format=None, paste=None, static=False):
        if not format:
            format = self._default_format
        if not paste:
            paste = self._default_paste
        if isinstance(contents, basestring):
            spec = contents
            self.contents = None
        else:
            spec = ""
            self.contents = contents
        self.format = format
        self.paste = paste
        DynStrActionBase.__init__(self, spec, static=static)

    def _parse_spec(self, spec):
        if self.contents:
            return self.contents
        else:
            return spec

    def _execute_events(self, events):
        original = Clipboard()
        try:
            original.copy_from_system()
        except clipboard_manipulation_error as e:
            self._log.warning("Failed to store original clipboard contents:"
                              " %s" % e)

        if self.format == CF_UNICODETEXT:
            events = unicode(events, "windows-1252")
        elif self.format == CF_TEXT:
            events = str(events)

        clipboard = Clipboard(contents={self.format: events})
        clipboard.copy_to_system()
        self.paste.execute()

        original.copy_to_system()
        return True
