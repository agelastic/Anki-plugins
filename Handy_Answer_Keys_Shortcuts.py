# -*- coding: utf-8 -*-
# Name: Handy Answer Keys Shortcuts
# Copyright: Vitalie Spinu 
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Bind 'j', 'k', 'l', ';' to card answering actions.  This allows answering with
# right hand, keeping your thumb on SPC (default action) and other fingers on
# 'j', 'k', 'l', ';'. If the number of buttons is less than 4, 'l' and ';' will
# do the right thing - choose the maximal ease level.
#
# If you are in the "question" state (no answer is yet visible) these keys
# bypass the display of the answer and automatically set the ease level.  So if
# you press ';', the note is automatically marked with the highest ease level
# (last button in answer state), if you press 'k' or 'l', the note is marked by
# the default ease level ("good"), if you press 'j', the note is marked as hard
# (first button).
# 
# As a bonus 'z' is bound to undo.

from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap

def keyHandler(self, evt, _old):
    key = unicode(evt.text())
    if key == "z":
        try:# throws an error on undo -> do -> undo pattern,  otherwise works fine
            mw.onUndo()
        except:
            pass
    elif key in ["j", "k", "l", ";",]:
        isq = self.state == "question"
        if isq:
            self._showAnswerHack()
        if key == "j":
            self._answerCard(1)
        elif key == "k":
            self._answerCard(2)
        elif key == "l":
            self._answerCard(3)
        elif key == ";":
            self._answerCard(4)
        else:
            return _old(self, evt)
    else:
        return _old(self, evt)

Reviewer._keyHandler = wrap(Reviewer._keyHandler, keyHandler, "around")

