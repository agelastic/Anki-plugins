# ExportCardsAsText.py
# Anki addon for exporting cards from Anki to a text file (CSV, XML, JSON).
# Copyright (c) 2014 Jiri Kriz, http://www.nosco.ch/main/en/contact.php
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# Version 1.1, 14-Sep-2014
# Support: None. Use at your own risk. You can send me suggestions and bug reports. 

# ======================================================
# Remarks:

# It is assumed that the created card and the associated reversed card (if any)
# have neighbouring IDs. More precisely, if a card has ID1 and its 
# associated reversed card has ID2, then no other card has an ID between ID1 and ID2.
# It seems that this assumption is always fulfilled.
# If this assumption were wrong then reverse cards
# would potentially also be exported even if ExportSettings.REVERSE_CARDS = False.
# Note that associated reverse cards have the same 'NoteID' and different 'CardType'.

# The addon was tested on Windows only.

# ======================================================
# Versions:
# 1.0 (19-May-2014) Initial version
# 1.1 (14-Sep-2014) Fixed bug 'IndexError' in deck list 
 
# ======================================================
# See also:
# http://ankisrs.net/docs/addons.html#a-simple-add-on
# https://github.com/dae/anki
# https://ankiweb.net/shared/addons/

# ======================================================
# Usage (HTML)

# Anki addon for exporting cards from Anki to a text file (CSV, XML, JSON).
# Copyright (c) 2014 Jiri Kriz, http://www.nosco.ch/main/en/contact.php
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version 1.1, 14-Sep-2014
# Support: None. Use at your own risk. You can send me suggestions and bug reports.
# <ul>
# <li><b>Format:</b> Format of the exported text file. One of: CSV (Comma Separateted Values), JSON, XML</li>
# <li><b>CSV Delimiter</b> Delimiter in the CSV file, e.g. <i>;</i> or <i>\t</i> (tabulator).</li>
# <li><b>File:</b> The exported file. </li>
# <li><b>Browse:</b> Displays a file dialog to specify the exported file. </li>
# <li><b>Deck Filter:</b> Either the specified deck or all decks will be exported.</li>
# <li><b>Tag Filter:</b> Cards having one of the specified tags (delimited by blanks) will be exported.
				# If the filter is empty, then all cards will be exported.</li>
# <li><b>Include All Fields:</b> If checked, then all card fields will be output.
				# If not checked, then only the front and back sides will be output.</li>
# <li><b>Include All Tags:</b> If checked, then all card tags will be output.
			# If not checked, then none tags will be output.</li>
# <li><b>Include Reverse Cards:</b> If checked, then also the reverse cards will be output.
			# If not checked, then the reverse cards will not be output. </li>
# <li><b>Include Deck Name:</b> If checked, then the card's deck name will be output.
			# If not checked, then the deck name will not be output.</li>
# <li><b>Include Card ID:</b> If checked, then the card's ID will be output.
			# If not checked, then the card's ID will not be output.</li>
# <li><b>Include Card Type:</b>If checked, then the card's type will be output.
			# If not checked, then the card's type will not be output.</li>
# <li><b>Include Note ID:</b> If checked, then the note's ID will be output.
			# If not checked, then the note's ID will not be output.</li>
# <li><b>Include Note Type:</b>If checked, then note's type will be output.
			# If not checked, then the note's type will not be output.</li>
# <li><b>OK:</b> Perform the export with the specified settings. </li>
# <li><b>Cancel:</b> Cancel the export. </li>
# </ul>
# Remarks:
# <ul>
# <li>It is assumed that the created card and the associated reversed card (if any)
# have neighbouring IDs. More precisely, if a card has ID1 and its 
# associated reversed card has ID2, then no other card has an ID between ID1 and ID2.
# It seems that this assumption is always fulfilled.
# If this assumption were wrong then reverse cards
# would potentially also be exported even if 'Include Reverse Cards' = False.
# Note that associated reverse cards have the same 'NoteID' and different 'CardType'.</li>
# <li>The addon was tested on Windows only.</li>
# </ul>
# Versions:
# <ul>
# <li>1.0 (19-May-2014) Initial version</li>
# <li>1.1 (14-Sep-2014) Fixed bug 'IndexError' in deck list </li>
# </ul>

# ======================================================

import os
from PyQt4 import QtCore, QtGui
import aqt
from aqt import mw
from aqt.qt import *
from aqt.utils import askUser, showWarning
from anki.exporting import Exporter

# ======================================================
# Settings: they are set by the dialog box

class ExportSettings:
	def __init__(self):
		self.formats = ["CSV", "JSON", "XML"]
		self.decks = []				# set by ExportDialog
		dir = QDesktopServices.storageLocation(QDesktopServices.DesktopLocation)
		path = os.path.join(dir, "anki_export.csv")
		self.PATHNAME = path 		# file extension will be added based on format
		self.FORMAT_INDEX = 0	  	# 0 = "CSV", 1 = "JSON", 2 = "XML"
		self.CSV_DELIMITER = "\t"   # use "\t" for the tabulator
		self.FILTER_DECK_INDEX = 0	# 0 means all decks. 
		self.FILTER_TAGS = ""		# "" matches cards with any or none tags. 
									# Other example: "t1 t2" matches cards having tag 't1' or 't2'.
		self.ALL_FIELDS = True		# if False, then only Front and Back fields exported
		self.REVERSE_CARDS = True
		self.TAGS = True
		self.DECK_NAME = True
		self.CARD_ID = False
		self.NOTE_ID = False
		self.CARD_TYPE = False		# also called "Template", or "Card" in Anki Browser
		self.NOTE_TYPE = False		# also called "Model name"
		
	def FORMAT(self):
		return self.formats[self.FORMAT_INDEX]
	
	def FILTER_DECK(self):
		return self.decks[self.FILTER_DECK_INDEX]

# ======================================================

class Logger:
	def __init__(self, filePath):
		self.file = open(filePath, "w")
		
	def log(self, msg):
		self.file.write(msg + "\n")
		
	def close(self):
		self.file.close()
		
# ======================================================
# Dialog UI: created with QtDesigner 4.2

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

class Ui_textExportDlg(object):
	def setupUi(self, textExportDlg):
		textExportDlg.setObjectName(_fromUtf8("textExportDlg"))
		textExportDlg.setWindowModality(QtCore.Qt.ApplicationModal)
		textExportDlg.resize(718, 358)
		textExportDlg.setSizeGripEnabled(True)
		textExportDlg.setModal(True)
		self.verticalLayout = QtGui.QVBoxLayout(textExportDlg)
		self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
		self.gridLayout_2 = QtGui.QGridLayout()
		self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
		self.fileEdit = QtGui.QLineEdit(textExportDlg)
		self.fileEdit.setObjectName(_fromUtf8("fileEdit"))
		self.gridLayout_2.addWidget(self.fileEdit, 1, 1, 1, 3)
		self.deckFilterCombo = QtGui.QComboBox(textExportDlg)
		self.deckFilterCombo.setObjectName(_fromUtf8("deckFilterCombo"))
		self.gridLayout_2.addWidget(self.deckFilterCombo, 2, 1, 1, 2)
		self.label = QtGui.QLabel(textExportDlg)
		self.label.setObjectName(_fromUtf8("label"))
		self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
		self.csvLabel = QtGui.QLabel(textExportDlg)
		self.csvLabel.setObjectName(_fromUtf8("csvLabel"))
		self.gridLayout_2.addWidget(self.csvLabel, 0, 2, 1, 1)
		self.formatCombo = QtGui.QComboBox(textExportDlg)
		self.formatCombo.setObjectName(_fromUtf8("formatCombo"))
		self.gridLayout_2.addWidget(self.formatCombo, 0, 1, 1, 1)
		self.csvEdit = QtGui.QLineEdit(textExportDlg)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.csvEdit.sizePolicy().hasHeightForWidth())
		self.csvEdit.setSizePolicy(sizePolicy)
		self.csvEdit.setMaxLength(2)
		self.csvEdit.setObjectName(_fromUtf8("csvEdit"))
		self.gridLayout_2.addWidget(self.csvEdit, 0, 3, 1, 1)
		self.label_3 = QtGui.QLabel(textExportDlg)
		self.label_3.setObjectName(_fromUtf8("label_3"))
		self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
		self.browseButton = QtGui.QPushButton(textExportDlg)
		self.browseButton.setObjectName(_fromUtf8("browseButton"))
		self.gridLayout_2.addWidget(self.browseButton, 1, 4, 1, 1)
		self.label_5 = QtGui.QLabel(textExportDlg)
		self.label_5.setObjectName(_fromUtf8("label_5"))
		self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)
		self.label_4 = QtGui.QLabel(textExportDlg)
		self.label_4.setObjectName(_fromUtf8("label_4"))
		self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
		self.tagFilterEdit = QtGui.QLineEdit(textExportDlg)
		self.tagFilterEdit.setObjectName(_fromUtf8("tagFilterEdit"))
		self.gridLayout_2.addWidget(self.tagFilterEdit, 3, 1, 1, 3)
		self.label_6 = QtGui.QLabel(textExportDlg)
		self.label_6.setObjectName(_fromUtf8("label_6"))
		self.gridLayout_2.addWidget(self.label_6, 3, 4, 1, 1)
		self.gridLayout_2.setColumnStretch(1, 1)
		self.verticalLayout.addLayout(self.gridLayout_2)
		self.line = QtGui.QFrame(textExportDlg)
		self.line.setFrameShape(QtGui.QFrame.HLine)
		self.line.setFrameShadow(QtGui.QFrame.Sunken)
		self.line.setObjectName(_fromUtf8("line"))
		self.verticalLayout.addWidget(self.line)
		self.gridLayout_3 = QtGui.QGridLayout()
		self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
		self.allTagsCheck = QtGui.QCheckBox(textExportDlg)
		self.allTagsCheck.setChecked(True)
		self.allTagsCheck.setObjectName(_fromUtf8("allTagsCheck"))
		self.gridLayout_3.addWidget(self.allTagsCheck, 0, 1, 1, 1)
		self.deckNameCheck = QtGui.QCheckBox(textExportDlg)
		self.deckNameCheck.setChecked(True)
		self.deckNameCheck.setObjectName(_fromUtf8("deckNameCheck"))
		self.gridLayout_3.addWidget(self.deckNameCheck, 1, 1, 1, 1)
		self.cardTypeCheck = QtGui.QCheckBox(textExportDlg)
		self.cardTypeCheck.setObjectName(_fromUtf8("cardTypeCheck"))
		self.gridLayout_3.addWidget(self.cardTypeCheck, 2, 1, 1, 1)
		self.reverseCardsCheck = QtGui.QCheckBox(textExportDlg)
		self.reverseCardsCheck.setChecked(True)
		self.reverseCardsCheck.setObjectName(_fromUtf8("reverseCardsCheck"))
		self.gridLayout_3.addWidget(self.reverseCardsCheck, 1, 0, 1, 1)
		self.cardIdCheck = QtGui.QCheckBox(textExportDlg)
		self.cardIdCheck.setObjectName(_fromUtf8("cardIdCheck"))
		self.gridLayout_3.addWidget(self.cardIdCheck, 2, 0, 1, 1)
		self.allFieldsCheck = QtGui.QCheckBox(textExportDlg)
		self.allFieldsCheck.setChecked(True)
		self.allFieldsCheck.setObjectName(_fromUtf8("allFieldsCheck"))
		self.gridLayout_3.addWidget(self.allFieldsCheck, 0, 0, 1, 1)
		self.noteIdCheck = QtGui.QCheckBox(textExportDlg)
		self.noteIdCheck.setObjectName(_fromUtf8("noteIdCheck"))
		self.gridLayout_3.addWidget(self.noteIdCheck, 3, 0, 1, 1)
		self.noteTypeCheck = QtGui.QCheckBox(textExportDlg)
		self.noteTypeCheck.setObjectName(_fromUtf8("noteTypeCheck"))
		self.gridLayout_3.addWidget(self.noteTypeCheck, 3, 1, 1, 1)
		self.verticalLayout.addLayout(self.gridLayout_3)
		spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
		self.verticalLayout.addItem(spacerItem)
		self.buttonBox = QtGui.QDialogButtonBox(textExportDlg)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
		self.verticalLayout.addWidget(self.buttonBox)

		self.retranslateUi(textExportDlg)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), textExportDlg.accept)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), textExportDlg.reject)
		QtCore.QMetaObject.connectSlotsByName(textExportDlg)

	def retranslateUi(self, textExportDlg):
		textExportDlg.setWindowTitle(_translate("textExportDlg", "Export Cards As Text", None))
		self.label.setText(_translate("textExportDlg", "Format", None))
		self.csvLabel.setText(_translate("textExportDlg", "CSV Delimiter", None))
		self.label_3.setText(_translate("textExportDlg", "File", None))
		self.browseButton.setText(_translate("textExportDlg", "Browse", None))
		self.label_5.setText(_translate("textExportDlg", "Deck Filter", None))
		self.label_4.setText(_translate("textExportDlg", "Tag Filter", None))
		self.label_6.setText(_translate("textExportDlg", "(blanks delimited)", None))
		self.allTagsCheck.setText(_translate("textExportDlg", "Include All Tags", None))
		self.deckNameCheck.setText(_translate("textExportDlg", "Include Deck Name", None))
		self.cardTypeCheck.setText(_translate("textExportDlg", "Include Card Type", None))
		self.reverseCardsCheck.setText(_translate("textExportDlg", "Include Reverse Cards", None))
		self.cardIdCheck.setText(_translate("textExportDlg", "Include Card ID", None))
		self.allFieldsCheck.setText(_translate("textExportDlg", "Include All Fields", None))
		self.noteIdCheck.setText(_translate("textExportDlg", "Include Note ID", None))
		self.noteTypeCheck.setText(_translate("textExportDlg", "Include Note Type", None))

# ======================================================
# Dialog Object

class ExportTextDialog(QDialog):

	def __init__(self, mw):
		QDialog.__init__(self, mw, Qt.Window)
		self.mw = mw
		self.ui = Ui_textExportDlg()
		self.ui.setupUi(self)
		self.setup()
		self.fillValues()

	def accept(self):
		ok = self.readValues()
		if ok:
			exporter = TextExporter(mw.col)
			ok = exporter.doExport()
		if ok:
			QDialog.accept(self)
		  
	def browseFile(self):
		pathName = self.getPathName()
		if pathName:
			self.ui.fileEdit.setText(pathName)

	def fillValues(self):
		self.ui.formatCombo.setCurrentIndex(mw.EXPORT.FORMAT_INDEX)
		self.ui.csvEdit.setEnabled(mw.EXPORT.FORMAT_INDEX == 0)
		if mw.EXPORT.CSV_DELIMITER == "\t":
			self.ui.csvEdit.setText("\\t")
		else:
			self.ui.csvEdit.setText(mw.EXPORT.CSV_DELIMITER)
		self.ui.fileEdit.setText(mw.EXPORT.PATHNAME)
		if mw.EXPORT.FILTER_DECK_INDEX >= self.ui.deckFilterCombo.count():
			 mw.EXPORT.FILTER_DECK_INDEX = 0
		self.ui.deckFilterCombo.setCurrentIndex(mw.EXPORT.FILTER_DECK_INDEX)
		self.ui.tagFilterEdit.setText(mw.EXPORT.FILTER_TAGS)
		self.ui.allFieldsCheck.setChecked(mw.EXPORT.ALL_FIELDS)
		self.ui.reverseCardsCheck.setChecked(mw.EXPORT.REVERSE_CARDS)
		self.ui.allTagsCheck.setChecked(mw.EXPORT.TAGS)
		self.ui.deckNameCheck.setChecked(mw.EXPORT.DECK_NAME)
		self.ui.cardIdCheck.setChecked(mw.EXPORT.CARD_ID)
		self.ui.noteIdCheck.setChecked(mw.EXPORT.NOTE_ID)
		self.ui.cardTypeCheck.setChecked(mw.EXPORT.CARD_TYPE)
		self.ui.noteTypeCheck.setChecked(mw.EXPORT.NOTE_TYPE)

	def formatComboChanged(self, currentIx):
		mw.EXPORT.FORMAT_INDEX = currentIx
		self.ui.csvEdit.setEnabled(currentIx == 0)  # CSV format
		
	def getPathName(self):
		if mw.EXPORT.FORMAT_INDEX == 0:
			filter = "CSV/Text files (*.csv *.txt)"
		elif mw.EXPORT.FORMAT_INDEX == 1:
			filter = "JSON/Text files (*.json *.txt)"
		else:	
			filter = "XML/Text files (*.xml *.txt)"
		pathName = unicode(QFileDialog.getSaveFileName(
			mw, _("Export to File"), mw.EXPORT.PATHNAME, filter,
			options = QFileDialog.DontConfirmOverwrite))
		return pathName

	def readValues(self):
		mw.EXPORT.FORMAT_INDEX = self.ui.formatCombo.currentIndex()
		delimiter = self.ui.csvEdit.text()
		if mw.EXPORT.FORMAT == "CSV" and mw.EXPORT.CSV_DELIMITER == "":
			showWarning(_("The CSV delimiter is not set"))
			return False
		if delimiter == "\\t":
			mw.EXPORT.CSV_DELIMITER = "\t"
		else:
			mw.EXPORT.CSV_DELIMITER = delimiter
		mw.EXPORT.FILEPATH = self.ui.fileEdit.text()
		if mw.EXPORT.FILEPATH == "":
			showWarning(_("The file name is not set"))
			return False
		mw.EXPORT.FILTER_DECK_INDEX = self.ui.deckFilterCombo.currentIndex()
		mw.EXPORT.FILTER_TAGS = self.ui.tagFilterEdit.text().strip()
		mw.EXPORT.ALL_FIELDS = self.ui.allFieldsCheck.isChecked()
		mw.EXPORT.REVERSE_CARDS = self.ui.reverseCardsCheck.isChecked()
		mw.EXPORT.TAGS = self.ui.allTagsCheck.isChecked()
		mw.EXPORT.DECK_NAME = self.ui.deckNameCheck.isChecked()
		mw.EXPORT.CARD_ID = self.ui.cardIdCheck.isChecked()
		mw.EXPORT.NOTE_ID = self.ui.noteIdCheck.isChecked()
		mw.EXPORT.CARD_TYPE = self.ui.cardTypeCheck.isChecked()
		mw.EXPORT.NOTE_TYPE = self.ui.noteTypeCheck.isChecked()
		return True

	def reject(self):
		self.accepted = False
		QDialog.reject(self)

	def setup(self):
		self.ui.formatCombo.addItems(["CSV", "JSON", "XML"])
		self.ui.csvEdit.setText("\\t")
		self.connect(self.ui.formatCombo, SIGNAL("activated(int)"), self.formatComboChanged)
		self.ui.browseButton.clicked.connect(self.browseFile)
		mw.EXPORT.decks = [_("All Decks")] + sorted(mw.col.decks.allNames()) # Version 1.1 (14-Sep-2014): bug fix 
		self.ui.deckFilterCombo.addItems(mw.EXPORT.decks)


# ======================================================
# Exporter

class TextExporter(Exporter):

	def __init__(self, col):
		Exporter.__init__(self, col)
		self.file = None
		self.tagFilterArray = []

	def buildOutputString(self, card, isReversedCard, note):
		if mw.EXPORT.FORMAT_INDEX == 0:
			return self.outputCSV(card, isReversedCard, note)
		elif mw.EXPORT.FORMAT_INDEX == 1:
			return self.outputJSON(card, isReversedCard, note)
		elif mw.EXPORT.FORMAT_INDEX == 2:
			return self.outputXML(card, isReversedCard, note)

	def doExport(self):
		self.file = self.getFile(mw.EXPORT.FILEPATH)
		if not self.file:
			return False
		self.tagFilterArray = mw.EXPORT.FILTER_TAGS.split()
		self.writeHeader()		
		cardIds = sorted(self.cardIds())
		lastNoteId = 0
		for cardId in cardIds:
			card = self.col.getCard(cardId)
			isReversedCard = card.nid == lastNoteId
			if mw.EXPORT.REVERSE_CARDS or not isReversedCard:
				lastNoteId = card.nid
				note = self.col.getNote(card.nid)
				deckName = self.getDeckName(card)
				matchDeck = mw.EXPORT.FILTER_DECK_INDEX == 0 or deckName == mw.EXPORT.FILTER_DECK()
				if matchDeck and self.matchTag(note):
					outputString = self.buildOutputString(card, isReversedCard, note)
					self.file.write(outputString.encode("utf-8"))		
		self.writeFooter()
		return True

	def getDeckName(self, card):
		#if card.odid:
			# in a cram deck
		#	return "%s (%s)" % (
		#		self.col.decks.name(card.did),
		#		self.col.decks.name(card.odid))
		# normal deck
		return self.col.decks.name(card.did)		

	def getFile(self, pathName):
		if os.path.exists(pathName):
			ok = askUser(_("The file \n%s \nalready exists. Overwrite it?") % pathName)
			if not ok:
				return None
		try:
			file = open(pathName, "w")
		except:
			file = None
			showWarning(_("Could not open the file \n%s. \n") % pathName)
		return file
	

	def matchTag(self, note):
		if mw.EXPORT.FILTER_TAGS == "":
			return True
		match = False
		for tag in note.tags:
			match = tag in self.tagFilterArray
			if match:
				break
		return match

	def outputCSV(self, card, isReversedCard, note):
		if isReversedCard:
			lineArray = [note.fields[1], note.fields[0]]
		else:
			lineArray = [note.fields[0], note.fields[1]]
		if mw.EXPORT.TAGS:
			tags = " ".join(note.tags) # all tags in one cell
			lineArray.append(tags)
		if mw.EXPORT.CARD_ID:
			lineArray.append(str(card.id))
		if mw.EXPORT.NOTE_ID:
			lineArray.append(str(note.id))
		if mw.EXPORT.CARD_TYPE:
			lineArray.append(card.template()['name'])
		if mw.EXPORT.NOTE_TYPE:
			lineArray.append(note._model['name']) 
		if mw.EXPORT.DECK_NAME:
			lineArray.append(self.getDeckName(card))
		if mw.EXPORT.ALL_FIELDS:
			lineArray.extend(note.fields[2:]) # remaining fields at the end, because varying number
		lineString = mw.EXPORT.CSV_DELIMITER.join(lineArray)
		lineString += "\n"
		return lineString

	def outputJSON(self, card, isReversedCard, note):
		def encodeString(s):
			js = s.replace("'", '"')
			js = js.replace('"', '\"')
			js = '"' + js + '"'
			return js		
		json = "{"
		# Fields
		fieldNames = [f['name'] for f in note._model['flds']]
		counter = 0
		for fName, fValue in zip(fieldNames, note.fields):
			if not mw.EXPORT.ALL_FIELDS and counter >= 2:
				break
			if counter > 0:
				json += ", "
			fieldName = encodeString(fName)
			if isReversedCard:
				if counter == 0:
					fieldValue = encodeString(note.fields[1])
				elif counter == 1:
					fieldValue = encodeString(note.fields[0])
			else:
				fieldValue = encodeString(fValue)
			json += fieldName + ': ' + fieldValue
			counter += 1
		if mw.EXPORT.TAGS:
			json += ', "Tags": ['
			tags = [encodeString(tag) for tag in note.tags]
			json += ", ".join(tags)
			json += ']'
		if mw.EXPORT.CARD_ID:
			json += ', "CardID": ' + str(card.id)
		if mw.EXPORT.NOTE_ID:
			json += ', "NoteID": ' + str(note.id)
		if mw.EXPORT.CARD_TYPE:
			json += ', "CardType": ' + encodeString(card.template()['name'])
		if mw.EXPORT.NOTE_TYPE:
			json += ', "NoteType": ' + encodeString(note._model['name'])
		if mw.EXPORT.DECK_NAME:
			json += ', "Deck": ' + encodeString(self.getDeckName(card))
		json += "},\n"
		return json

	def outputXML(self, card, isReversedCard, note):
		xml = "<Card>\n"
		# Fields
		fieldNames = [f['name'] for f in note._model['flds']]
		counter = 0
		for fieldName, fieldValue in zip(fieldNames, note.fields):
			if not mw.EXPORT.ALL_FIELDS and counter >= 2:
				break
			if isReversedCard:
				if counter == 0:
					fieldValue = note.fields[1]
				elif counter == 1:
					fieldValue = note.fields[0]
			fieldName = fieldName.replace(' ', '_')
			xml += "  <" + fieldName + ">" + fieldValue + "</" + fieldName + ">\n"
			counter += 1
		if mw.EXPORT.TAGS:
			for tag in note.tags:
				xml += "  <Tag>" + tag + "</Tag>\n"
		if mw.EXPORT.CARD_ID:
			xml += "  <CardID>" + str(card.id) + "</CardID>\n"
		if mw.EXPORT.NOTE_ID:
			xml += "  <NoteID>" + str(note.id) + "</NoteID>\n"
		if mw.EXPORT.CARD_TYPE:
			xml += "  <CardType>" + card.template()['name'] + "</CardType>\n"
		if mw.EXPORT.NOTE_TYPE:
			xml += "  <NoteType>" + note._model['name'] + "</NoteType>\n"
		if mw.EXPORT.DECK_NAME:
			xml += "  <Deck>" + self.getDeckName(card) + "</Deck>\n"
		xml += "</Card>\n"
		return xml

	def writeFooter(self):
		if mw.EXPORT.FORMAT_INDEX == 1: # "JSON"
			line = "{}]\n"  # add empty dummy object, because the previous line ended with ","
			self.file.write(line.encode("utf-8"))
		elif mw.EXPORT.FORMAT_INDEX == 2: # "XML"
			line = "</Anki>\n"
			self.file.write(line.encode("utf-8"))

	def writeHeader(self):
		line = ""
		if mw.EXPORT.FORMAT_INDEX == 0: # "CSV"
			lineArray = ["Field 1 (Front)", "Field 2 (Back)"]
			if mw.EXPORT.TAGS:
				lineArray.append("Tags");
			if mw.EXPORT.CARD_ID:
				lineArray.append("CardID")
			if mw.EXPORT.NOTE_ID:
				lineArray.append("NoteID")
			if mw.EXPORT.CARD_TYPE:
				lineArray.append("CardType")
			if mw.EXPORT.NOTE_TYPE:
				lineArray.append("NoteType")
			if mw.EXPORT.DECK_NAME:
				lineArray.append("Deck")
			if mw.EXPORT.ALL_FIELDS:
				lineArray.append("Further Fields (3, 4, ...)") # at the end, because varying number
			line = mw.EXPORT.CSV_DELIMITER.join(lineArray)
			line += "\n"
		elif mw.EXPORT.FORMAT_INDEX == 1: # "JSON"
			line = "[\n"
		elif mw.EXPORT.FORMAT_INDEX == 2: # "XML"
			line = "<?xml version='1.0' encoding='UTF-8'?>\n"
			self.file.write(line.encode("utf-8"))
			line = "<Anki>\n"
		self.file.write(line.encode("utf-8"))

# ======================================================
# Main program

def displayDlg():
	dlg = ExportTextDialog(mw)
	dlg.exec_()

action = QAction("ExportCardsAsText", mw)
mw.connect(action, SIGNAL("triggered()"), displayDlg)
mw.form.menuTools.addAction(action)
mw.EXPORT = ExportSettings() # keep settings over multiple calls of the dialog


