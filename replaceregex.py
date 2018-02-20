# -*- coding: utf-8 -*-
#
# Description: Adds (an additional) search&replaces dialog to Anki.
#
# Author: xelif@icqmail.com
#
from aqt.qt import *
from aqt import mw
from anki.hooks import addHook
from PyQt4 import uic
import re
import sys
import traceback

def deb(*args):
    """Print debug output."""
    sys.stderr.write("\n".join(args) + "\n")

#-------------------------------------------------------------------------------
# Global var (for caching the dialog)
dialog = None

#-------------------------------------------------------------------------------
# ReplaceRegex implementation:
class ReplaceRegex(QDialog):
    def __init__(self):
        if isMac:
            # use a separate window on os x so we can a clean menu
            QDialog.__init__(self, None, Qt.Window)
        else:
            QDialog.__init__(self, mw)
        QDialog.__init__(self, None, Qt.Window)
        self.mw = mw
        self.ui = uic.loadUi('../../addons/replaceregex/form.ui', self)
        self.connect(self, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)
        self.connect(self.ui.anyFieldCheckBox, SIGNAL("toggled(bool)"), self.onAnyFieldToggle)
    def display(self, browser):
        self.browser = browser
        self.show()

    def onAnyFieldToggle(self, value):
        self.ui.fieldEdit.setEnabled(not value)

    def onReject(self):
        pass

    def onAccept(self):
        fieldRegex = self.ui.fieldEdit.text()
        searchRegex = self.ui.searchEdit.toPlainText()
        replaceRegex = self.ui.replaceEdit.toPlainText()
        result = self.bulkReplace(fieldRegex, searchRegex, replaceRegex)
        info = QMessageBox()
        if result:
            if self.countMatches != 0:
                info.setText("Replaced " + str(self.countMatches)
                             + " matches in " + str(self.countFields) + " searched fields.\n"
                             + str(self.countCards) + " cards have been modified.")
            else:
                info.setText("No matches found.")
        else:
            info.setText("No changes made because of an error.")
        info.exec_()

    def _isAnyField(self):
        return self.ui.anyFieldCheckBox.isChecked()

    def bulkReplace(self, fieldRegex, searchRegex, replaceRegex):
        self.countMatches = 0
        self.countFields = 0
        self.countCards = 0
        # Compile regular expression objects for faster matching.
        fieldRO = re.compile(fieldRegex)
        searchRO = re.compile(searchRegex)
        def checkField(field):
            """Check wheter field should be searched."""
            if self._isAnyField():
                return True
            mo = fieldRO.match(name)
            return mo is not None and mo.end() == len(name)
        mw.checkpoint("Bulk-Replace-Regex")
        mw.progress.start()
        try:
            for nid in self.browser.selectedNotes():
                note = mw.col.getNote(nid)
                changed = False
                for i, name in enumerate(mw.col.models.fieldNames(note.model())):
                    if checkField(name):
                        # Replace content of field:
                        (newField, matches) = searchRO.subn(replaceRegex, note.fields[i])
                        note.fields[i] = newField
                        self.countMatches += matches
                        self.countFields += 1
                        changed = changed or matches > 0
                if changed:
                    note.flush()
                    self.countCards += 1
        except:
            mw.col.undo()
            sys.stderr.write(traceback.format_exc())
            return False
        finally:
            mw.progress.finish()
            mw.reset()
        return True

def showDialog(browser):
    global dialog
    if dialog is None:
        dialog = ReplaceRegex()
    dialog.display(browser)

def setupMenu(browser):
    """
    Add the button to the browser menu "edit".
    """
    a = QAction("Bulk-Replace-Regex", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: showDialog(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

#-------------------------------------------------------------------------------
# Setup code.
addHook("browser.setupMenus", setupMenu)

