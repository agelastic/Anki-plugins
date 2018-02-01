# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/leechdialog.ui'
#
# Created: Mon Jul  4 19:03:53 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(256, 232)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.suspendButton = QtGui.QPushButton(Dialog)
        self.suspendButton.setAutoDefault(False)
        self.suspendButton.setObjectName(_fromUtf8("suspendButton"))
        self.gridLayout.addWidget(self.suspendButton, 4, 0, 1, 1)
        self.deleteButton = QtGui.QPushButton(Dialog)
        self.deleteButton.setAutoDefault(False)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.gridLayout.addWidget(self.deleteButton, 5, 0, 1, 1)
        self.closeEditorLabel = QtGui.QLabel(Dialog)
        self.closeEditorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.closeEditorLabel.setObjectName(_fromUtf8("closeEditorLabel"))
        self.gridLayout.addWidget(self.closeEditorLabel, 0, 0, 1, 2)
        self.addNotesButton = QtGui.QPushButton(Dialog)
        self.addNotesButton.setAutoDefault(False)
        self.addNotesButton.setObjectName(_fromUtf8("addNotesButton"))
        self.gridLayout.addWidget(self.addNotesButton, 4, 1, 1, 1)
        self.editButton = QtGui.QPushButton(Dialog)
        self.editButton.setAutoDefault(False)
        self.editButton.setObjectName(_fromUtf8("editButton"))
        self.gridLayout.addWidget(self.editButton, 6, 0, 1, 1)
        self.changeDeckButton = QtGui.QPushButton(Dialog)
        self.changeDeckButton.setAutoDefault(False)
        self.changeDeckButton.setObjectName(_fromUtf8("changeDeckButton"))
        self.gridLayout.addWidget(self.changeDeckButton, 5, 1, 1, 1)
        self.ignoreButton = QtGui.QPushButton(Dialog)
        self.ignoreButton.setAutoDefault(False)
        self.ignoreButton.setDefault(True)
        self.ignoreButton.setObjectName(_fromUtf8("ignoreButton"))
        self.gridLayout.addWidget(self.ignoreButton, 6, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Leech", None))
        self.label.setText(_translate("Dialog", "<html><head/><body>Leeched 2 times.<br><span style=\" font-weight:600;\">Lapses</span>: 8<br><span style=\" font-weight:600;\">Last interval</span>: 30d<br><span style=\" font-weight:600;\">Ease</span>: 145%<br><span style=\"font-weight:600;\">Total time</span>: 5m23s</body></html>", None))
        self.suspendButton.setToolTip(_translate("Dialog", "Suspend this card.\n"
"This may allow you time to learn other cards that are interfering,\n"
"or you can suspend the card and deal with the problem later.", None))
        self.suspendButton.setText(_translate("Dialog", "&Suspend", None))
        self.deleteButton.setToolTip(_translate("Dialog", "Delete this card\'s note.\n"
"A difficult and low-priority note may not be worth studying anymore.", None))
        self.deleteButton.setText(_translate("Dialog", "&Delete", None))
        self.closeEditorLabel.setText(_translate("Dialog", "Please close the editor to continue.", None))
        self.addNotesButton.setToolTip(_translate("Dialog", "Add new notes to your collection.\n"
"This may be useful if you can split the current card into several easier cards.", None))
        self.addNotesButton.setText(_translate("Dialog", "&Add notes...", None))
        self.editButton.setToolTip(_translate("Dialog", "Edit this card.\n"
"If the phrasing of the question is causing you difficulty, you can fix it now.", None))
        self.editButton.setText(_translate("Dialog", "&Edit...", None))
        self.changeDeckButton.setToolTip(_translate("Dialog", "Move this card to a different deck.\n"
"You may wish to move difficult cards somewhere else,\n"
"for extra study or to get them out of your way temporarily.", None))
        self.changeDeckButton.setText(_translate("Dialog", "C&hange deck", None))
        self.ignoreButton.setToolTip(_translate("Dialog", "Continue reviewing without doing anything about this leech.\n"
"If you think you just need a little bit longer to learn this card, you can continue studying it as is.\n"
"This option should be used sparingly – overuse can waste massive amounts of study time.", None))
        self.ignoreButton.setText(_translate("Dialog", "&Continue", None))

