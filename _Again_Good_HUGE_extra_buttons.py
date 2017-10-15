# -*- mode: Python ; coding: utf-8 -*-
# • Again Good HUGE buttons
# https://ankiweb.net/shared/info/2074653746
# https://github.com/ankitest/anki-musthave-addonz-by-ankitest
# -- tested with Anki 2.0.44 under Windows 7 SP1
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Copyright (c) 2016-2017 Dmitry Mikheev, http://finpapa.ucoz.net/
# No support. Use it AS IS on your own risk.
"""
 Show 2 buttons: Again and (Hard or Good or Easy) buttons
  so wide as Anki window.
 Or usual 4 buttons: it's on user's choice.

 Good button always takes place of Hard and Easy buttons,
  if they are absent on the card.
 4 wide color buttons only with smiles
  instead of words and with a bigger font on them.

 -- In 2-buttons mode hotkeys are:
 Hotkey 1 means AGAIN in any case.
 Hotkeys 2,3,4 means the same:
   it is Hard, Good or Easy (on user's choice)
 -- In 3-4-buttons mode hotkeys are:
 Hotkey 1 means AGAIN in any case.
 Hotkey 2 means HARD when available otherwise it mean GOOD.
 Hotkey 3 means GOOD anyway.
 Hotkey 4 means maximum available easiness anyhow
  (it is Good for 2 buttons and Easy for 3 or 4 buttons).

 Adds 1-4 (4 by default) extra answer buttons with regular intervals.
  No answer on that card will be given, just setup additional interval.
 You can assign you own intervals, labels (by editing source).
  Hotkeys are 6, 7, 8, 9.
 You can use intervals as button labels
  View - Answer buttons without labels or Ctrl+Alt+Shift+L

 On Cards - Later, Not Now menu click (Escape hotkey):
  No answer will be given, next card will be shown.
  Card stays on its place in queue,
  you'll see it next time you study the deck
  or immediatly after reset of cards' queue.

 • Flip-flop card: Show FrontSide/BackSide
   by Ctrl+Up/Control+Down or ^8/^2 or Insert/0

 To modify a single card so the front and back are inverted
  use F12 in Card Reviewer.

 You can easily add your own field name pairs in existing list.
  Pairs higher in the list take precedence over lower
   if some of them exist in the same note simultaneously.

 2B cont...
"""
from __future__ import unicode_literals
from __future__ import division

"""
 Inspired by Duplicate Selected Notes
  https://ankiweb.net/shared/info/2126361512
 and Create Copy of Selected Cards
  https://ankiweb.net/shared/info/787914845

 It puts the stats when you finish a timebox in a tooltip message
  that goes away after a few seconds.
 Based on Decks Total https://ankiweb.net/shared/info/1421528223

 Some hotkeys:
  Check Database...  Ctrl+Delete
  Check Media...  Alt+Shift+Delete
  Empty Cards...  Ctrl+Shift+Delete
  Add-ons Browse and Install...  Ctrl+Shift+Ins

 rated:90:1 will be available with this addon.

 You can enter more than one addon number in install dialog
  with spaces: 1238745 2378903 9875237

 You can add some {{info:...}} stencil in your templates.

 This is a simple monkey patch add-on that inserts day learning cards
 (learning cards with intervals that crossed the day turnover)
 always before new cards without depending due reviews.

 By default Anki do so:
  learning; new if before; due; day learning; new if after
 With this add-on card will be displayed in the following order:
  learning; (day learning; new) if before; due; (day learning; new) if after

 Normally these cards go after due, but I want them to go before new.

 If Tools -> Preferences... -> Basic -> Show new cards before reviews
    learning; day learning; new; due
 If Tools -> Preferences... -> Basic -> Show new cards after reviews
    learning; due; day learning; new

 How to make Anki insensitive case when using {{type:field}}
 Upper case, lower case and {{type:}} /monkey patch/

 You can use it together with
 Multiple type fields on card
 https://ankiweb.net/shared/info/689574440

 Inspired by
 Select Buttons Automatically If Correct Answer, Wrong Answer or Nothing
 https://ankiweb.net/shared/info/2074758752
"""
import datetime
import random
import json
import time
import sys
import os
import re
import copy
import unicodedata
import HTMLParser

import anki  # ' Addons Install Tooltip
import aqt

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import anki.hooks
import anki.utils
import anki.sound

import aqt.main
import aqt.utils
import aqt.qt
import aqt.reviewer
import aqt.editor
import aqt.fields
import aqt.deckconf
import aqt.forms

import aqt.customstudy
import anki.sched  # why?

from anki.collection import _Collection

from aqt.qt import *
from aqt.clayout import CardLayout
from anki.consts import MODEL_STD, MODEL_CLOZE
from anki.consts import *

# Get language class
# import anki.lang
lang = anki.lang.getLang()

extra_buttons = [  # should start from 6 anyway
    {'Description': '5-7d',
        'Label': '!!!',
        'ShortCut': '6',
        'ReschedMin': 5,
        'ReschedMax': 7},
    {'Description': '8-15d',
        'Label': 'Veni',
        'ShortCut': '7',
        'ReschedMin': 8,
        'ReschedMax': 15},
    {'Description': '3-4w',
        'Label': 'Vidi',
        'ShortCut': '8',
        'ReschedMin': 15,
        'ReschedMax': 30},
    {'Description': '2-3mo',
        'Label': 'Vici',
        'ShortCut': '9',
        'ReschedMin': 31,
        'ReschedMax': 90},
]

MSG = {
    'en': {
        'later': _('later'),
        'not now': _('not now'),
        'Later, not now': _('&Later, not now'),

        'View': _('&View'),
        'Cards': _('&Cards'),
        'Sound': _('&Sound'),
        'Go': _('&Go'),

        'HardGoodEasy':
            _('Again')+', '+_('Hard')+', '+_('Good')+', '+_('Easy'),
        'Again': '&'+_('Again'),
        'AgainHard': _('Again')+', &'+_('Hard'),
        'AgainGood': _('Again')+', &'+_('Good'),
        'AgainEasy': _('Again')+', &'+_('Easy'),

        'no_smiles': _('No smiles'),
        'no_styles': _('No big buttons'),
        'no_labels': _('Next Interva&L — on answer buttons'),
        'later_not_now': _('&nbsp;not&nbsp;now&nbsp;'),
        'no_extra_buttons': _('Hide &Extra buttons'),
        'Hide button: ': _('&Hide button: '),
        'Edit': _('Edit'),
        'More': _('More'),
        'Hide buttons': _('Hide buttons: '),
        'Edit': _('&Edit...'),
        'Edit Layout': _('Edi&t Layout...'),
        'Edit Fields': _('Edit &Fields...'),
        'flat_buttons': _('&Flat buttons'),
        'HUGE_buttons': _('&HUGE buttons options'),

        'aa': _('About addon  '),

        'showFrontSide': _('Show &FrontSide'),
        'showBackSide': _('Show &BackSide'),
        'viewFrontSide': _('&FrontSide'),
        'viewBackSide': _('&BackSide'),
        'cardFrontSide': _("Card's &FrontSide"),
        'cardBackSide': _("Card's &BackSide"),
        'gotoFrontSide': _('Goto &FrontSide'),
        'gotoBackSide': _('Goto &BackSide'),
        'goFrontSide': _('to &FrontSide'),
        'goBackSide': _('to &BackSide'),

        'swap_fields': _('S&wap %s and %s fields'),
        'fields_swapped': _('<b>%s</b> and <b>%s</b> swapped.'),
        'swapping': _('Swap fields'),
        'duplicate': _('Duplicate notes and Swap fields'),
        'target_deck': _('Enter the name of target deck:'),

        'till next': _('Number of days until next review'),
        'current': _('actual interval'),
        'card ease': _('Card ease'),
        'days interval': _('&Prompt and Set ... days interval'),

        'search in browser': 'Search Anki Browser for %s...',
        'delete note': 'Delete note?',

        'autoshow': _("Autoshow answer/next question"),
        'autoshow Answer': _("Automatically show answer after"),
        'autoshow Question': _("Automatically show next question after"),
        'AUTOSHOW_STATE is on':
            "<b>Auto</b> show Q-and-A is <b style=color:blue;>ON</b> now",
        'AUTOSHOW_STATE is off':
            "<b>Auto</b> show QandA is <b style=color:red;>OFF</b> now",

        'show_install': _("Show Browse and Install... &Again"),
        'open_ankiweb': _("Open Anki&Web shared add-ons site"),
        'exact': 'type: compare exactly',
        },
    'ru': {
        'later': 'позже',
        'not now': 'не сейчас',
        'Later, not now': 'Поз&же, не сейчас',

        'View': '&Вид',
        'Cards': '&Карточки',
        'Sound': '&Звук',
        'Go': 'П&ереход',

        'HardGoodEasy':
            _('Again')+', '+_('Hard')+', '+_('Good')+', '+_('Easy'),
        'Again': '&'+_('Again'),
        'AgainHard': _('Again')+', &'+_('Hard'),
        'AgainGood': _('Again')+', &'+_('Good'),
        'AgainEasy': _('Again')+', &'+_('Easy'),

        'no_smiles': '&Без смайликов',
        'no_styles': '&Обычная высота кнопок',
        'no_labels': 'На кнопках о&ценок - следующий интервал',
        'later_not_now': '&nbsp;не&nbsp;сейчас&nbsp;',
        'Hide button: ': 'Скрыть кнопку: ',
        'no_extra_buttons': 'Скрыть кнопки &интервалов',
        'Edit': 'Правка',
        'More': 'Ещё',
        'Hide buttons': 'Скрыть кнопки: ',
        'Edit': 'Ре&дактирование...',
        'Edit Layout': '&Шаблоны карточек...',
        'Edit Fields': '&Список полей...',
        'flat_buttons': '&Плоские кнопки',
        'HUGE_buttons': '&Настройка кнопок ответа',

        'aa': 'О дополнении  ',

        'showFrontSide': 'Перейти на &Лицевую Сторону карточки',
        'showBackSide': 'Перейти на &Оборотную Сторону карточки',
        'viewFrontSide': 'Показать &Лицевую Сторону карточки',
        'viewBackSide': 'Показать &Оборотную Сторону карточки',

        'swap_fields': 'О&бмен полей %s и %s',
        'fields_swapped':
            'Выполнен обмен значений ' +
            'между полями <b>%s</b> и <b>%s</b>.',
        'swapping': 'Обмен полей',
        'duplicate': 'Дублировать записи и обменять поля',
        'target_deck': 'Введите имя целевой папки для дублируемых карточек:',

        'till next': 'Дней до следующего просмотра карточки',
        'current': 'фактический интервал',
        'card ease': 'Лёгкость карточки',
        'days interval': '&Через ... дней',

        'search in browser': 'Поиск в Обозревателе Anki: %s...',
        'delete note': "Удалить запись?",

        'autoshow': "Автопоказ ответа/следующего вопроса",
        'autoshow Answer': "Автоматически показывать ответ на вопрос через",
        'autoshow Question': "Автоматически показывать следующий вопрос через",
        'AUTOSHOW_STATE is on':
            "<b style=color:blue;>Включён</b> <b>автопоказ</b> " +
            "вопросов и ответов",
        'AUTOSHOW_STATE is off':
            "<b>Автопоказ</b> вопросов и ответов " +
            "<b style=color:red;>отключён</b>",

        'show_install': "Показывать Обзор и установка... &Снова",
        'open_ankiweb': 'Открыть сайт AnkiWeb с &дополнениями',
        'exact': 'type: точное сравнение при проверке',
        }
    }

try:
    MSG[lang]
except KeyError:
    lang = 'en'

# 'позже' if lang == 'ru' else _('later')
# 'не сейчас' if lang == 'ru' else _('not now')
# _(u'&Карточки') if lang == 'ru' else _(u'&Cards')
# u'Позж&е, не сейчас' if lang == 'ru' else _(u'&Later, not now')

# _('&Вид') if lang == 'ru' else _('&View')
# '&Кнопки оценок - без меток' if lang == 'ru'
#   else _('&Answer buttons without labels')
# '&nbsp;не&nbsp;сейчас&nbsp;'
#   if lang == 'ru' else _('&nbsp;not&nbsp;now&nbsp;')

HOTKEY = {
    'no_smiles': QKeySequence('Ctrl+Alt+Shift+O'),
    'no_styles': QKeySequence('Ctrl+Alt+Shift+B'),
    'no_labels': QKeySequence('Ctrl+Alt+Shift+L'),
    'later_not_now': 'Escape',
    'hide_later': QKeySequence('Ctrl+Alt+Shift+Esc'),
    'HideButtons': QKeySequence('Ctrl+Alt+Shift+M'),
    'no_extra_buttons': QKeySequence('Ctrl+Alt+Shift+N'),

    'All':  QKeySequence('Ctrl+Alt+Shift+0'),
    'Again': QKeySequence('Ctrl+Alt+Shift+1'),
    'Hard': QKeySequence('Ctrl+Alt+Shift+2'),
    'Good': QKeySequence('Ctrl+Alt+Shift+3'),
    'Easy': QKeySequence('Ctrl+Alt+Shift+4'),

    'flat_buttons': 'Ctrl+Alt+Shift+F',

    "next_cloze": 'Ctrl+Space',
    "same_cloze": 'Ctrl+Alt+Space',

    'same_without_Alt': 'F1',
    "next_closure": 'F2',  # 'Ctrl+Shift+C'
    "same_closure": 'Alt+F2',  # 'Ctrl+Alt+Shift+C' -- old style

    # Ctrl+F11 does not work
    "LaTeX": 'Alt+F11',  # "Ctrl+T, T"
    "LaTeX$": 'F11',       # "Ctrl+T, E"
    "LaTeX$$": 'Shift+F11',  # "Ctrl+T, M"

    'showFrontSide': "Ctrl+Up",
    'showBackSide': "Ctrl+Down",
    'viewFrontSide': "Ctrl+8",
    'viewBackSide': "Ctrl+2",

    'swap': 'F12',
    'dupe': 'Shift+F12',
    'timebox': "Ctrl+Shift+T",
    'prompt_popup': 'Alt+Shift+Space',
    'autoshow': 'Ctrl+Shift+F5',
    'Install': QKeySequence('Ctrl+Shift+Insert'),
    }

# It is a part of '• Must Have' addon's functionality:
#  --musthave.py
#   https://ankiweb.net/shared/info/67643234

# based on
#  _Again_Hard.py
#   https://ankiweb.net/shared/info/1996229983
#   old name of this one
#  _Later_not_now_button.py
#   https://ankiweb.net/shared/info/777151722
#  ' Again Hard Good Easy wide big buttons
#   https://ankiweb.net/shared/info/1508882486

# inspired by
#  Answer_Key_Remap.py
#   https://ankiweb.net/shared/info/1446503737
#  Bigger Show Answer Button
#   https://ankiweb.net/shared/info/1867966335
#  Button Colours (Good, Again)
#   https://ankiweb.net/shared/info/2494384865
#  Bigger Show All Answer Buttons
#   https://ankiweb.net/shared/info/2034935033
#  More_Answer_Buttons_for_New_Cards.py
#   https://ankiweb.net/shared/info/468253198 invalid id
#   https://ankiweb.net/shared/info/153603893
#  Low Key Anki: Pass/Fail
#   https://ankiweb.net/shared/info/477405355

black = 'none'  # Night_Mode compatibility
orange = '#c90'  # darkgoldenrod
red = '#c33'  # #c33
green = '#3c3'  # #090
blue = '#69f'  # #66f

remap = 'All'
remaps = {'Again':
          {1:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           2:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           3:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           4:  [None, 1, 1, 1, 1]},    # nil     Again   Again   Again   Again
          'Hard':
          {1:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           2:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           3:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           4:  [None, 1, 2, 2, 2]},    # nil     Again   Hard    Hard    Hard
          'Good':
          {1:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           2:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           3:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           4:  [None, 1, 3, 3, 3]},    # nil     Again   Good    Good    Good
          'Easy':
          {1:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           2:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           3:  [None, 1, 3, 3, 3],     # nil     Again   Easy    Easy    Easy
           4:  [None, 1, 4, 4, 4]},    # nil     Again   Easy    Easy    Easy
          'All':
          {1:  [None, 1, 1, 1, 1],     # nil     Again   Again   Again   Again
           2:  [None, 1, 2, 2, 2],     # nil     Again   Good    Good    Good
           3:  [None, 1, 2, 2, 3],     # nil     Again   Good    Good    Easy
           4:  [None, 1, 2, 3, 4]}}    # nil     Again   Hard    Good    Easy

# -- width of Show Answer button, triple, double and single answers buttons
BEAMS4 = '99%'
BEAMS3 = '74%'
BEAMS2 = '48%'
BEAMS1 = '24%'

USE_INTERVALS_AS_LABELS = False  # True  #
EDIT_MORE_BUTTONS = True  # False  #
HIDE_LATER = False  # True  #
swAdded = True  # False  #
NO_SMILES = False  # True  #
NO_STYLES = False  # True  #

##

BUTTON_COLOR = {'Again': [black, red, red, red, red],
                'Hard': [black, red, orange, orange, orange],
                'Good': [black, red, green, green, green],
                'Easy': [black, red, blue, blue, blue],
                'All': [black, red, orange, green, blue]}

BTN_CLR = {'Again': red, 'Hard': orange, 'Good': green, 'Easy': blue}

BUTTON_LABEL = {'Again': '<span style="color:' + red + ';">o_0</span>',
                'Hard': '<b style="color:' + orange + ';">:-(</b>',
                'Good': '<b style="color:' + green + ';">:-|</b>',
                'Easy': '<b style="color:' + blue + ';">:-)</b>'}

BTN_LABL = {
    'en': {
            'Again': _('Again').upper(),
            'Hard': _('Hard').upper(),
            'Good': _('Good').upper(),
            'Easy': _('Easy').upper(),
        },
    'ru': {
            'Again': 'СНОВА',
            'Hard': 'ТРУДНО',
            'Good': 'ХОРОШО',
            'Easy': 'ЛЕГКО',
        }
    }

try:
    import Night_Mode

    Night_Mode.nm_css_bottom = Night_Mode.nm_css_buttons \
        + Night_Mode.nm_css_color_replacer + \
        """
body {
 background:-webkit-gradient(linear,
    left top, left bottom, from(#333), to(#222));
 border-top-color: #000;
}
.stattxt {
 color: #ccc;
}
        """
except ImportError:
    pass

FLIP_FLOP = True
# FLIP_FLOP = False

ANKI_MENU_ICONS = True
# ANKI_MENU_ICONS = False

try:
    MUSTHAVE_COLOR_ICONS = os.path.join(
        aqt.mw.pm.addonFolder(), 'handbook')
except:
    MUSTHAVE_COLOR_ICONS = ''

ZERO_KEY_TO_SHOW_ANSWER = True
# ZERO_KEY_TO_SHOW_ANSWER = False

##

CASE_SENSITIVE = True  # False  #

SWAP_TAG = False
# SWAP_TAG = datetime.datetime.now().strftime(
#    'swapped::swap-%Y-%m-%d')  #-%H:%M:%S')
# SWAP_TAG = datetime.datetime.now().strftime('sw-%y-%m-%d')

DUPE_TAG = False
# DUPE_TAG = datetime.datetime.now().strftime(
#    'double::dupe-%Y-%m-%d')  # -%H:%M:%S')
# DUPE_TAG = datetime.datetime.now().strftime('dp-%y-%m-%d')

fldlst = [
    ['En', 'Ru'],
    ['Eng', 'Rus'],
    ['English', 'Russian'],
    ['по-английски', 'по-русски'],
    ['Q', 'A'], ['В', 'О'],
    ['Question', 'Answer'],
    [_('Question'), _('Answer')],
    ['Front', 'Back'],
    [_('Front'), _('Back')],  # Вопрос, Ответ
]

# Anki uses a single digit to track which button has been clicked.
NOT_NOW_BASE = 5

# We will use shortcut number from the first extra button
#  and above to track the extra buttons.
INTERCEPT_EASE_BASE = 6

# Must be four or less
assert len(extra_buttons) <= 4

SWAP_TAG = False
# SWAP_TAG = datetime.datetime.now().strftime(
#    'rescheduled::re-%Y-%m-%d::re-card')
# SWAP_TAG = datetime.datetime.now().strftime('re-%y-%m-%d-c')

USE_INTERVALS_AS_LABELS = False  # True  #

FLAT_BUTTONS = True  # False  #

AUTOSHOW_STATE = False  # True  #

install_tooltip = True  # False  #
install_hotkeys = True  # False  #
install_again = False  # True  #
install_menu = True  # False  #

#

__addon__ = "'" + __name__.replace('_', ' ')
__version__ = "2.0.44a"

if __name__ == '__main__':
    print("This is _Again_Good_HUGE_extra_buttons" +
          " add-on for the Anki program" +
          "and it can't be run directly.")
    print('Please download Anki 2.0 from https://apps.ankiweb.net/')
    sys.exit()
else:
    pass

if sys.version[0] == '2':  # Python 3 is utf8 only already.
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf8')

##

old_addons = (
    'Answer_Key_Remap.py',
    'Bigger_Show_Answer_Button.py',
    'Button_Colours_Good_Again.py',
    'Bigger_Show_All_Answer_Buttons.py',
    'More_Answer_Buttons_for_New_Cards.py',
    '_Again_Hard.py',
    # '_Editor_Fontsize.py',
    '_Again_Hard_Good_Easy_wide_big_buttons.py',
    '_Alternative_hotkeys_to_cloze_selected_text_in_Add_or_Editor_window.py',
    '_Later_not_now_button.py',
    'More_Answer_Buttons_for_New_Cards.py',
    '_More_Answer_Buttons_for_ALL_Cards.py',
    'Low_Key_Anki_PassFail.py',
    '_Flip-flop.py',
    '_Duplicate_notes_and_Swap_fields.py',
    '_Swap.py',
    '_Swap_fields.py',
    'Create_Copy_of_Selected_Cards.py',
    'Create_Duplicate_Notes.py',
    'Duplicate_Selected_Notes.py',
    'anki-browser-create-duplicate.py',
    '_Prompt_and_set_days_interval_and_card_ease.py',
    'Automatically_show_answer_after_X_seconds.py',
    '_Addons_Install_Tooltip.py',
)

old_addons2delete = ''
for old_addon in old_addons:
    if len(old_addon) > 0:
        old_filename = os.path.join(aqt.mw.pm.addonFolder(), old_addon)
        if os.path.exists(old_filename):
            old_addons2delete += old_addon[:-3] + ' \n'

if old_addons2delete != '':
    if lang == 'ru':
        aqt.utils.showText(
            'В каталоге\n\n ' + aqt.mw.pm.addonFolder() +
            '\n\nнайдены дополнения, которые уже включены в дополнение\n' +
            " Again Good HUGE buttons \n" +
            'и поэтому будут конфликтовать с ним.\n\n' +
            old_addons2delete +
            '\nУдалите эти дополнения и перезапустите Anki.')
    else:
        aqt.utils.showText(
            '<big>There are some add-ons in the folder <br>\n<br>\n' +
            ' &nbsp; ' + aqt.mw.pm.addonFolder() +
            '<pre>' + old_addons2delete + '</pre>' +
            'They are already part of<br>\n' +
            " <b> &nbsp; Again Good HUGE buttons</b>" +
            ' addon.<br>\n' +
            'Please, delete them and restart Anki.</big>', type="html")

act = [None, None, None, None, None]

# --------------------------
# hotkeys does not work on context menu
# for information purpose only (exploratory testing is anticipated)


def ask_delete():
    """Delete a note after asking the user."""
    if aqt.mw.state != 'review':
        return
    if aqt.utils.askUser(MSG[lang]['delete note']):  # , defaultno=True):
        aqt.mw.reviewer.onDelete()

# -- Disable the delete key in reviews
aqt.mw.disconnect(aqt.mw.reviewer.delShortcut, aqt.qt.SIGNAL(
    "activated()"), aqt.mw.reviewer.onDelete)
# дисконнект нужен обязательно, иначе продолжают работать вместе
aqt.mw.connect(aqt.mw.reviewer.delShortcut,
               aqt.qt.SIGNAL("activated()"), ask_delete)

opts = [
    [_("Mark Note"), "*", aqt.mw.reviewer.onMark],
    None,
    [_("Bury Card"), "-", aqt.mw.reviewer.onBuryCard],
    [_("Bury Note"), "=", aqt.mw.reviewer.onBuryNote],
    [_("Suspend Card"), "@", aqt.mw.reviewer.onSuspendCard],
    [_("Suspend Note"), "!", aqt.mw.reviewer.onSuspend],
    [_("Delete Note"), "Delete", ask_delete],  # aqt.mw.reviewer.onDelete],
    None,
    [_("Options"), "o", aqt.mw.reviewer.onOptions],
]

opts.extend([
    None,
    [_("Replay Audio"), "r", aqt.mw.reviewer.replayAudio],
    None,
])

opts.append(
    [_("Record Own Voice"), "Shift+v", aqt.mw.reviewer.onRecordVoice],
)
opts.append(
    [_("Replay Own Voice"), "v", aqt.mw.reviewer.onReplayRecorded],
)


class BrowserLookup:

    def get_selected(self, view):
        """Copy selected text"""
        return view.page().selectedText()

    def lookup_action(self, view):
        browser = aqt.dialogs.open("Browser", aqt.mw)
        browser.form.searchEdit.lineEdit().setText(self.get_selected(view))
        browser.onSearch()

    def add_action(self, view, menu, action):
        """Add 'lookup' action to context menu."""
        if self.get_selected(view):
            action = menu.addAction(action)
            action.connect(action, SIGNAL('triggered()'),
                           lambda view=view: self.lookup_action(view))

    def context_lookup_action(self, view, menu):
        if aqt.mw.state != 'review':
            return

        edit_current_action = menu.addAction(MSG[lang]["Edit"])
        edit_current_action.connect(
            edit_current_action, SIGNAL("triggered()"), go_edit_current)

        more_menu = QMenu(MSG[lang]["More"], menu)
        menu.addMenu(more_menu)

        for row in opts:
            if not row:
                more_menu.addSeparator()
                continue
            label, scut, func = row
            a = more_menu.addAction(label)
            a.setShortcut(QKeySequence(scut))
            a.connect(a, SIGNAL("triggered()"), func)

        """Browser Lookup action"""
        self.add_action(
            view, menu,
            MSG[lang]['search in browser'] % self.get_selected(view)[:20])

# Add lookup actions to context menu
browser_lookup = BrowserLookup()
anki.hooks.addHook(
    "AnkiWebView.contextMenuEvent",
    browser_lookup.context_lookup_action)

"""
# Bigger Show Answer Button
For people who do their reps with a mouse.
Makes the show answer button wide enough to cover all 4 of the review buttons.
"""


def newRemaining(self):
    if not self.mw.col.conf['dueCounts']:
        return 0
    idx = self.mw.col.sched.countIdx(self.card)
    if self.hadCardQueue:
        # if it's come from the undo queue, don't count it separately
        counts = list(self.mw.col.sched.counts())
    else:
        counts = list(self.mw.col.sched.counts(self.card))
    return (idx == 0 and counts[0] < 1)


def laterNotNow(self, showAnswer):
    ret = '<style>td{vertical-align:bottom;}' +\
        'html, body, table { width: 100%; height: 100%;' +\
        ' margin: 0px; padding: 0px; box-sizing: content-box; }' +\
        '/*html,*/ body { overflow: hidden; } ' +\
        '</style>'

    if not NO_STYLES:
        ret += '<style>' +\
            'td button{font-size:large;}' +\
            'td.x button{font-size:x-large;color:#888;}' +\
            'td.xx button{font-size:xx-large;}' +\
            '</style>'

    if not NO_STYLES and FLAT_BUTTONS:
        ret += '<style>' +\
            'td.esc,td.xxx,td.stat{border:none;}' +\
            'td.esc button, td.xxx button, td.stat button {border:none;}' +\
            '/*td.stat,td.stat button{background-color:Ivory;}*/' +\
            'td.xxx, td.xxx button {background-color:aliceblue;}' +\
            'td.esc, td.esc button {background-color:whitesmoke;}' +\
            'td.but1, td.but1 button {background-color:#D72D2E;}' +\
            'td.but2, td.but2 button {background-color:#465A65;}' +\
            'td.but3, td.but3 button {background-color:#4CB050;}' +\
            'td.but4, td.but4 button {background-color:#03A9F5;}' +\
            'td.but button span, td.but button b, td.but, ' +\
            'td.but button {color:#ffFFff!important;border:none;}' +\
            'td.but button:focus {outline: orange 1px dashed;}' +\
            '</style>'

    if not NO_STYLES and FLAT_BUTTONS and (swAdded or not HIDE_LATER):
        ret += '<style>' +\
            'td.esc,td.xxx,td.stat{border-left:solid 1px silver;}' +\
            'td:first-child.stat{border-left:none;}' +\
            '</style>'

    if not NO_STYLES and USE_INTERVALS_AS_LABELS and FLAT_BUTTONS:
        ret += '<style>' +\
            '.stattxt, .nobold {display:none;}' +\
            ' button { width: 100%; height: 100%;} ' +\
            '</style>'

    ret += '<table cellpadding=0 cellspacing=0 width=100%><tr>'

    if HIDE_LATER:
        return ret

    ret = ret.replace('%', '%%') +\
        '<td align=center class="x esc" style="padding-right:.35em;" ' +\
        """onclick="py.link('ease%d');"><span class="stattxt">%s</span>""" +\
        '''<button title=" %s " onclick="py.link('ease%d');" ''' +\
        'style="width:99%%;%s">%s</button></td>'  # <td>&nbsp;</td>

    if showAnswer:
        if self.mw.col.conf['dueCounts']:
            retv = True
        else:
            retv = False
    else:
        if self.mw.col.conf['estTimes']:
            retv = True
        else:
            retv = False
    if USE_INTERVALS_AS_LABELS:
        retv = False

    if retv:
        return ret % (NOT_NOW_BASE, MSG[lang]['later'],
                      _("Shortcut key: %s") % (HOTKEY['later_not_now']),
                      NOT_NOW_BASE,
                      'color:' + black + ';', (MSG[lang]['later_not_now']))
    else:
        return ret % (NOT_NOW_BASE, "",
                      _("Shortcut key: %s") % (HOTKEY['later_not_now']),
                      NOT_NOW_BASE,
                      'color:' + black + ';', (MSG[lang]['later']))


def myShowAnswerButton(self, _old):
    _old(self)
    set_timeoutA(self)

    if newRemaining(self):
        self.mw.moveToState('overview')
    self._bottomReady = True
    if not self.typeCorrect:
        self.bottom.web.setFocus()

    if USE_INTERVALS_AS_LABELS:
        middle = laterNotNow(self, True) + (
            '<td align=center style="width:%s;" class="xx xxx"' +
            ''' onclick="py.link('ans');"><span''' +
            ' class="stattxt">&nbsp;</span><button %s id=ansbut ' +
            '''style="width:100%%;%s" onclick="py.link('ans');" ''' +
            '>%s</button></td>' +
            '</tr></table>') % (
                BEAMS4,
                ' title=" ' + (_('Shortcut key: %s') % _('Space')) + ' " ',
                ' color:' + black + ';', self._remaining())
    else:
        middle = laterNotNow(self, True) + (
            '<td align=center style="width:%s;" class="xx xxx"' +
            ' onclick="py.link(\'ans\');"><span' +
            ' class="stattxt">%s</span><button %s id=ansbut ' +
            '''style="width:100%%;%s" onclick="py.link('ans');" ''' +
            '>%s</button></td>' +
            '</tr></table>') % (
                BEAMS4, self._remaining(),
                ' title=" ' + (_('Shortcut key: %s') % _('Space')) + ' " ',
                ' color:' + black + ';', _('Show Answer'))

    # place it in a table so it has the same top margin as the ease buttons
    # middle = '<!div align=center style='width:%s!important;'>%s</div>' %
    # (BEAMS4, middle)
    if self.card.shouldShowTimer():
        maxTime = self.card.timeLimit() / 1000
    else:
        maxTime = 0
    self.bottom.web.eval('showQuestion(%s,%d);' % (
        json.dumps(middle), maxTime))
    return True

if old_addons2delete == '':
    aqt.reviewer.Reviewer._showAnswerButton = anki.hooks.wrap(
        aqt.reviewer.Reviewer._showAnswerButton, myShowAnswerButton, 'around')

    # This wraps existing Reviewer._answerCard function.

    def answer_card_intercepting(self, actual_ease, _old):
        ease = actual_ease
        if actual_ease == NOT_NOW_BASE:
            self.nextCard()
            return True
        elif actual_ease < NOT_NOW_BASE:
            count = self.mw.col.sched.answerButtons(self.card)
            try:
                ease = remaps[remap][count][ease]
            except (KeyError, IndexError):
                pass
            return _old(self, ease)
        else:
            was_new_card = self.card.type in (0, 1, 2, 3)
            is_extra_button = was_new_card and \
                actual_ease >= INTERCEPT_EASE_BASE
            if is_extra_button:
                # Make sure this is as expected.
                # assert self.mw.col.sched.answerButtons(self.card) == 3
                # So this is one of our buttons.
                # First answer the card as if 'Easy' clicked.
                ease = 3
                # We will need this to reschedule it.
                prev_card_id = self.card.id
                prev_card_factor = self.card.factor
                #
                buttonItem = extra_buttons[actual_ease - INTERCEPT_EASE_BASE]
                # Do the reschedule.
                self.mw.checkpoint(_('Reschedule card'))
                # self.mw.col.sched.reschedCards([prev_card_id],
                #   buttonItem['ReschedMin'], buttonItem['ReschedMax'])
                _reschedCards(
                    self.mw.col.sched, [prev_card_id],
                    buttonItem['ReschedMin'], buttonItem['ReschedMax'],
                    indi=prev_card_factor)
                aqt.utils.tooltip(
                    '<center>Rescheduled:' + '<br>' +
                    buttonItem['Description'] + '</center>')

                SwapTag = SWAP_TAG
                if SwapTag:
                    SwapTag += unicode(self.mw.reviewer.card.ord + 1)
                    note = self.mw.reviewer.card.note()
                    if not note.hasTag(SwapTag):
                        note.addTag(SwapTag)
                        note.flush()  # never forget to flush

                self.mw.reset()
                return True
            else:
                ret = _old(self, ease)
                return ret

    aqt.reviewer.Reviewer._answerCard = anki.hooks.wrap(
        aqt.reviewer.Reviewer._answerCard,
        answer_card_intercepting, 'around')
# 'before' does not working as intended cause ease is changing inside AKR


# to remove <span class=nobold>
def _bottomTimes(self, i):
    if not self.mw.col.conf['estTimes']:
        return '&nbsp;'
    txt = self.mw.col.sched.nextIvlStr(self.card, i, True) or '&nbsp;'
    return txt.replace("<", "&lt;")


# always show interval despite user's preferences
def _bottomTime(self, i):
    # if not self.mw.col.conf['estTimes']:
    #    return '&nbsp;'
    txt = self.mw.col.sched.nextIvlStr(self.card, i, True) or '&nbsp;'
    return txt.replace("<", "&lt;")


def BTN_LBL(title):
    if NO_STYLES:
        return '<b style="color:%s;">' % (BTN_CLR[title]) + \
            _(title) + '</b>'
    elif NO_SMILES:
        return '<span style="color:%s;">' % (BTN_CLR[title]) + \
            BTN_LABL[lang][title] + '</span>'
    else:
        return BUTTON_LABEL[title]


# Replace _answerButtonList method
def answerButtonList(self):
    if remap == 'All':
        l = ((1, '' + BTN_LBL('Again') + '', BEAMS1),)
        cnt = self.mw.col.sched.answerButtons(self.card)
    elif remap == 'Again':
        l = ((1, '' + BTN_LBL('Again') + '', BEAMS4),)
        cnt = 1
        return l
    else:
        l = ((1, '' + BTN_LBL('Again') + '', BEAMS2),)
        cnt = 2
    if cnt == 2:
        if remap == 'All':
            return l + ((2, '' + BTN_LBL('Good') + '', BEAMS3),)
        else:
            return l + ((2, '' + BTN_LBL(remap) + '', BEAMS2),)
        # the comma at the end is mandatory, a subtle bug occurs without it
    elif cnt == 3:
        return l + ((2, '' + BTN_LBL('Good') + '', BEAMS2),
                    (3, '' + BTN_LBL('Easy') + '', BEAMS1))
    else:
        return l + ((2, '' + BTN_LBL('Hard') + '', BEAMS1),
                    (3, '' + BTN_LBL('Good') + '', BEAMS1),
                    (4, '' + BTN_LBL('Easy') + '', BEAMS1))
# all buttons are with coloured text
# and have an equal width with buttons in Night Mode


def answerCard_tooltip(self, ease):
    l = self._answerButtonList()
    a = [item for item in l if item[0] == ease]
    if len(a) > 0:
        return a[0][1]
    else:
        return ''


def myAnswerButtons(self, _old):
    _old(self)
    set_timeoutQ(self)

    times = []
    default = self._defaultEase()

    cnt = self.mw.col.sched.answerButtons(self.card)

    def but(i, label, beam):
        if i == default:
            extra = 'id=defease'
        else:
            extra = ''
        # due = self._buttonTime(i)

        j = i
        cnt = self.mw.col.sched.answerButtons(self.card)
        if remap == 'All':
            if cnt == 2:
                if i == 2:
                    j = 3
            elif cnt == 3:
                if i == 2:
                    j = 3
                if i == 3:
                    j = 4
            due = _bottomTimes(self, i)
            ij = j
        else:
            ij = j
            if i == 2:
                if remap == 'Good':
                    ij = 3
                    if cnt == 4:
                        j = 3
                    else:
                        j = 2
                if remap == 'Easy':
                    ij = 4
                    j = cnt
            due = _bottomTimes(self, j)

        text_label = anki.utils.stripHTML(label)
        if text_label != answerCard_tooltip(self, i):
            text_label += '   ' + answerCard_tooltip(self, i)
        text_label += '   '

        if USE_INTERVALS_AS_LABELS:
            return '''
<td align=center class="but but%s xx" style="width:%s;"
 onclick="py.link('ease%d');"><span class="stattxt">&nbsp;</span
><button %s title="%s" style="width:99%%;%s" onclick="py.link('ease%d');"
><b>%s</b></button></td>''' % (
                        ij, beam, j, extra,
                        ('  ' + text_label + due +
                         ' -- ' + _('Shortcut key: %s') % j +
                         '  ').replace(' ', ' '),
                        "color:"+BUTTON_COLOR[remap][j]+";", j, due)
        else:
            return '''
<td align=center class="but but%s xx" style="width:%s;"
 onclick="py.link('ease%d');"><span class="stattxt">%s</span
><button %s title="%s" style="width:99%%;%s" onclick="py.link('ease%d');"
>%s</button></td>''' % (ij, beam, j, due, extra,
                        ('  ' + text_label + due +
                         ' -- ' + _('Shortcut key: %s') % j +
                         '  ').replace(' ', ' '),
                        "", j, label)

    buf = laterNotNow(self, False)

    for ease, lbl, beams in answerButtonList(self):
        buf += but(ease, lbl, beams)

    # swAdded start ====>
    # Only for cards in the new queue
    if swAdded and self.card.type in (0, 1, 2, 3):  # New, Learn, Day learning
        # Check that the number of answer buttons is as expected.
        #  assert self.mw.col.sched.answerButtons(self.card) == 3
        # python lists are 0 based
        for i, buttonItem in enumerate(extra_buttons):
            if USE_INTERVALS_AS_LABELS:
                buf += '''
<td align=center class="x xxx"
 onclick="py.link('ease%d');"><span class="stattxt">&nbsp;</span
><button title="%s" onclick="py.link('ease%d');">\
%s</button></td>''' % (i + INTERCEPT_EASE_BASE,
                       _('Shortcut key: %s') % buttonItem['ShortCut'],
                       i + INTERCEPT_EASE_BASE,
                       buttonItem['Description'])
            else:
                buf += '''
<td align=center class="x xxx"
 onclick="py.link('ease%d');"><span class="stattxt">%s</span
><button title="%s" onclick="py.link('ease%d');">\
%s</button></td>''' % (
                    i + INTERCEPT_EASE_BASE,
                    buttonItem['Description'],
                    _('Shortcut key: %s') % buttonItem['ShortCut'],
                    i + INTERCEPT_EASE_BASE,
                    buttonItem['Label'])
    # swAdded end   ====>

    return (
        buf + "</tr></table>" +
        "<script>$(function(){$('#defease').focus();});</script>")


def answer_card_intercepting_WTF(self, actual_ease, _old):
    ease = actual_ease
    if actual_ease >= NOT_NOW_BASE:
        self.nextCard()
        return True
    else:
        return _old(self, ease)


def save_wide_buttons():
    aqt.mw.pm.profile['wide_big_buttons'] = (
        more_action.isChecked())
    aqt.mw.pm.profile['remap_buttons'] = (
        remap)
    aqt.mw.pm.profile['hide_later'] = (
        HIDE_LATER)
    aqt.mw.pm.profile['swAdded'] = (
        swAdded)
    aqt.mw.pm.profile['NO_SMILES'] = (
        NO_SMILES)
    aqt.mw.pm.profile['NO_STYLES'] = (
        NO_STYLES)
    aqt.mw.pm.profile['ctb_edit_more'] = (
        EDIT_MORE_BUTTONS)
    aqt.mw.pm.profile['flat_buttons'] = (
        FLAT_BUTTONS)


def load_wide_buttons():
    global USE_INTERVALS_AS_LABELS, more_action, remap, act, HIDE_LATER,\
        hide_later_action, EDIT_MORE_BUTTONS, edit_more_action, swAdded,\
        swAdded_action, NO_STYLES, styles_action, FLAT_BUTTONS, flat_action,\
        NO_SMILES, smiles_action
    try:
        remap = aqt.mw.pm.profile['remap_buttons']
    except KeyError:
        remap = 'All'
    try:
        USE_INTERVALS_AS_LABELS = aqt.mw.pm.profile['wide_big_buttons']
    except KeyError:
        USE_INTERVALS_AS_LABELS = False
    more_action.setChecked(USE_INTERVALS_AS_LABELS)

    if remap == 'All':
        act[0].setChecked(True)
    if remap == 'Again':
        act[1].setChecked(True)
    if remap == 'Hard':
        act[2].setChecked(True)
    if remap == 'Good':
        act[3].setChecked(True)
    if remap == 'Easy':
        act[4].setChecked(True)

    try:
        EDIT_MORE_BUTTONS = aqt.mw.pm.profile['ctb_edit_more']
    except KeyError:
        EDIT_MORE_BUTTONS = True

    edit_more_action.setChecked(not EDIT_MORE_BUTTONS)
    edit_more_proc()

    try:
        HIDE_LATER = aqt.mw.pm.profile['hide_later']
    except KeyError:
        HIDE_LATER = False

    hide_later_action.setChecked(HIDE_LATER)

    try:
        swAdded = aqt.mw.pm.profile['swAdded']
    except KeyError:
        swAdded = True

    swAdded_action.setChecked(not swAdded)

    try:
        NO_SMILES = aqt.mw.pm.profile['NO_SMILES']
    except KeyError:
        NO_SMILES = False

    smiles_action.setChecked(NO_SMILES)

    try:
        NO_STYLES = aqt.mw.pm.profile['NO_STYLES']
    except KeyError:
        NO_STYLES = False

    styles_action.setChecked(NO_STYLES)

    try:
        FLAT_BUTTONS = aqt.mw.pm.profile['flat_buttons']
    except KeyError:
        FLAT_BUTTONS = True

    flat_action.setChecked(FLAT_BUTTONS)

    if NO_STYLES or USE_INTERVALS_AS_LABELS:
        smiles_action.setEnabled(False)

##

try:
    aqt.mw.addon_view_menu
except AttributeError:
    aqt.mw.addon_view_menu = QMenu(MSG[lang]['View'], aqt.mw)
    aqt.mw.form.menubar.insertMenu(
        aqt.mw.form.menuTools.menuAction(), aqt.mw.addon_view_menu)

if old_addons2delete == '':
    anki.hooks.addHook("unloadProfile", save_wide_buttons)
    anki.hooks.addHook("profileLoaded", load_wide_buttons)

    try:
        aqt.mw.huge_buttons
    except AttributeError:
        aqt.mw.huge_buttons = QMenu(MSG[lang]['HUGE_buttons'], aqt.mw)
        aqt.mw.huge_buttons.setIcon(
            QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'push_button.png')))
        aqt.mw.addon_view_menu.addMenu(aqt.mw.huge_buttons)

    aqt.mw.huge_buttons.addSeparator()

    def onSmiles():
        global NO_SMILES
        NO_SMILES = smiles_action.isChecked()

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    def onStyles():
        global NO_STYLES, FLAT_BUTTONS, flat_action, smiles_action
        NO_STYLES = styles_action.isChecked()
        if NO_STYLES:
            flat_action.setChecked(False)
            FLAT_BUTTONS = False
            smiles_action.setEnabled(False)
        else:
            smiles_action.setEnabled(True)

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    def flat_proc():
        global NO_STYLES, FLAT_BUTTONS, styles_action

        if flat_action.isChecked():
            styles_action.setChecked(False)
            NO_STYLES = False
            FLAT_BUTTONS = True
        else:
            FLAT_BUTTONS = False

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    def more_proc():
        global USE_INTERVALS_AS_LABELS, smiles_action
        if more_action.isChecked():
            USE_INTERVALS_AS_LABELS = True
            smiles_action.setEnabled(False)
        else:
            USE_INTERVALS_AS_LABELS = False
            smiles_action.setEnabled(True)

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    smiles_action = QAction(MSG[lang]['no_smiles'], aqt.mw)
    smiles_action.setShortcut(HOTKEY['no_smiles'])
    smiles_action.setCheckable(True)
    smiles_action.setCheckable(True)
    smiles_action.setChecked(NO_SMILES)
    aqt.mw.connect(smiles_action, SIGNAL('triggered()'), onSmiles)

    styles_action = QAction(MSG[lang]['no_styles'], aqt.mw)
    styles_action.setShortcut(HOTKEY['no_styles'])
    styles_action.setCheckable(True)
    styles_action.setChecked(NO_STYLES)
    aqt.mw.connect(styles_action, SIGNAL('triggered()'), onStyles)

    flat_action = QAction(MSG[lang]['flat_buttons'], aqt.mw)
    flat_action.setShortcut(HOTKEY['flat_buttons'])
    flat_action.setCheckable(True)
    flat_action.setChecked(FLAT_BUTTONS)
    aqt.mw.connect(flat_action, SIGNAL('triggered()'), flat_proc)

    more_action = QAction(MSG[lang]['no_labels'], aqt.mw)
    more_action.setShortcut(HOTKEY['no_labels'])
    more_action.setCheckable(True)
    more_action.setChecked(USE_INTERVALS_AS_LABELS)
    aqt.mw.connect(more_action, SIGNAL('triggered()'), more_proc)

    aqt.reviewer.Reviewer._answerButtons = anki.hooks.wrap(
        aqt.reviewer.Reviewer._answerButtons, myAnswerButtons, 'around')

    def onEscape():
        aqt.mw.reviewer.nextCard()

    try:
        aqt.mw.addon_cards_menu
    except AttributeError:
        aqt.mw.addon_cards_menu = QMenu(MSG[lang]['Cards'], aqt.mw)
        aqt.mw.form.menubar.insertMenu(
            aqt.mw.form.menuTools.menuAction(), aqt.mw.addon_cards_menu)

    escape_action = QAction(aqt.mw)
    escape_action.setText(MSG[lang]['Later, not now'])
    escape_action.setShortcut(HOTKEY['later_not_now'])
    escape_action.setEnabled(False)
    aqt.mw.connect(escape_action, SIGNAL('triggered()'), onEscape)

    aqt.mw.addon_cards_menu.addAction(escape_action)

    aqt.mw.deckBrowser.show = anki.hooks.wrap(
        aqt.mw.deckBrowser.show, lambda: escape_action.setEnabled(False))
    aqt.mw.overview.show = anki.hooks.wrap(
        aqt.mw.overview.show, lambda: escape_action.setEnabled(False))
    aqt.mw.reviewer.show = anki.hooks.wrap(
        aqt.mw.reviewer.show, lambda: escape_action.setEnabled(True))

    def setup_menu():
        # Add a submenu to a view menu.
        # Add a submenu that lists the available answer buttons
        global act_all, act_hard, act_good, act_easy

        aqt.mw.extra_class_submenu = QMenu(
            '&'+MSG[lang]['HardGoodEasy'], aqt.mw)
        aqt.mw.extra_class_submenu.setIcon(
            QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'push_button.png')))

        aqt.mw.huge_buttons.addAction(flat_action)
        aqt.mw.huge_buttons.addAction(styles_action)
        aqt.mw.huge_buttons.addMenu(aqt.mw.extra_class_submenu)
        aqt.mw.huge_buttons.addAction(more_action)
        aqt.mw.huge_buttons.addAction(smiles_action)
        aqt.mw.huge_buttons.addSeparator()

        def set_buttons(parm_btn, parm_act):
            global remap
            remap = parm_btn

            rst = aqt.mw.reviewer.state == 'answer'
            aqt.mw.reset()
            if rst:
                aqt.mw.reviewer._showAnswerHack()

        def setup_ag(parm_msg, parm_btns, parm_chk, parm_act, n):
            parm_act[n] = action_group.addAction(
                QAction(parm_msg, aqt.mw, checkable=True))
            parm_act[n].setChecked(parm_chk)
            parm_act[n].setShortcut(HOTKEY[parm_btns])
            aqt.mw.extra_class_submenu.addAction(parm_act[n])
            aqt.mw.connect(parm_act[n], SIGNAL("triggered()"),
                           lambda: set_buttons(parm_btns, parm_act[n]))

        action_group = QActionGroup(aqt.mw, exclusive=True)

        setup_ag(MSG[lang]['HardGoodEasy'], 'All', remap == 'All', act, 0)

        aqt.mw.extra_class_submenu.addSeparator()

        setup_ag(MSG[lang]['Again'], 'Again', remap == 'Again', act, 1)
        setup_ag(MSG[lang]['AgainHard'], 'Hard', remap == 'Hard', act, 2)
        setup_ag(MSG[lang]['AgainGood'], 'Good', remap == 'Good', act, 3)
        setup_ag(MSG[lang]['AgainEasy'], 'Easy', remap == 'Easy', act, 4)

    setup_menu()

    def onHideLater():
        global HIDE_LATER
        HIDE_LATER = hide_later_action.isChecked()

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    hide_later_action = QAction(aqt.mw)
    hide_later_action.setText(
        MSG[lang]['Hide button: '] + ' ' + MSG[lang]['Later, not now'])
    hide_later_action.setShortcut(HOTKEY['hide_later'])
    hide_later_action.setCheckable(True)
    aqt.mw.connect(hide_later_action, SIGNAL('triggered()'), onHideLater)
    aqt.mw.huge_buttons.addAction(hide_later_action)

    ##

    EDIT_MORE_BUTTONS = False  # True  #

    MORE_EDIT = " td.stat button { visibility: hidden; } "
    EDIT_MORE = " td\.stat button \{ visibility\: hidden\; \} "

    MORE_EDIT = " td.stat { display: none; } "
    EDIT_MORE = " td\.stat \{ display\: none\; \} "

    def initEditMore(editMore):
        global EDIT_MORE_BUTTONS
        EDIT_MORE_BUTTONS = editMore
        if not editMore:
            aqt.mw.reviewer._bottomCSS += MORE_EDIT
        else:
            aqt.mw.reviewer._bottomCSS = re.sub(
                EDIT_MORE, "", aqt.mw.reviewer._bottomCSS)

    initEditMore(EDIT_MORE_BUTTONS)

    def edit_more_proc():
        global EDIT_MORE_BUTTONS
        EDIT_MORE_BUTTONS = edit_more_action.isChecked()

        initEditMore(not EDIT_MORE_BUTTONS)

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    edit_more_action = QAction(
        MSG[lang]['Hide buttons'] + MSG[lang]['Edit'] + ' ' +
        MSG[lang]['More'], aqt.mw)
    edit_more_action.setShortcut(HOTKEY['HideButtons'])
    edit_more_action.setCheckable(True)
    edit_more_action.setChecked(not EDIT_MORE_BUTTONS)
    aqt.mw.connect(edit_more_action, SIGNAL('triggered()'), edit_more_proc)
    aqt.mw.huge_buttons.addAction(edit_more_action)

    def swAdded_proc():
        global swAdded
        swAdded = not swAdded_action.isChecked()

        rst = aqt.mw.reviewer.state == 'answer'
        aqt.mw.reset()
        if rst:
            aqt.mw.reviewer._showAnswerHack()

    swAdded_action = QAction(
        MSG[lang]['no_extra_buttons'], aqt.mw)
    swAdded_action.setShortcut(HOTKEY['no_extra_buttons'])
    swAdded_action.setCheckable(True)
    swAdded_action.setChecked(not EDIT_MORE_BUTTONS)
    aqt.mw.connect(swAdded_action, SIGNAL('triggered()'), swAdded_proc)
    aqt.mw.huge_buttons.addAction(swAdded_action)

    def about_addon():
        """
        Show "About addon" message popup window.
        """
        aa_about_box = QMessageBox()
        aa_about_box.setText(
            __addon__ + "   " + __version__ + "\n" + __doc__)
        aa_width, aa_height = (1024, 768)
        # aa_width, aa_height = (1920, 1080)
        aa_left = (aa_width-480)/2
        aa_right = (aa_height-640)/2
        aa_about_box.setGeometry(aa_left, aa_right, 480, 640)
        aa_about_box.setWindowTitle(MSG[lang]['aa'] + __addon__)
        aa_about_box.exec_()

    about_addon_action = QAction(MSG[lang]['aa'] + __addon__, aqt.mw)
    about_addon_action.setIcon(
        QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'money.png')))
    aqt.mw.connect(about_addon_action, SIGNAL('triggered()'), about_addon)
    aqt.mw.huge_buttons.addSeparator()
    aqt.mw.huge_buttons.addAction(about_addon_action)

    def go_edit_current():
        """Edit the current card when there is one."""
        try:
            aqt.mw.onEditCurrent()
        except AttributeError:
            pass

##

    def onAltCloze(self, delta):
        # check that the model is set up for cloze deletion
        if not re.search('{{(.*:)*cloze:',
                         self.note.model()['tmpls'][0]['qfmt']):
            if self.addMode:
                aqt.utils.tooltip(
                    _("Warning, cloze deletions will not work until " +
                      "you switch the type at the top to Cloze."))
            else:
                aqt.utils.showInfo(_("""\
    To make a cloze deletion on an existing note, you need to change it \
    to a cloze type first, via Edit>Change Note Type."""))
                return
        # find the highest existing cloze
        highest = 0
        for name, val in self.note.items():
            m = re.findall("\{\{c(\d+)::", val)
            if m:
                highest = max(highest, sorted([int(x) for x in m])[-1])
        # reuse last?
        # if not self.mw.app.keyboardModifiers() & Qt.AltModifier:
        highest += delta
        # must start at 1
        highest = max(1, highest)
        self.web.eval("wrap('{{c%d::', '}}');" % highest)

    def setupButtonz(self):
        s = QShortcut(
            QKeySequence(HOTKEY["next_cloze"]), self.parentWindow)
        s.connect(s, SIGNAL('activated()'), self.onCloze)

        s = QShortcut(
            QKeySequence(HOTKEY["same_cloze"]), self.parentWindow)
        s.connect(s, SIGNAL('activated()'), self.onCloze)

        s = QShortcut(QKeySequence(
            HOTKEY['same_without_Alt']), self.parentWindow)
        s.connect(s, SIGNAL('activated()'), lambda: onAltCloze(self, 0))

        s = QShortcut(QKeySequence(
            HOTKEY["next_closure"]), self.parentWindow)
        s.connect(s, SIGNAL('activated()'), self.onCloze)

        s = QShortcut(QKeySequence(
            HOTKEY["same_closure"]), self.parentWindow)
        s.connect(s, SIGNAL('activated()'), self.onCloze)

        s = QShortcut(QKeySequence(HOTKEY["LaTeX"]), self.widget)
        s.connect(s, SIGNAL("activated()"), self.insertLatex)
        s = QShortcut(QKeySequence(HOTKEY["LaTeX$"]), self.widget)
        s.connect(s, SIGNAL("activated()"), self.insertLatexEqn)
        s = QShortcut(QKeySequence(HOTKEY["LaTeX$$"]), self.widget)
        s.connect(s, SIGNAL("activated()"), self.insertLatexMathEnv)

    aqt.editor.Editor.setupButtons = anki.hooks.wrap(
        aqt.editor.Editor.setupButtons, setupButtonz)

#

"""
Adds extra buttons to the Reviewer window for new cards
https://ankiweb.net/shared/info/468253198

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Modified by Glutanimate, 2016

WARNING: this addon uses private methods to achieve its goals. Use at your
own risk and keep backups.

What it does: Adds anywhere between 1 to 4 new buttons to the review window
when reviewing a new card. The new buttons function like the existing "Easy"
button, but in addition, they reschedule the card to different interval,
 which is randomly assigned between a lower and upper limit that is preset
  by the user (see below).

By default 3 buttons are added, with intervals: "3-4d" , "5-7d" , "8-15d"
This can be changed below.

I wanted this addon because many of my new cards do not need to be
"Learned" as I created and added them myself, typically an hour or so before
my first review session. I often add around 100-200 new cards per day, all on
a related topic, and this addon allows me to spread the next review
 of the new cards that don't need learning out in time.

How it works: This addon works by intercepting the creation of the reviewer
  buttons and adds up to 4 extra buttons to the review window.
   The answer function
  is wrapped and the ease parameter is checked to see if it one of the new
  buttons. If it is, the standard answer function is used to add the card
  as an easy card, and then the browser 'reschedCards' function is used
  to reschedule it to the desired interval.

In summary, this functions as if you click the "Easy" button on a new card,
  and then go to the browser and reschedule the card.

Warning: This completely replaces the Reviewer._answerButtons fn,
 so any changes
   to that function in future updates will be lost. Could ask for a hook?
Warning: buyer beware ... The author is not a python, nor a qt programmer

Support: None. Use at your own risk. If you do find a problem please email me
at steveawa@gmail.com

Setup data
List of dicts, where each item of the list (a dict) is the data
for a new button.
This can be edited to suit, but there can not be more than 4 buttons.

Description ... appears above the button
Label ... the label of the button
ShortCut ... the shortcut key for the button

ReschedMin ... same as the lower number
    in the Browser's "Edit/Rescedule" command
ReschedMax ... same as the higher number
    in the Browser's "Edit/Rescedule" command
"""

##

if old_addons2delete == '':

    def keyHandler(self, evt, _old):
        key = unicode(evt.text())
        if self.state == 'answer':
            for i, buttonItem in enumerate(extra_buttons):
                if key == buttonItem['ShortCut']:
                    # early exit ok in python?
                    return self._answerCard(i + INTERCEPT_EASE_BASE)
        return _old(self, evt)

    aqt.reviewer.Reviewer._keyHandler = anki.hooks.wrap(
        aqt.reviewer.Reviewer._keyHandler, keyHandler, 'around')

##############
# • Flip-flop


def go_question():
    if aqt.mw.state == 'review':
        if (aqt.mw.reviewer.state == 'answer' or
                aqt.mw.reviewer.state == 'question'):
            anki.sound.stopMplayer()
            aqt.mw.reviewer._showQuestion()


def go_answer():
    if aqt.mw.state == 'review':
        if aqt.mw.reviewer.state == 'question':
            anki.sound.stopMplayer()
            aqt.mw.reviewer._showAnswer()

PageUp_icon = QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'PageUp.png'))
PageDown_icon = QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'PageDown.png'))

#
if FLIP_FLOP:

    show_question_auction = QAction(aqt.mw)
    show_question_auction.setText(MSG[lang]['showFrontSide'])
    show_question_auction.setShortcut(QKeySequence(HOTKEY['showFrontSide']))
    if ANKI_MENU_ICONS:
        show_question_auction.setIcon(PageUp_icon)
    aqt.mw.connect(show_question_auction, SIGNAL('triggered()'), go_question)

    show_answer_auction = QAction(aqt.mw)
    show_answer_auction.setText(MSG[lang]['showBackSide'])
    show_answer_auction.setShortcut(HOTKEY['showBackSide'])
    if ANKI_MENU_ICONS:
        show_answer_auction.setIcon(PageDown_icon)
    aqt.mw.connect(show_answer_auction, SIGNAL('triggered()'), go_answer)

    aqt.mw.form.menuEdit.addSeparator()
    aqt.mw.form.menuEdit.addAction(show_question_auction)
    aqt.mw.form.menuEdit.addAction(show_answer_auction)
    aqt.mw.form.menuEdit.addSeparator()

##

mw_addon_view_menu_exists = hasattr(aqt.mw, 'addon_view_menu')

if FLIP_FLOP and mw_addon_view_menu_exists:

    show_question_aktion = QAction(aqt.mw)
    show_question_aktion.setText(MSG[lang]['viewFrontSide'])
    show_question_aktion.setShortcut(HOTKEY['viewFrontSide'])
    if ANKI_MENU_ICONS:
        show_question_aktion.setIcon(PageUp_icon)
    aqt.mw.connect(show_question_aktion, SIGNAL('triggered()'), go_question)

    show_answer_aktion = QAction(aqt.mw)
    show_answer_aktion.setText(MSG[lang]['viewBackSide'])
    show_answer_aktion.setShortcut(HOTKEY['viewBackSide'])
    if ANKI_MENU_ICONS:
        show_answer_aktion.setIcon(PageDown_icon)
    aqt.mw.connect(show_answer_aktion, SIGNAL('triggered()'), go_answer)

    aqt.mw.addon_view_menu.addSeparator()
    aqt.mw.addon_view_menu.addAction(show_question_aktion)
    aqt.mw.addon_view_menu.addAction(show_answer_aktion)
    aqt.mw.addon_view_menu.addSeparator()

##

if ZERO_KEY_TO_SHOW_ANSWER:
    # -------------------------------
    # key handler for reviewer window
    # -------------------------------
    def newKeyHandler(self, evt):
        key = evt.key()
        # text = unicode(evt.text())
        Keys0 = [Qt.Key_0, Qt.Key_Insert]  # Show Answer
        if key in Keys0:
            if self.state == 'question':
                go_answer()
            else:
                go_question()
    aqt.reviewer.Reviewer._keyHandler = anki.hooks.wrap(
        aqt.reviewer.Reviewer._keyHandler, newKeyHandler, 'before')

##

fld1st = _('Front')  # Вопрос
fld2nd = _('Back')  # Ответ


def JustDoIt(note, ecf, tip=True):
    global fld1st, fld2nd
    """
    if not (aqt.mw.reviewer.state == 'question'
        or aqt.mw.reviewer.state == 'answer'):
     showCritical('''Обмен в списке колод или в окне колоды невозможен,
      <br>только при просмотре (заучивании) карточек.''' \
        if lang=='ru' else '''Swap fields is available only for cards,<br>
 not for decks panel nor deck overview as well.''')
     return
    if not hasattr(aqt.mw.reviewer.card,'model'):
     showCritical('Извините, конечно, но пока делать просто нечего!' \
        if lang=='ru' else 'Oops, <s>I did it again!</s> ' +
        'there is <b>nothing to do</b> yet!')
     return
    """
    if note.model()['type'] == MODEL_CLOZE:
        aqt.utils.showCritical(
            '''<center>Обмен полей для типа записей
<b>с пропусками</b><br> не поддерживается. Только вручную.</center>'''
            if lang == 'ru' else '''<div style="text-align:center;">
It's unable to swap fields of CLOZE note type automatically.
<br>Please, do it manually by yourself.</div>''')

        # Unfortunately, style="text-align:center;" does not work here.
        # But <center> works.

    elif note.model()['type'] == MODEL_STD:
        fldn = note.model()['flds']
        fldl = len(note.fields)

        audioSound = False
        for fld in fldn:
            if fld['name'].lower() == 'audio' or\
               fld['name'].lower() == 'sound':
                audioSound = True
                break

        fnd1st = False
        fnd2nd = False

        if ecf is not None:
            fnd = fldn[ecf]['name']
            for lst in fldlst:
                if CASE_SENSITIVE:
                    found = fnd == lst[0]
                else:
                    found = fnd.lower() == lst[0].lower()
                if found:
                    fnd1st = True
                    fld1st = fnd
                    fnd2nd = True
                    fld2nd = lst[1]
                    break
                else:
                    for lst in fldlst:
                        if CASE_SENSITIVE:
                            found = fnd == lst[1]
                        else:
                            found = fnd.lower() == lst[1].lower()
                        if found:
                            fnd1st = True
                            fld1st = lst[0]
                            fnd2nd = True
                            fld2nd = fnd
                            break

        if not fnd1st:
            for lst in fldlst:
                for fld in fldn:
                    if CASE_SENSITIVE:
                        found = fld['name'] == lst[0]
                    else:
                        found = fld['name'].lower() == lst[0].lower()
                    if found:
                        fnd1st = True
                        fld1st = fld['name']
                        break
                else:
                    continue
                break

        if not fnd2nd:
            for lst in fldlst:
                for fld in fldn:
                    if CASE_SENSITIVE:
                        found = fld['name'] == lst[1] and lst[0] == fld1st
                    else:
                        found = fld['name'].lower() == lst[1].lower() and lst[
                            0].lower() == fld1st.lower()
                    if found:
                        fnd2nd = True
                        fld2nd = fld['name']
                        break
                else:
                    continue
                break

        if fldl < 2:
            aqt.utils.showCritical(
                'У данной записи одно-единственное поле,<br>' +
                ' его просто не с чем обменивать.'
                if lang == 'ru'
                else 'It is unable to swap a note with a single field in it.')
            return

        elif fldl == 2:  # There are two fields only? Swap it anyway.
            fld1st = fldn[0]['name']
            fld2nd = fldn[1]['name']
            swap_fld = note[fld1st]
            note[fld1st] = note[fld2nd]
            note[fld2nd] = swap_fld

        elif fldl == 3 and audioSound:
            # There are three fields only? With Audio or Sound? Swap other two
            # anyway.
            fld1st = ''
            fld2nd = ''
            for fld in fldn:
                if fld['name'].lower() != 'audio' \
                        and fld['name'].lower() != 'sound' and fld1st == '':
                    fld1st = fld['name']
                if fld['name'].lower() != 'audio' \
                        and fld['name'].lower() != 'sound' and fld2nd == '' \
                        and fld['name'] != fld1st:
                    fld2nd = fld['name']
            if fld1st != '' and fld2nd != '':
                aqt.utils.showInfo(unicode(fld1st) + ' ' + unicode(fld2nd))
                swap_fld = note[fld1st]
                note[fld1st] = note[fld2nd]
                note[fld2nd] = swap_fld
            else:
                aqt.utils.showCritical(
                    '3 поля, но есть и Audio, и Sound.<br> ' +
                    'Что с чем обменивать-то тогда?')
                return

        # There are 3 (w/o Audio/Sound) or 4 or more fields?
        elif fnd1st and fnd2nd:
            # Swap fields by name if names are found in list.
            swap_fld = note[fld1st]
            note[fld1st] = note[fld2nd]
            note[fld2nd] = swap_fld

        else:
            # Otherwise swap two first fields anyway.
            fld1st = fldn[0]['name']
            fld2nd = fldn[1]['name']
            swap_fld = note[fld1st]
            note[fld1st] = note[fld2nd]
            note[fld2nd] = swap_fld

        if SWAP_TAG:
            if not note.hasTag(SWAP_TAG):
                note.addTag(SWAP_TAG)

        note.flush()  # never forget to flush

        if tip:
            aqt.utils.tooltip(
                MSG[lang]['fields_swapped'] %
                (fld1st, fld2nd), period=2000)


def JustDoItYourself():
    rst = aqt.mw.reviewer.state
    NB = aqt.mw.reviewer.card.note()
    JustDoIt(NB, None)
    aqt.mw.reset()  # refresh gui
    if rst == 'answer':
        aqt.mw.reviewer._showAnswer()  # ._showAnswerHack()


def TryItYourself(edit):
    edcufi = edit.currentField
    JustDoIt(edit.note, edcufi)
    aqt.mw.reset()  # refresh gui
    # focus field so it's saved
    edit.web.setFocus()
    edit.web.eval('focusField(%d);' % edcufi)

##

swap_action = QAction(MSG[lang]['swap_fields'] % (fld1st, fld2nd), aqt.mw)

swap_action.setShortcut(QKeySequence(HOTKEY['swap']))
swap_action.setIcon(QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'swap.png')))
aqt.mw.connect(swap_action, SIGNAL('triggered()'), JustDoItYourself)

aqt.mw.form.menuEdit.addSeparator()
aqt.mw.form.menuEdit.addAction(swap_action)
aqt.mw.form.menuEdit.addSeparator()


def swap_off():
    swap_action.setEnabled(False)


def swap_on():
    swap_action.setEnabled(True)

aqt.mw.deckBrowser.show = anki.hooks.wrap(
    aqt.mw.deckBrowser.show, swap_off)
aqt.mw.overview.show = anki.hooks.wrap(
    aqt.mw.overview.show, swap_off)
aqt.mw.reviewer.show = anki.hooks.wrap(
    aqt.mw.reviewer.show, swap_on)


def setup_buttons(editor):
    '''Add the buttons to the editor.'''
    editor._addButton(
        'swap_fields', lambda edito=editor: TryItYourself(edito),
        HOTKEY['swap'], text='Sw',
        tip=MSG[lang]['swapping'] + ' (' + HOTKEY['swap'] + ')')

# register callback function that gets executed
# after setupEditorButtons has run.
# See Editor.setupEditorButtons for details
anki.hooks.addHook('setupEditorButtons', setup_buttons)

# reset_card_scheduling.py
# https://ankiweb.net/shared/info/1432861881
# Reset card(s) scheduling information / progress
#######################################################

# Col is a collection of cards, cids are the ids of the cards to reset.


def swapSelectedNotes(self):
    ''' Resets statistics for selected cards,
    and removes them from learning queues. '''
    nids = self.selectedNotes()
    if not nids:
        return
    # Allow undo
    self.mw.checkpoint(MSG[lang]['swapping'])
    self.mw.progress.start(immediate=True)
    # Not sure if beginReset is required
    self.model.beginReset()

    # Resets selected cards in current collection
    # self.col.sched.resetCards(cids)
    # Removes card from dynamic deck?
    # self.col.sched.remFromDyn(cids)
    # Removes card from learning queues
    # self.col.sched.removeLrn(cids)

    for nid in nids:
        JustDoIt(aqt.mw.col.getNote(nid), None)
    aqt.mw.reset()  # refresh gui

    self.model.endReset()
    self.mw.progress.finish()
    # Update the main UI window to reflect changes in card status
    self.mw.reset()

"""
Anki Add-on: Create Duplicate Notes -- Duplicate Selected Notes

Select any number of cards in the card browser and duplicate their notes

Copyright: Glutanimate 2016
Based on: "Create Copy of Selected Cards" by Kealan Hobelmann
(https://ankiweb.net/shared/info/787914845)
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

To use:

1) Open the card browser
2) Select the desired cards
3) Press CTRL+ALT+C or go to Edit > Duplicate Notes

A few pointers:

- All cards generated by each note will be duplicated alongside the note
- All duplicated cards will end up in the deck of the first selected cards
- The duplicated cards should look exactly like the originals
- Tags are preserved in the duplicated notes
- Review history is NOT duplicated to the new cards (they appear as new cards)
- The notes will be marked as duplicates (because they are!)
"""


def createDuplicate(self):
    # Get deck of first selected card
    cids = self.selectedCards()
    if not cids:
        tooltip(_('No cards selected.'), period=2000)
        return
    SQL = 'select DISTINCT did from cards where id in (%s)' % (
        ','.join(str(i) for i in cids))
    dids = self.mw.col.db.list(SQL)
    if not dids:
        aqt.utils.showCritical(_('No deck ids was found.'))
        return
    for did in dids:
        deck = self.mw.col.decks.get(did)
        if deck['dyn']:
            # Skip filtered deck.
            continue
        else:
            deckName = deck['name']
            break
    else:
            # All cards are in Filtered Decks — get Name of destination deck
            # from user.
        deckName = ''

    (deckName, retv) = aqt.utils.getText(
        MSG[lang]['target_deck'], default=deckName)
    deckName = deckName.replace('"', '').replace("'", '')
    if not retv:
        tooltip('Canceled by user', period=1000)
        return
    else:
        if not deckName:  # empty input?
            # current Deck! # if it is not a Filtered deck :o)
            aqt.utils.showCritical(_('There is nothing to do!!!'))
            return

    # Create new deck with name from input box if not exists.
    deck = self.mw.col.decks.get(self.mw.col.decks.id(deckName))

    # <big> does not work here
    doSwap = aqt.utils.askUser(_(
           '<center><code>  &nbsp; After duplicating notes ' +
           'of selected cards &nbsp;  \n<br>  &nbsp; ' +
           'into <i>%s</i> &nbsp;  \n<br> <b>Swap fields</b> ' +
           'in duplicated notes? </code></center>') % (deckName))

    # Set checkpoint
    self.mw.progress.start()
    self.mw.checkpoint('Duplicate Notes')
    self.model.beginReset()

    # Copy notes
    for nid in self.selectedNotes():
        note = self.mw.col.getNote(nid)
        model = note._model

        # Assign model to deck
        self.mw.col.decks.select(deck['id'])
        self.mw.col.decks.get(deck)['mid'] = model['id']
        self.mw.col.decks.save(deck)

        # Assign deck to model
        self.mw.col.models.setCurrent(model)
        self.mw.col.models.current()['did'] = deck['id']
        self.mw.col.models.save(model)

        # Create new note
        note_copy = self.mw.col.newNote()
        # Copy tags and fields (all model fields) from original note
        note_copy.tags = note.tags
        note_copy.fields = note.fields

        if DUPE_TAG:
            if not note_copy.hasTag(DUPE_TAG):
                note_copy.addTag(DUPE_TAG)

        if doSwap:
            JustDoIt(note_copy, None, tip=False)
        else:
            # Refresh note and add to database
            note_copy.flush()
        self.mw.col.addNote(note_copy)

    # Reset collection and main window
    self.model.endReset()
    self.mw.col.reset()
    self.mw.reset()
    self.mw.progress.finish()

    aqt.utils.tooltip(_('Notes duplicated and swapped.'), period=1000)

##


def setupMenu(self):
    ''' Adds hook to the Edit menu in the note browser '''
    menu = self.form.menuEdit
    menu.addSeparator()

    swp_action = QAction(MSG[lang]['swapping'], self)
    swp_action.setShortcut(QKeySequence(HOTKEY['swap']))
    self.connect(swp_action, SIGNAL('triggered()'),
                 lambda s=self: swapSelectedNotes(self))
    menu.addAction(swp_action)

    dup_action = menu.addAction(MSG[lang]['duplicate'])
    dup_action.setShortcut(QKeySequence(HOTKEY['dupe']))
    self.connect(dup_action, SIGNAL('triggered()'),
                 lambda s=self: createDuplicate(s))

    menu.addSeparator()

anki.hooks.addHook('browser.setupMenus', setupMenu)

##


def renderOstrich(self):

    # Get due and new cards
    new = 0
    lrn = 0
    due = 0

    for tree in self.mw.col.sched.deckDueTree():
        new += tree[4]
        lrn += tree[3]
        due += tree[2]
    total = new + lrn + due

    # Get studdied cards
    cards, thetime = self.mw.col.db.first(
            """select count(), sum(time)/1000 from revlog where id > ?""",
            (self.mw.col.sched.dayCutoff - 86400) * 1000)

    cards = cards or 0
    thetime = thetime or 0

    speed = cards * 60 / max(1, thetime)
    minutes = int(total / max(1, speed))

    msgp1 = ngettext("%d card", "%d cards", cards) % cards

    buf = "" + _("Average") \
        + ": " + _("%.01f cards/minute") % (speed) + " &nbsp; " \
        + _("More") + "&nbsp;" + ngettext(
             "%s minute.", "%s minutes.", minutes) % (
                "<b>"+str(minutes)+"</b>")

    return buf


def timeboxReached(self):
    "Return (elapsedTime, reps)"
    if not self.conf['timeLim']:
        # timeboxing disabled
        return False
    elapsed = time.time() - self._startTime
    return (self.conf['timeLim'], self.sched.reps - self._startReps)


def maProc(self, elapsed):
        part1 = ngettext('%d card studied in',
                         '%d cards studied in', elapsed[1]) % elapsed[1]
        mins = int(round(elapsed[0] / 60))
        part2 = ngettext('%s minute.', '%s minutes.', mins) % mins
        aqt.utils.tooltip(
            '<big><b style=font-size:larger;color:blue;font-weight:bold;>' +
            '%s <span style=color:red>%s</span></b> <br><br> %s</big>' % (
                part1, part2, renderOstrich(self)), period=8000)


def myInfoCards(self):
    elapsed = timeboxReached(self.mw.col)
    if elapsed:
        maProc(self, elapsed)


def maNextCard(self):
    elapsed = self.mw.col.timeboxReached()
    if elapsed:
        maProc(self, elapsed)
        self.mw.col.startTimebox()

aqt.reviewer.Reviewer.nextCard = anki.hooks.wrap(
    aqt.reviewer.Reviewer.nextCard, maNextCard, 'before')

if True:
    info_action = QAction(aqt.mw)
    info_action.setText("&" + _("Timebox time limit"))
    info_action.setIcon(
        QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'clock.png')))
    info_action.setShortcut(HOTKEY['timebox'])
    info_action.setEnabled(False)

    aqt.mw.connect(
        info_action, SIGNAL("triggered()"),
        lambda: myInfoCards(aqt.mw.reviewer))

    aqt.mw.addon_view_menu.addAction(info_action)

    def info_off():
        info_action.setEnabled(False)

    def info_on():
        info_action.setEnabled(True)

    aqt.mw.deckBrowser.show = anki.hooks.wrap(
        aqt.mw.deckBrowser.show, info_off)
    aqt.mw.overview.show = anki.hooks.wrap(
        aqt.mw.overview.show, info_off)
    aqt.mw.reviewer.show = anki.hooks.wrap(
        aqt.mw.reviewer.show, info_on)

################################
# • Promt and set days interval


def _reschedCards(self, ids, imin, imax, indi=2500):
    """Put cards in review queue with a new interval in days (min, max)."""
    d = []
    t = self.today
    mod = anki.utils.intTime()
    for id in ids:
        r = random.randint(imin, imax)
        d.append(dict(id=id, due=r + t, ivl=max(1, r), mod=mod,
                      usn=self.col.usn(), fact=indi))
    self.remFromDyn(ids)
    self.col.db.executemany("""
update cards set type=2,queue=2,ivl=:ivl,due=:due,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id""", d)
    self.col.log(ids)


def _nofactorCards(self, ids, imin, imax, indi=2500):
    """Put cards in review queue with a new interval in days (min, max)."""
    d = []
    t = self.today
    mod = anki.utils.intTime()
    for id in ids:
        r = random.randint(imin, imax)
        d.append(dict(id=id, due=r + t, ivl=max(1, r), mod=mod,
                      usn=self.col.usn(), fact=indi))
    self.remFromDyn(ids)
    self.col.db.executemany("""
update cards set queue=2,ivl=:ivl,due=:due,odue=0,
usn=:usn,mod=:mod where id=:id and type=2""", d)
    self.col.db.executemany("""
update cards set type=2,queue=2,ivl=:ivl,due=:due,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id and type<>2""", d)
    self.col.log(ids)


def _refactorCards(self, ids, indi=2500):
    """Put cards in review queue with a new factor."""
    d = []
    t = self.today
    mod = anki.utils.intTime()
    for id in ids:
        d.append(dict(id=id, due=1 + t, mod=mod,
                      usn=self.col.usn(), fact=indi))
    self.remFromDyn(ids)
    self.col.db.executemany("""
update cards set queue=2,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id and type=2""", d)
    self.col.db.executemany("""
update cards set type=2,queue=2,ivl=1,due=:due,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id and type<>2""", d)
    self.col.log(ids)

# inspired by
# Date:     January 27, 2016
# Author:   Benjamin Gray
# File:     Quick_Reschedule.py
# Purpose:  Quickly reschedule cards in anki to a user specified interval
# using sched.reschedCards()

# prompt for new interval, and set it


def promptNewInterval(cids):
    if cids is None:
        cids = [aqt.mw.reviewer.card.id]
    SWAP_TAG = False
    cardEase = None
    infotip = ''
    prefix = ''
    suffix = ''
    total = 0
    dayz = float(0)
    try:
        days = unicode(aqt.mw.reviewer.card.ivl + 1)
    except AttributeError:
        days = u'1'
    dayString = aqt.utils.getText(
        (MSG[lang]['till next'] +
         ' (' + MSG[lang]['current'] + ' + 1 = %s ):') % (days),
        default=days)

    stringY = False
    stringM = False
    stringW = False
    stringD = False

    if dayString[1]:
        daysList = dayString[0].strip().lower().split()
        for nextWord in daysList:
            nextDate = nextWord.strip()
            if len(nextDate) == 0:
                continue

            dayStringY = False
            dayStringM = False
            dayStringW = False
            dayStringD = False

            if nextDate.endswith('y') or nextDate.endswith(u'г'):
                nextDate = nextDate[:-1].strip()
                dayStringY = True
                stringY = True
            if nextDate.endswith('m') or nextDate.endswith(u'м'):
                nextDate = nextDate[:-1].strip()
                dayStringM = True
                stringM = True
            if nextDate.endswith('w') or nextDate.endswith(u'н'):
                nextDate = nextDate[:-1].strip()
                dayStringW = True
                stringW = True
            if nextDate.endswith('d') or nextDate.endswith(u'д'):
                nextDate = nextDate[:-1].strip()
                dayStringD = True
                stringD = True
            if len(nextDate) == 0:
                nextDate = '1'
                dayStringD = True
                stringD = True

            if nextDate.endswith('%'):
                nextDate = nextDate[:-1].strip()
                if nextDate == '':
                    nextDate = '250'
                try:
                    cardEase = max(130, abs(int(nextDate)))
                except ValueError:
                    cardEase = 130
            else:
                prefix += nextWord + ' '
                try:
                    dayz = float(0)
                    days = int(nextDate)
                    if dayStringM:
                        dayz = abs(float(days))
                        days = 0
                    if dayStringY:
                        dayz = abs(float(days)) * 12.0
                        days = 0
                        dayStringM = True
                    if dayStringW:
                        days = abs(days) * 7
                except ValueError:
                    days = 1  # aqt.mw.reviewer.card.ivl + 1
                    try:
                        dayz = abs(float(nextDate))
                        if 0 < dayz and dayz < 1:
                            days = int(dayz * 10) * 7
                            dayz = float(0)
                            dayStringW = True
                            stringW = True
                        else:
                            days = 0
                            dayStringM = True
                            stringM = True
                            if dayStringY:
                                dayz = dayz * 12.0
                    except ValueError:
                        dayz = float(0)

                if dayStringM:
                    total += int(30 * abs(dayz))
                else:
                    total += abs(days)

        aqt.mw.checkpoint(_('Reschedule card'))

        days = total

        if stringD or (not stringD and not stringW and not stringM):
            if days > 9:
                suffix = '&plusmn;1'
                total = days + random.randrange(-1, 1 + 1, 1)
            else:  # from 1 to 9 setup exact number of day
                suffix = ''
                total = days  # days = days
        elif stringW:  # .2 is two weeks
            suffix = '&plusmn;3'
            total = abs(days) + random.randrange(-3, 3 + 1, 1)
        elif stringM:  # 3.1 or 1.2 is monthes
            suffix = '&plusmn;15'
            total = abs(days) + random.randrange(-15, 15 + 1, 1)

        if cardEase is None:
            if not total:  # empty request line == drop cards to new queue
                aqt.mw.col.sched.forgetCards(cids)
                aqt.mw.reset()
                return
            infotip = ''
            # try:
            #     cardEase = aqt.mw.reviewer.card.factor  # 2500
            # except AttributeError:
            #     cardEase = 2500
        else:
            infotip = (MSG[lang]['card ease'] +
                       ' <b>%s</b>%%<br><br>') % (cardEase)
            cardEase *= 10

        if total:
            # aqt.mw.col.sched.reschedCards(
            #   [aqt.mw.reviewer.card.id], total-1 if total>1 else 1, total+1 )
            if cardEase is not None:
                if total < 10:
                    _reschedCards(
                        aqt.mw.col.sched, cids, total, total, indi=cardEase)
                else:
                    _reschedCards(
                        aqt.mw.col.sched, cids, total -
                        1 if total > 1 else 1, total + 1, indi=cardEase)
            else:
                if total < 10:
                    _nofactorCards(
                        aqt.mw.col.sched, cids, total, total)
                else:
                    _nofactorCards(
                        aqt.mw.col.sched, cids, total -
                        1 if total > 1 else 1, total + 1)

            days_mod = (total % 10) if ((total % 100) < 11 or (
                total % 100) > 14) else (total % 100)
            aqt.utils.tooltip(
                infotip + (
                    'Запланирован просмотр через <b>%s</b> %s ' +
                    ('день' if days_mod == 1 else (
                        'дня' if days_mod >= 2 and
                        days_mod <= 4 else 'дней'))
                    if lang == 'ru' else
                    'Rescheduled for review in <b>%s</b> %s days') % (
                        total, ' ( <b style="color:#666;">%s</b> %s ) ' %
                        (prefix.strip(), suffix) if len(suffix) else ''),
                period=2000)

            # SWAP_TAG = datetime.datetime.now().strftime(
            #   'rescheduled::re-%Y-%m-%d::re-card')
            # SWAP_TAG = datetime.datetime.now().strftime(
            #   're-%y-%m-%d-c')
            if SWAP_TAG:
                SWAP_TAG += unicode(aqt.mw.reviewer.card.ord + 1)
                note = aqt.mw.reviewer.card.note()
                if not note.hasTag(SWAP_TAG):
                    note.addTag(SWAP_TAG)
                    note.flush()  # never forget to flush

        elif cardEase is not None:
            aqt.utils.tooltip((
                MSG[lang]['card ease'] +
                ' <b>%s</b>%%<br><br>') %
                (int(cardEase / 10)), period=2000)
            _refactorCards(aqt.mw.col.sched, cids, indi=cardEase)
            # aqt.mw.reviewer.card.factor = cardEase
            # aqt.mw.reviewer.card.flush()

        aqt.mw.reset()

if True:
    try:
        aqt.mw.addon_cards_menu
    except AttributeError:
        aqt.mw.addon_cards_menu = QMenu(MSG[lang]['Cards'], aqt.mw)
        aqt.mw.form.menubar.insertMenu(
            aqt.mw.form.menuTools.menuAction(), aqt.mw.addon_cards_menu)

    set_new_int_action = QAction(aqt.mw)
    set_new_int_action.setText(MSG[lang]['days interval'])
    set_new_int_action.setIcon(
        QIcon(os.path.join(MUSTHAVE_COLOR_ICONS, 'schedule.png')))
    set_new_int_action.setShortcut(QKeySequence(HOTKEY['prompt_popup']))
    set_new_int_action.setEnabled(False)
    aqt.mw.connect(
        set_new_int_action, SIGNAL('triggered()'),
        lambda: promptNewInterval(None))

    if hasattr(aqt.mw, 'addon_cards_menu'):
        aqt.mw.addon_cards_menu.addAction(set_new_int_action)
        aqt.mw.addon_cards_menu.addSeparator()

    def edit_actions_off():
        set_new_int_action.setEnabled(False)

    def edit_actions_on():
        set_new_int_action.setEnabled(True)

    aqt.mw.deckBrowser.show = anki.hooks.wrap(
        aqt.mw.deckBrowser.show, edit_actions_off)
    aqt.mw.overview.show = anki.hooks.wrap(
        aqt.mw.overview.show, edit_actions_off)
    aqt.mw.reviewer.show = anki.hooks.wrap(
        aqt.mw.reviewer.show, edit_actions_on)

# reset_card_scheduling.py
# https://ankiweb.net/shared/info/1432861881
# Reset card(s) scheduling information / progress
#######################################################

# Col is a collection of cards, cids are the ids of the cards to reset.


def resetSelectedCardScheduling(self):
    """
    Resets statistics for selected cards,
    and removes them from learning queues.
    """
    cids = self.selectedCards()
    if not cids:
        return
    # Allow undo
    self.mw.checkpoint(_('Promt and set days interval'))
    self.mw.progress.start(immediate=True)
    # Not sure if beginReset is required
    self.model.beginReset()

    # Resets selected cards in current collection
    # self.col.sched.resetCards(cids)
    # Removes card from dynamic deck?
    # self.col.sched.remFromDyn(cids)
    # Removes card from learning queues
    # self.col.sched.removeLrn(cids)

    promptNewInterval(cids=cids)

    self.model.endReset()
    self.mw.progress.finish()
    # Update the main UI window to reflect changes in card status
    self.mw.reset()


def addMenuItem(self):
    """ Adds hook to the Edit menu in the note browser """
    newInt_action = QAction('Promt and set days interval', self)
    newInt_action.setShortcut(QKeySequence(HOTKEY['prompt_popup']))
    self.resetSelectedCardScheduling = resetSelectedCardScheduling
    self.connect(newInt_action, SIGNAL('triggered()'),
                 lambda s=self: resetSelectedCardScheduling(self))
    self.form.menuEdit.addAction(newInt_action)

# Add-in hook; called by the AQT Browser object when it is ready for the
# add-on to modify the menus
anki.hooks.addHook('browser.setupMenus', addMenuItem)

##


def switch_autoshow():
    global AUTOSHOW_STATE
    AUTOSHOW_STATE = autoshow_action.isChecked()
    if AUTOSHOW_STATE:
        aqt.utils.tooltip(MSG[lang]['AUTOSHOW_STATE is on'])
        if aqt.mw.reviewer.state == 'answer':
            set_timeoutQ(aqt.mw.reviewer)
        elif aqt.mw.reviewer.state == 'question':
            set_timeoutA(aqt.mw.reviewer)
    else:
        aqt.utils.tooltip(MSG[lang]['AUTOSHOW_STATE is off'])
        clear_timeout()

autoshow_action = QAction(MSG[lang]['autoshow'], aqt.mw)
autoshow_action.setShortcut(QKeySequence(HOTKEY['autoshow']))
autoshow_action.setCheckable(True)
aqt.mw.connect(autoshow_action, SIGNAL('triggered()'), switch_autoshow)

if hasattr(aqt.mw, 'addon_view_menu'):
    aqt.mw.addon_view_menu.addAction(autoshow_action)

##


def append_html(self, _old):
    return _old(self) + """
        <script>
            var autoTimeout = 0;
            var setAuto = function(ms) {
                clearTimeout(autoTimeout);
                autoTimeout = setTimeout(function () { py.link('ans') }, ms);
            }
            var setAvto = function(ms) {
                clearTimeout(autoTimeout);
                autoTimeout = setTimeout(function () { py.link('ease%d')},ms);
            }
        </script>
        """ % (NOT_NOW_BASE)


def clear_timeout():
    aqt.mw.reviewer.bottom.web.eval("clearTimeout(autoTimeout);")


def set_timeoutA(self):
    if AUTOSHOW_STATE:
        c = self.mw.col.decks.confForDid(self.card.odid or self.card.did)
        if c.get('autoAnswer', 0) > 0:
            self.bottom.web.eval("setAuto(%d);" % (c['autoAnswer'] * 1000))


def set_timeoutQ(self):
    if AUTOSHOW_STATE:
        c = self.mw.col.decks.confForDid(self.card.odid or self.card.did)
        if c.get('autoQuestion', 0) > 0:
            self.bottom.web.eval("setAvto(%d);" % (c['autoQuestion'] * 1000))


def setup_ui(self, Dialog):
    self.maxTaken.setMinimum(3)
    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText(MSG[lang]['autoshow Answer'])
    label2 = QLabel(self.tab_5)
    label2.setText(_("seconds"))
    self.autoAnswer = QSpinBox(self.tab_5)
    self.autoAnswer.setMinimum(0)
    self.autoAnswer.setMaximum(3600)
    grid.addWidget(label1, 0, 0, 1, 1)
    grid.addWidget(self.autoAnswer, 0, 1, 1, 1)
    grid.addWidget(label2, 0, 2, 1, 1)
    self.verticalLayout_6.insertLayout(1, grid)

    self.maxTaken.setMinimum(3)
    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText(MSG[lang]['autoshow Question'])
    label2 = QLabel(self.tab_5)
    label2.setText(_("seconds"))
    self.autoQuestion = QSpinBox(self.tab_5)
    self.autoQuestion.setMinimum(0)
    self.autoQuestion.setMaximum(3600)
    grid.addWidget(label1, 0, 0, 1, 1)
    grid.addWidget(self.autoQuestion, 0, 1, 1, 1)
    grid.addWidget(label2, 0, 2, 1, 1)
    self.verticalLayout_6.insertLayout(1, grid)


def load_conf(self):
    f = self.form
    c = self.conf
    f.autoAnswer.setValue(c.get('autoAnswer', 0))
    f.autoQuestion.setValue(c.get('autoQuestion', 0))


def save_conf(self):
    f = self.form
    c = self.conf
    c['autoAnswer'] = f.autoAnswer.value()
    c['autoQuestion'] = f.autoQuestion.value()

aqt.reviewer.Reviewer._bottomHTML = anki.hooks.wrap(
    aqt.reviewer.Reviewer._bottomHTML, append_html, 'around')

aqt.forms.dconf.Ui_Dialog.setupUi = anki.hooks.wrap(
    aqt.forms.dconf.Ui_Dialog.setupUi, setup_ui)

aqt.deckconf.DeckConf.loadConf = anki.hooks.wrap(
    aqt.deckconf.DeckConf.loadConf, load_conf)

aqt.deckconf.DeckConf.saveConf = anki.hooks.wrap(
    aqt.deckconf.DeckConf.saveConf, save_conf, 'before')

# ------ ====== ' Addons Install Tooltip ' ====== ------ #

try:
    aqt.mw.addon_view_menu
except AttributeError:
    aqt.mw.addon_view_menu = QMenu(MSG[lang]['View'], aqt.mw.menuBar())
    aqt.mw.form.menubar.insertMenu(
        aqt.mw.form.menuTools.menuAction(), aqt.mw.addon_view_menu)


def timefn(tm):
    str = ''
    if tm >= 60:
        str = anki.utils.fmtTimeSpan(
            (tm / 60) * 60, short=True, point=-1, unit=1)
    if tm % 60 != 0 or not str:
        str += anki.utils.fmtTimeSpan(
            tm % 60, point=2 if not str else -1, short=True)
    return str

# Here are hotkeys for
#  https://github.com/dae/anki/blob/master/designer/main.ui

aqt.mw.form.actionFullDatabaseCheck.setShortcut(
    QKeySequence('Ctrl+Delete'))  # Check Database...

aqt.mw.form.actionCheckMediaDatabase.setShortcut(
    QKeySequence('Alt+Shift+Delete'))  # Check Media...

aqt.mw.form.actionEmptyCards.setShortcut(
    QKeySequence('Ctrl+Shift+Delete'))  # Empty Cards...


# anki-master\aqt\addons.py
#  Monkey Patching
#   showInfo -> tooltip
def _accept1(self):
    # go_AnkiWeb_addons()
    # This way starts after dialog window were closed, not before.

    QDialog.accept(self)
    # create downloader thread

    txt = self.form.code.text().split()
    for x in txt:
        ret = aqt.downloader.download(self.mw, x)
        if not ret:
            return
        data, fname = ret
        self.mw.addonManager.install(data, fname)
        self.mw.progress.finish()

    aqt.utils.tooltip(
        _("Download successful. Please restart Anki."),
        period=3000)

    if install_again:
        aqt.addons.AddonManager.onGetAddons(self.mw.addonManager)

if install_tooltip:
    aqt.addons.GetAddons.accept = _accept1

# hotkeys

if install_hotkeys:
    aqt.mw.form.actionDownloadSharedPlugin.setShortcut(HOTKEY['Install'])


# menu
def go_AnkiWeb_addons():
    aqt.utils.openLink("https://ankiweb.net/shared/addons/")


def toggle_install_again():
    global install_again
    install_again = show_install_again_action.isChecked()

    aqt.addons.AddonManager.onGetAddons(aqt.mw.addonManager)

show_install_again_action = QAction(aqt.mw)
show_install_again_action.setText(MSG[lang]['show_install'])
show_install_again_action.setCheckable(True)
show_install_again_action.setChecked(install_again)
aqt.mw.connect(show_install_again_action, SIGNAL("triggered()"),
               toggle_install_again)


def save_install_again():
    aqt.mw.pm.profile['addons_install_again'] = (
        show_install_again_action.isChecked())


def load_install_again():
    global install_again, show_install_again_action
    try:
        install_again = aqt.mw.pm.profile['addons_install_again']
    except KeyError:
        install_again = False
    show_install_again_action.setChecked(install_again)

if install_menu:
    anki.hooks.addHook("unloadProfile", save_install_again)
    anki.hooks.addHook("profileLoaded", load_install_again)

    aqt.mw.form.menuPlugins.insertAction(aqt.mw.form.actionOpenPluginFolder,
                                         show_install_again_action)

    open_ankiweb_shared_action = QAction(aqt.mw)
    open_ankiweb_shared_action.setText(MSG[lang]['open_ankiweb'])
    aqt.mw.connect(open_ankiweb_shared_action, SIGNAL("triggered()"),
                   go_AnkiWeb_addons)
    aqt.mw.form.menuPlugins.insertAction(aqt.mw.form.actionOpenPluginFolder,
                                         open_ankiweb_shared_action)

else:
    install_again = False

# menuPlugins
# designer/main.ui

# Browse & Install...
# <string>Browse &amp;&amp; Install...</string>
# actionDownloadSharedPlugin

# <string>&amp;Open Add-ons Folder...</string>
# actionOpenPluginFolder

##############################################################
# rated:30:1
# https://anki.tenderapp.com/discussions/add-ons/9032-rated301

# RADIO_FORGOT: 30 -> 36500

# aqt/customstudy.py
# Copyright: Damien Elmes <anki@ichi2.net>

RATED301 = 36500

RADIO_NEW = 1
RADIO_REV = 2
RADIO_FORGOT = 3
RADIO_AHEAD = 4
RADIO_PREVIEW = 5
RADIO_CRAM = 6

TYPE_NEW = 0
TYPE_DUE = 1
TYPE_ALL = 2


def _onRadioChange(self, idx):
    f = self.form
    sp = f.spin
    smin = 1
    smax = DYN_MAX_SIZE
    sval = 1
    post = _("cards")
    tit = ""
    spShow = True
    typeShow = False
    ok = _("OK")

    def plus(num):
        if num == 1000:
            num = "1000+"
        return "<b>"+str(num)+"</b>"
    if idx == RADIO_NEW:
        new = self.mw.col.sched.totalNewForCurrentDeck()
        self.deck['newToday']
        tit = _("New cards in deck: %s") % plus(new)
        pre = _("Increase today's new card limit by")
        sval = min(new, self.deck.get('extendNew', 10))
        smax = new
    elif idx == RADIO_REV:
        rev = self.mw.col.sched.totalRevForCurrentDeck()
        tit = _("Reviews due in deck: %s") % plus(rev)
        pre = _("Increase today's review limit by")
        sval = min(rev, self.deck.get('extendRev', 10))
    elif idx == RADIO_FORGOT:
        pre = _("Review cards forgotten in last")
        post = _("days")
        smax = RATED301
    elif idx == RADIO_AHEAD:
        pre = _("Review ahead by")
        post = _("days")
    elif idx == RADIO_PREVIEW:
        pre = _("Preview new cards added in the last")
        post = _("days")
        sval = 1
    elif idx == RADIO_CRAM:
        pre = _("Select")
        post = _("cards from the deck")
        # tit = _("After pressing OK, you can choose which tags to include.")
        ok = _("Choose Tags")
        sval = 100
        typeShow = True
    sp.setVisible(spShow)
    f.cardType.setVisible(typeShow)
    f.title.setText(tit)
    f.title.setVisible(not not tit)
    f.spin.setMinimum(smin)
    f.spin.setMaximum(smax)
    f.spin.setValue(sval)
    f.preSpin.setText(pre)
    f.postSpin.setText(post)
    f.buttonBox.button(QDialogButtonBox.Ok).setText(ok)
    self.radioIdx = idx

aqt.customstudy.CustomStudy.onRadioChange = _onRadioChange


def _findRated(self, (val, args)):
    # days(:optional_ease)
    r = val.split(":")
    try:
        days = int(r[0])
    except ValueError:
        return
    days = min(days, RATED301)
    # ease
    ease = ""
    if len(r) > 1:
        if r[1] not in ("1", "2", "3", "4"):
            return
        ease = "and ease=%s" % r[1]
    cutoff = (self.col.sched.dayCutoff - 86400*days)*1000
    return ("c.id in (select cid from revlog where id>%d %s)" %
            (cutoff, ease))

anki.find.Finder._findRated = _findRated

##

_old_renderQA = _Collection._renderQA


def _renderQA(self, data, qfmt=None, afmt=None):
    origFieldMap = self.models.fieldMap
    model = self.models.get(data[2])
    if data[0] is None:
        card = None
    elif data[0] == 1:
        card = None
    else:
        try:
            card = self.getCard(data[0])
        except:
            card = None

    def tmpFieldMap(m):
        """Mapping of field name -> (ord, field)."""
        d = dict((f['name'], (f['ord'], f)) for f in m['flds'])
        newFields = [
            'info:ord', 'info:did', 'info:due',
            'info:odid', 'info:odue', 'info:cid', 'info:left',
            'info:ivl', 'info:queue', 'info:Reviews', 'info:reps',
            'info:lapses', 'info:flags', 'info:data',
            'info:FirstReview', 'info:LastReview', 'info:TimeAvg',
            'info:TimeTotal', 'info:Young', 'info:Mature',
            'info:type', 'info:nid', 'info:mod', 'info:usn', 'info:factor',
            'info:New', 'info:Learning', 'info:dayLearning', 'info:Review',
        ]
        for i, f in enumerate(newFields):
            d[f] = (len(m['flds']) + i, 0)
        return d
    self.models.fieldMap = tmpFieldMap
    origdata = copy.copy(data)
    data[6] += '\x1f'
    additionalFields = [str(data[4])]
    if card is not None:
        additionalFields += map(str, [
            card.did, card.due, card.odid, card.odue, card.id, card.left,
            card.ivl, card.queue, card.reps, card.reps, card.lapses,
            card.flags, card.data])
        (first, last, cnt, total) = self.db.first(
            'select min(id), max(id), count(), sum(time)/1000 ' +
            'from revlog where cid = :cid',
            cid=card.id)
        if cnt:
            additionalFields.append(time.strftime(
                '%Y-%m-%d', time.localtime(first / 1000)))
            additionalFields.append(time.strftime(
                '%Y-%m-%d', time.localtime(last / 1000)))
            additionalFields.append(timefn(total / float(cnt)))
            additionalFields.append(timefn(total))
        else:
            additionalFields += [''] * 4
        if card.type == 2 and card.ivl < 21:
            additionalFields += [_('Young')]
        else:
            additionalFields += ['']
        if card.type == 2 and card.ivl > 20:
            additionalFields += [_('Mature')]
        else:
            additionalFields += ['']
        additionalFields += [str(card.type)]
        additionalFields += [str(card.nid)]
        # additionalFields += [str(card.mod)]
        additionalFields.append(time.strftime(
            '%Y-%m-%d', time.localtime(card.mod)))
        additionalFields += [str(card.usn)]
        additionalFields += [str(card.factor)]
        if card.type == 0:
            additionalFields += [_('New')]
        else:
            additionalFields += ['']
        if card.type == 1:
            additionalFields += [_('Learn')]
        else:
            additionalFields += ['']
        if card.type == 1 and card.queue == 3:
            additionalFields += [_('Learning')]
        else:
            additionalFields += ['']
        if card.type == 2:
            additionalFields += [_('Review')]
        else:
            additionalFields += ['']
    else:
        additionalFields += [''] * 28
    data[6] += '\x1f'.join(additionalFields)

    result = _old_renderQA(self, data, qfmt=qfmt, afmt=afmt)

    data = origdata
    self.models.fieldMap = origFieldMap
    return result

##

_Collection._renderQA = _renderQA


def previewCards(self, note, type=0):
    existingTemplates = {c.template()[u'name']: c for c in note.cards()}
    if type == 0:
        cms = self.findTemplates(note)
    elif type == 1:
        cms = [c.template().name() for c in note.cards()]
    else:
        cms = note.model()['tmpls']
    if not cms:
        return []
    cards = []
    for template in cms:
        if template[u'name'] in existingTemplates:
            card = existingTemplates[template[u'name']]
        else:
            card = self._newCard(note, template, 1, flush=False)
        cards.append(card)
    return cards

_Collection.previewCards = previewCards


def _getCardReordered(self):
    """
    'Return the next due card id, or None.'

 inspired by Anki user rjgoif
 https://ankiweb.net/shared/info/1810271825
 put ALL due "learning" cards first ×
 ####################################################################
 That is a simple add-on that inserts the daily-learning cards, i.e.
 cards in the learning queue with intervals that crossed the day turnover,
 before starting other reviews (new cards, review cards). \
 Normally these cards go last, but I want them to go first.
 ####################################################################
    """

    # learning card due?
    c = self._getLrnCard()
    if c:
        return c

    # new first, or time for one?
    if self._timeForNewCard():

        # day learning card due?
        c = self._getLrnDayCard()
        if c:
            return c

        c = self._getNewCard()
        if c:
            return c

    # card due for review?
    c = self._getRevCard()
    if c:
        return c

    # day learning card due?
    c = self._getLrnDayCard()
    if c:
        return c

    # new cards left?
    c = self._getNewCard()
    if c:
        return c

    # collapse or finish
    return self._getLrnCard(collapse=True)

anki.sched.Scheduler._getCard = _getCardReordered

#################################################
# • Insensitive case type field

# from Ignore accents in browser search add-on
# https://ankiweb.net/shared/info/1924690148

UPPER_CASE = False
# UPPER_CASE = True

EXACT_COMPARING = False
# EXACT_COMPARING = True


def onExact():
    global EXACT_COMPARING
    EXACT_COMPARING = exact_action.isChecked()


def save_exact():
    aqt.mw.pm.profile['EXACT_COMPARING'] = (
        EXACT_COMPARING)


def load_exact():
    global EXACT_COMPARING, exact_action
    try:
        EXACT_COMPARING = aqt.mw.pm.profile['EXACT_COMPARING']
    except KeyError:
        EXACT_COMPARING = False
    exact_action.setChecked(EXACT_COMPARING)

if install_menu:  # create menu item in Cards
    anki.hooks.addHook("unloadProfile", save_exact)
    anki.hooks.addHook("profileLoaded", load_exact)

    exact_action = QAction(aqt.mw)
    exact_action.setText(MSG[lang]['exact'])
    exact_action.setCheckable(True)
    exact_action.setChecked(EXACT_COMPARING)
    aqt.mw.connect(exact_action, SIGNAL('triggered()'), onExact)
    aqt.mw.addon_view_menu.addAction(exact_action)

##


def stripCombining(txt):
    """Return txt with all combining characters removed."""
    norm = unicodedata.normalize('NFKD', txt)
    return ''.join([c for c in norm if not unicodedata.combining(c)])


def maTypeAnsAnswerFilter(self, buf):
    # tell webview to call us back with the input content
    self.web.eval('_getTypedText();')
    if not self.typeCorrect:
        return buf
    origSize = len(buf)
    buf = buf.replace('<hr id=answer>', '')
    hadHR = len(buf) != origSize
    # munge correct value
    parser = HTMLParser.HTMLParser()
    cor = anki.utils.stripHTML(
        self.mw.col.media.strip(self.typeCorrect))
    # ensure we don't chomp multiple whitespace
    cor = cor.replace(' ', '&nbsp;')
    cor = parser.unescape(cor)
    cor = cor.replace(u'\xa0', ' ')
    given = self.typedAnswer

    if not EXACT_COMPARING:
        cor = stripCombining(cor)
        given = stripCombining(given)

    # compare with typed answer
    if EXACT_COMPARING:
        res = self.correct(given, cor, showBad=False)
    elif UPPER_CASE:
        res = self.correct(given.strip().upper(),
                           cor.strip().upper(), showBad=False)
    else:
        res = self.correct(given.strip().lower(),
                           cor.strip().lower(), showBad=False)
    # and update the type answer area

    def repl(match):
        # can't pass a string in directly, and can't use re.escape as it
        # escapes too much
        s = """
<span style="font-family: '%s'; font-size: %spx">%s</span>""" % (
            self.typeFont, self.typeSize, res)
        if hadHR:
            # a hack to ensure the q/a separator falls before the answer
            # comparison when user is using {{FrontSide}}
            s = '<hr id=answer>' + s
        return s
    return re.sub(self.typeAnsPat, repl, buf)


def myTypeAnsAnswerFilter(self, buf, i):
    if i >= len(self.typeCorrect):
        return re.sub(self.typeAnsPat, '', buf)
    # tell webview to call us back with the input content
    self.web.eval('_getTypedText(%d);' % i)
    if not self.typeCorrect:
        return buf
    origSize = len(buf)
    buf = buf.replace('<hr id=answer>', '')
    hadHR = len(buf) != origSize
    # munge correct value
    parser = HTMLParser.HTMLParser()
    cor = anki.utils.stripHTML(
        self.mw.col.media.strip(self.typeCorrect[i]))
    # ensure we don't chomp multiple whitespace
    cor = cor.replace(' ', '&nbsp;')
    cor = parser.unescape(cor)
    cor = cor.replace(u'\xa0', ' ')
    given = self.typedAnswer

    if not EXACT_COMPARING:
        cor = stripCombining(cor)
        given = stripCombining(given)

    # compare with typed answer
    if EXACT_COMPARING:
        res = self.correct(given, cor, showBad=False)
    elif UPPER_CASE:
        res = self.correct(given.strip().upper(),
                           cor.strip().upper(), showBad=False)
    else:
        res = self.correct(given.strip().lower(),
                           cor.strip().lower(), showBad=False)
    # and update the type answer area

    def repl(match):
        # can't pass a string in directly, and can't use re.escape as it
        # escapes too much
        s = """
<span style="font-family: '%s'; font-size: %spx">%s</span>""" % (
            self.typeFont, self.typeSize, res)
        if hadHR:
            # a hack to ensure the q/a separator falls before the answer
            # comparison when user is using {{FrontSide}}
            s = '<hr id=answer>' + s
        return s
    buf = re.sub(self.typeAnsPat, repl, buf, 1)
    return self.typeAnsAnswerFilter(buf, i + 1)

if os.path.exists(os.path.join(aqt.mw.pm.addonFolder(),
                  'Multiple_type_fields_on_card.py')):
    aqt.reviewer.Reviewer.typeAnsAnswerFilter = myTypeAnsAnswerFilter
else:
    aqt.reviewer.Reviewer.typeAnsAnswerFilter = maTypeAnsAnswerFilter

##################################################################
# Select_Buttons_Automatically_If_Correct_Answer_Wrong_Answer_or_Nothing.py
# https://ankiweb.net/shared/info/2074758752
# Select Buttons Automatically If Correct Answer, Wrong Answer or Nothing


def maybe_skip_question(self):
    self.typedAnswers = []

aqt.reviewer.Reviewer._showQuestion = anki.hooks.wrap(
    aqt.reviewer.Reviewer._showQuestion, maybe_skip_question)


def maLinkHandler(self, url):

    if ':' in url:
        (cmd, arg) = url.split(':', 1)
    else:
        cmd = url
        arg = ''

    if cmd == 'study':
        my_studyDeck(self, arg)
    elif url.startswith('typeans:'):
        self.typedAnswers.append(unicode(arg))

aqt.reviewer.Reviewer._linkHandler = anki.hooks.wrap(
    aqt.reviewer.Reviewer._linkHandler, maLinkHandler)


def JustPlayIt(parm):
    try:
        arg = anki.utils.stripHTML(aqt.mw.col.media.strip(unicode(parm)))
        arg = parm.replace(' ', '&nbsp;')
    except UnicodeDecodeError:
        arg = ''
    # ensure we don't chomp multiple whitespace
    arg = HTMLParser.HTMLParser().unescape(arg)
    return arg  # unicode(arg.replace(u'\xa0', ' ')) #arg


def myDefaultEase(self, _old):
    # if self.mw.reviewer.state == 'question':
    #    return _old(self)
    # tooltip(self.mw.reviewer.state)
    # it's always called on answer side, but three times

    given = ''
    if hasattr(self, 'typedAnswer'):
        if hasattr(self, 'typeCorrect'):
            if self.typeCorrect:  # not None
                if hasattr(self, 'typedAnswers'):

                    self.typedAnswer = JustPlayIt(
                        unicode(self.typedAnswer))
                    if not len(self.typedAnswers):
                        gvn = [self.typedAnswer]
                    else:
                        for i in range(len(self.typedAnswers)):
                            self.typedAnswers[i] = JustPlayIt(
                                unicode(self.typedAnswers[i]))
                        gvn = self.typedAnswers

                    if not type(self.typeCorrect) is list:
                        self.typeCorrect = JustPlayIt(
                            unicode(self.typeCorrect))
                        cor = [self.typeCorrect]
                        # in native Anki it is a string
                    else:
                        for i in range(len(self.typeCorrect)):
                            # <div>Indiana</div>
                            # It happens very often
                            # after unexpected pushing Enter key.
                            self.typeCorrect[i] = JustPlayIt(
                                anki.utils.stripHTML(
                                    unicode(self.typeCorrect[i])))
                        cor = self.typeCorrect
                        # with Multiple_type_fields_on_card.py it becomes
                        # a list of strings

                    if (len(gvn) == 0):
                        res = False
                    else:
                        if (len(gvn) > 1 and len(gvn) != len(cor)):
                            res = False
                            # something went wrong
                        else:
                            res = True
                            for i in range(0, len(cor)):

                                if EXACT_COMPARING:
                                    pass
                                elif UPPER_CASE:
                                    gvn[i] = gvn[i].strip().upper()
                                    cor[i] = cor[i].strip().upper()
                                else:
                                    gvn[i] = gvn[i].strip().lower()
                                    cor[i] = cor[i].strip().lower()

                                if not EXACT_COMPARING:
                                    cor[i] = stripCombining(cor[i])
                                    gvn[i] = stripCombining(gvn[i])

                                if (gvn[i] != '' and gvn[i] != cor[i]):
                                    res = False
                                if (gvn[i] != ''):
                                    given += gvn[i]

                    retv = self.mw.col.sched.answerButtons(self.card)
                    if res or given == '':
                        if retv == 4:
                            retv = 3
                        else:
                            retv = 2
                    else:
                        retv = 1
                        """
                        if retv == 4:
                            retv = 2
                        else:
                            retv = 1
                        """
                else:
                    # tooltip ('No typedAnswers')
                    retv = _old(self)
            else:
                    # tooltip ('typeCorrect is None')
                retv = _old(self)
        else:
            # tooltip ('No typeCorrect')
            retv = _old(self)
    else:
        # tooltip ('No typedAnswer')
        retv = _old(self)

    return retv

aqt.reviewer.Reviewer._defaultEase = anki.hooks.wrap(
    aqt.reviewer.Reviewer._defaultEase, myDefaultEase, 'around')
##
