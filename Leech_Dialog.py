"""
Leech Dialog
version 0.1.0
Copyright (c) 2016 Soren Bjornstad.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This add-on borrows some code directly from Anki's source and the add-on
writing guide; comments are listed at those places.
"""

from __future__ import division
from aqt import mw, dialogs
from aqt.utils import showInfo, showWarning, askUser, tooltip
from anki.hooks import addHook
from anki.lang import _, ngettext
from anki.stats import CardStats
from anki.utils import fmtTimeSpan
from PyQt4.QtGui import QDialog

import leechdialog.leechdialog as ldForm

class LeechDialog(QDialog):
    def __init__(self, mw, card):
        self.mw = mw
        self.card = card

        QDialog.__init__(self)
        self.form = ldForm.Ui_Dialog()
        self.form.setupUi(self)
        self.form.ignoreButton.clicked.connect(self.reject)
        self.form.suspendButton.clicked.connect(self.onSuspend)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.editButton.clicked.connect(self.onEdit)
        self.form.addNotesButton.clicked.connect(self.onAdd)
        self.form.changeDeckButton.clicked.connect(self.onChangeDeck)
        self.form.closeEditorLabel.setHidden(True)
        self._showCardValues()

        # save func for use if the dialog is disabled, see _toggleDlgEnabled()
        self.workingReject = self.reject

    def _toggleDlgEnabled(self):
        f = self.form
        doHide = not f.suspendButton.isHidden()
        for i in (f.suspendButton, f.deleteButton, f.editButton,
                  f.ignoreButton, f.changeDeckButton, f.addNotesButton):
            i.setHidden(doHide)
        if doHide:
            def closeEditorAlert():
                # can't use a lambda because we need to return None
                showInfo("Please close the editor first.")
                return None
            self.reject = closeEditorAlert
            self.form.closeEditorLabel.setHidden(False)
        else:
            self.reject = self.workingReject
            self.form.closeEditorLabel.setHidden(True)

    def _showCardValues(self):
        lapses = self.card.lapses
        # since we just failed the card, current ivl is no use
        interval = fmtTimeSpan(self.card.lastIvl * 86400)
        ease = self.card.factor // 10

        statManager = CardStats(self.mw.col, self.card)
        secondsSpent = self.mw.col.db.first(
                "select sum(time)/1000 from revlog where cid = :id",
                id=self.card.id)[0]
        totalTime = statManager.time(secondsSpent)

        # watch on updates: calling a private method of sched for config info
        leechThreshold = self.mw.col.sched._lapseConf(self.card)['leechFails']
        if leechThreshold == lapses:
            timesLeeched = "Leech for the first time."
        else:
            beyondOne = (lapses - leechThreshold) // (leechThreshold // 2)
            timesLeeched = "Leeched %i times." % (beyondOne + 1)

        txt = ("{leechtimes}<br>"
               "<b>Lapses</b>: {lapses}<br>"
               "<b>Last interval</b>: {lastivl}<br>"
               "<b>Ease</b>: {ease}%<br>"
               "<b>Total time</b>: {ttime}")
        self.form.label.setText(txt.format(leechtimes=timesLeeched,
                lapses=lapses, lastivl=interval, ease=ease, ttime=totalTime))

    def onSuspend(self):
        # This code is taken from the original leech handler,
        # anki/sched.py:_checkLeech.
        # We can't just use mw.col.sched.suspendCards() because when the
        # reviewer saves the card for us, this change will be lost.
        # https://anki.tenderapp.com/discussions/add-ons/7745-cant-get-cards-to-suspend
        self.mw.checkpoint(_("Suspend"))
        if self.card.odue:
            self.card.due = self.card.odue
        if self.card.odid:
            self.card.did = self.card.odid
        self.card.odue = self.card.odid = 0
        self.card.queue = -1
        tooltip(_("Card suspended."))
        self.accept()

    def onDelete(self):
        note = self.card.note()
        numCards = len(note.cards())
        if numCards > 1:
            r = askUser("Really delete this note? It has %i cards." % numCards,
                        defaultno=True, title="Delete note?")
            if not r:
                return
        self.mw.checkpoint(_("Delete"))
        self.mw.col.remNotes([self.card.note().id])
        tooltip(ngettext(
            "Note and its %d card deleted.",
            "Note and its %d cards deleted.",
            numCards) % numCards)
        self.accept()

    def onEdit(self):
        """
        This function needs to set the leech dialog to non-modal so the user
        can interact with the edit window. This actually only allows the user
        to interact with the editor -- it's not possible to click the "resume
        editing" button in the main window for example.

        I don't understand why, but it works fine to set the dialog to
        non-modal permanently here, but it doesn't work if the dialog is set to
        non-modal in the constructor!

        In order to make sure the user can't do funny things by pressing a
        button in the leech dialog while the editor is still open, we hide all
        the buttons and block reject. Then we temporarily wrap the close-window
        method in aqt to toggle the buttons back on (the normal version is
        restored as soon as it is called once on the edit-current dialog).
        """
        dlg = dialogs.open("EditCurrent", mw)
        oldCloseDlg = dialogs.close
        def newCloseDlg(name):
            if name == "EditCurrent":
                dialogs.close = oldCloseDlg # restore old functionality
                self._toggleDlgEnabled()
            oldCloseDlg(name)
        dialogs.close = newCloseDlg
        self.setModal(False)
        self._toggleDlgEnabled()

    def onAdd(self):
        dialogs.open("AddCards", mw)
        self.setModal(False)

    def onChangeDeck(self):
        # based on aqt/browser.py:setDeck(), and add-on writing guide example
        self.mw.checkpoint(_("Suspend"))
        from aqt.studydeck import StudyDeck
        cids = [self.card.id]
        did = self.mw.col.db.scalar(
            "select did from cards where id = ?", cids[0])
        current = self.mw.col.decks.get(did)['name']
        ret = StudyDeck(
            self.mw, current=current, accept=_("Move Cards"),
            title = _("Change Deck"), help="browse", parent=self)
        if not ret.name:
            return
        did = self.mw.col.decks.id(ret.name)
        deck = self.mw.col.decks.get(did)
        if deck['dyn']:
            showWarning(_("Cards can't be manually moved into a filtered deck."))
            return

        self.mw.checkpoint(_("Change deck"))
        self.card.did = did
        # if the card was in a cram deck, we have to put back the original due
        # time and original deck
        self.card.odid = 0
        if self.card.odue:
            self.card.due = self.card.odue
            self.card.odue = 0
        self.accept()


def leechHook(card):
    ld = LeechDialog(mw, card)
    ld.exec_()

    # Since this add-on doesn't work on mobile, or anywhere it's not installed,
    # it's useful to keep separate track of which notes are leeches that have
    # been marked but not handled and which are leeches that have been marked
    # and dealt with in the dialog. Therefore, anytime this add-on handles a
    # card, it will be tagged 'leech_dialog' rather than 'leech' (and any
    # 'leech' tag present from before will be removed).
    n = card.note()
    n.delTag("leech")
    n.addTag("leech_dialog")
    n.flush()

addHook("leech", leechHook)
