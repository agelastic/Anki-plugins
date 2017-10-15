# -*- mode: Python ; coding: utf-8 -*-
# • More decks overview stats
# -- tested with Anki 2.0.44 under Windows 7 SP1
# https://ankiweb.net/shared/info/1841403427
# https://github.com/ankitest/anki-musthave-addons-by-ankitest
# -- tested with Anki 2.0.44 under Windows 7 SP1
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Copyright (c) 2017 Dmitry Mikheev, http://finpapa.ucoz.ru/index.html
# No support. Use it AS IS on your own risk.
"""
 Do not forget about _('To Review')
"""
from __future__ import division
from __future__ import unicode_literals

# Based on Decks Total https://ankiweb.net/shared/info/1421528223
# https://github.com/b50/anki-deck-stats
# Author of original addon: Calumks <calumks@gmail.com>
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import anki
import aqt
from aqt.utils import tooltip

# Get language class
lang = anki.lang.getLang()

# --------------------------
# -- Show learn count -- deck_overview_tweaks.py --
# Show_learn_count.py by ospalh
# Show the learn count in the deck browser, too.
# 3 numbers vs 2 by default
# New, Learn, Due vs Learn+Due and New
# Show count of unseen and suspended cards in deck browser.

# -- Unseen and buried counts --
# https://ankiweb.net/shared/info/161964983
# Show count of unseen and buried cards in deck browser.

PARM = {
    'STUDY_BUTTON': False,
    'GEAR_AT_END_OF_LINE': True,
    'BUTTON_TITLES': True,
    'MORE_OVERVIEW_STATS': 3,
    'HIDE_BIG_NUMBER': 999,
    'HIDE_BIG_NUMBERS': False,
    'queueLimit': 50,  # important
    'reportLimit': 9999,  # not less than in deck options
    '': ''
    }

# --------------------------

_Buried = _('Suspended+Buried').split('+')
_Buried = _Buried[1] if len(_Buried) == 2 else _('Buried')
_Buried = _Buried.capitalize()

_Suspended = _('<small>Sus-<br>pen-<br>ded&nbsp;</small>') \
    if lang == 'en' else _('Suspended')

titles = {
    'en': (
        _("More Decks Stats"),

        _("Activate") + " " + _("More Decks Stats"),

        "%s, %s, %s, %s" % (_('New'), _('Learn'), _('Review'), _('Due')),

        "%s, %s, %s" % (_('Unseen'), _('Suspended'), _Buried),

        _('&Gear at the end of line'),
        _('&Hide big numbers ( > %s )') % (PARM['HIDE_BIG_NUMBER']),
        _('&Study Deck Button'),

        # 7
        _("&View"),

        _('Unseen'),
        _Suspended,
        _Buried,

        _('New'),
        _('Learn'),
        _('Review'),
        _('Due'),

        ''),

    # Please, do not delete English!
    # You can add your own languages in this dictionary

    'ru': (
        'Больше статистики колод',

        "Настраивать панель колод",

        "%s, %s, %s, %s" % (_('New'), _('Learn'), _('Review'), _('Due')),

        '&Невиданные, исключённые и отложенные',

        '&Шестерёнка в конце строки',
        '&Спрятать числа больше %d' % (PARM['HIDE_BIG_NUMBER']),
        '&Кнопка Учить колоду',

        # 7
        "&Вид",

        'Неви-<br>данные',
        'Исклю-<br>чённые',
        'Отло-<br>женные',

        "Новые",
        "Учить",
        "Про-<br>верить",
        "Пора",

        ''),

    '': ''
    }

try:
    titles[lang]
except KeyError:
    lang = 'en'

__addon__ = "'" + __name__.replace('_', ' ')
__version__ = "2.0.44a"

# --------------------------

if True:

    # Replace _renderStats method
    def renderStats(self, _old):

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

        msgp1 = anki.lang.ngettext("%d card", "%d cards", cards) % cards

        buf = "<div style='display:table;padding-top:1.5em;'>" \
            + "<div style='display:table-cell;'> " \
            + _old(self) + "<hr>" \
            + _("New Cards") \
            + ": &nbsp; <font color=#00a> %(d)s</font>" % dict(d=new) \
            + " &nbsp; " + _("Learn") \
            + ": &nbsp; <font color=#a00>%(c)s</font>" % dict(c=lrn) \
            + " &nbsp; <span style='white-space:nowrap;'>" + _("To Review") \
            + ": &nbsp; <font color=#0a0>%(c)s</font>" % dict(c=due) \
            + "</span>" \
            + " &nbsp; <br><span style='white-space:nowrap;'>" + _("Due") \
            + ": &nbsp; <b style=color:#aaa>%(c)s</b> " % dict(c=(lrn+due)) \
            + "</span> " \
            + " &nbsp; <span style='white-space:nowrap;'>" + _("Total") \
            + ": &nbsp; <b style=color:#888>%(c)s</b>" % dict(c=(total)) \
            + "</span></div>" \
            + "<div style='display:table-cell;vertical-align:middle;" \
            + "padding-left:2em;'>" \
            + "<span style='white-space:nowrap;'>" + _("Average") \
            + ":<br> " + _("%.01f cards/minute") % (speed) \
            + "</span><br><br>" \
            + _("More") + "&nbsp;" + ngettext(
                 "%s minute.", "%s minutes.", minutes) % (minutes) \
            + "</div></div>"

        return buf

    aqt.deckbrowser.DeckBrowser._renderStats = anki.hooks.wrap(
        aqt.deckbrowser.DeckBrowser._renderStats, renderStats, 'around')

    ##

    def on_musthave_study():
        global PARM
        PARM['STUDY_BUTTON'] = musthave_study_action.isChecked()
        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")

    def on_gear_at_end_of_line():
        global PARM
        PARM['GEAR_AT_END_OF_LINE'] = gear_at_end_of_line_action.isChecked()
        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")

    def on_hide_big_numbers():
        global PARM
        PARM['HIDE_BIG_NUMBERS'] = hide_big_numbers_action.isChecked()
        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")
        if aqt.mw.state == "overview":
            aqt.mw.moveToState("overview")

    def Unseen_and_buried_counts():
        global PARM
        if PARM['MORE_OVERVIEW_STATS'] == 0:
            return

        if PARM['MORE_OVERVIEW_STATS'] == 3:
            PARM['MORE_OVERVIEW_STATS'] = 2
        else:
            PARM['MORE_OVERVIEW_STATS'] = 3

        musthave_setup_menu()
        initDeckBro()

        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")
        if aqt.mw.state == "overview":
            aqt.mw.moveToState("overview")

    def on_checkers():
        global PARM
        if checkers_action.isChecked():
            PARM['MORE_OVERVIEW_STATS'] = 3
        else:
            PARM['MORE_OVERVIEW_STATS'] = 0

        musthave_setup_menu()
        initDeckBro()

        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")
        if aqt.mw.state == "overview":
            aqt.mw.moveToState("overview")

    def new_and_due_counts():
        global PARM
        if PARM['MORE_OVERVIEW_STATS'] == 0:
            return

        if PARM['MORE_OVERVIEW_STATS'] > 1:
            PARM['MORE_OVERVIEW_STATS'] = 1
        else:
            PARM['MORE_OVERVIEW_STATS'] = 3

        musthave_setup_menu()
        initDeckBro()

        if aqt.mw.state == "deckBrowser":
            aqt.mw.moveToState("deckBrowser")
        if aqt.mw.state == "overview":
            aqt.mw.moveToState("overview")

    ##

    aqt.mw.musthave_submenu = QMenu(titles[lang][0], aqt.mw)

    checkers_action = QAction(titles[lang][1], aqt.mw)
    aqt.mw.connect(checkers_action, SIGNAL("triggered()"), on_checkers)
    checkers_action.setCheckable(True)

    new_and_due_action = QAction(titles[lang][2], aqt.mw)
    aqt.mw.connect(
        new_and_due_action, SIGNAL("triggered()"), new_and_due_counts)
    new_and_due_action.setCheckable(True)

    unseen_and_suspended_action = QAction(titles[lang][3], aqt.mw)
    aqt.mw.connect(unseen_and_suspended_action, SIGNAL(
        "triggered()"), Unseen_and_buried_counts)
    unseen_and_suspended_action.setCheckable(True)

    gear_at_end_of_line_action = QAction(titles[lang][4], aqt.mw)
    aqt.mw.connect(gear_at_end_of_line_action, SIGNAL(
        "triggered()"), on_gear_at_end_of_line)
    gear_at_end_of_line_action.setCheckable(True)

    hide_big_numbers_action = QAction(titles[lang][5], aqt.mw)
    aqt.mw.connect(hide_big_numbers_action, SIGNAL(
        "triggered()"), on_hide_big_numbers)
    hide_big_numbers_action.setCheckable(True)

    musthave_study_action = QAction(titles[lang][6], aqt.mw)
    aqt.mw.connect(
        musthave_study_action, SIGNAL("triggered()"), on_musthave_study)
    musthave_study_action.setCheckable(True)

    try:
        aqt.mw.addon_view_menu
    except AttributeError:
        aqt.mw.addon_view_menu = QMenu(titles[lang][7], aqt.mw)
        aqt.mw.form.menubar.insertMenu(
            aqt.mw.form.menuTools.menuAction(), aqt.mw.addon_view_menu)

    mw_addon_view_menu_exists = hasattr(aqt.mw, 'addon_view_menu')

    if mw_addon_view_menu_exists:
        aqt.mw.addon_view_menu.addSeparator()
        aqt.mw.addon_view_menu.addMenu(aqt.mw.musthave_submenu)
        aqt.mw.musthave_submenu.addAction(checkers_action)
        aqt.mw.musthave_submenu.addSeparator()
        aqt.mw.musthave_submenu.addAction(new_and_due_action)
        aqt.mw.musthave_submenu.addAction(unseen_and_suspended_action)
        aqt.mw.musthave_submenu.addAction(gear_at_end_of_line_action)
        aqt.mw.musthave_submenu.addAction(hide_big_numbers_action)
        aqt.mw.musthave_submenu.addSeparator()
        aqt.mw.musthave_submenu.addAction(musthave_study_action)
        aqt.mw.musthave_submenu.addSeparator()

    def musthave_setup_menu():

        checkers_action.setChecked(PARM['MORE_OVERVIEW_STATS'] > 0)

        unseen_and_suspended_action.setChecked(
            PARM['MORE_OVERVIEW_STATS'] > 2)
        unseen_and_suspended_action.setEnabled(
            PARM['MORE_OVERVIEW_STATS'] > 1)

        musthave_study_action.setChecked(PARM['STUDY_BUTTON'])
        musthave_study_action.setEnabled(PARM['MORE_OVERVIEW_STATS'] > 0)

        hide_big_numbers_action.setChecked(PARM['HIDE_BIG_NUMBERS'])
        hide_big_numbers_action.setEnabled(PARM['MORE_OVERVIEW_STATS'] > 1)

        new_and_due_action.setChecked(PARM['MORE_OVERVIEW_STATS'] > 1)
        new_and_due_action.setEnabled(PARM['MORE_OVERVIEW_STATS'] > 0)

        gear_at_end_of_line_action.setChecked(PARM['GEAR_AT_END_OF_LINE'])
        gear_at_end_of_line_action.setEnabled(
            PARM['MORE_OVERVIEW_STATS'] > 2)

    musthave_setup_menu()

# _____ ------ ========== *********** ========== -------- ______

    th_Unseen = u"<span style='color:#DA70D6;'>" + titles[lang][8] + "</span>"
    th_Suspended = u"<span style='color:#c90;'>" + titles[lang][9] + "</span>"
    th_Buried = u"<span style='color:#960;'>" + titles[lang][10] + "</span>"

# --------------------------
# Copyright © 2012–2014 Roland Sieker <ospalh@gmail.com>
#   Show_learn_count.py
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/licenses/agpl.html

"""
Anki-2 add-on to show the learn count in the deck browser proper way
"""


def my_studyDeck(self, did):
    self.scrollPos = self.web.page().mainFrame().scrollPosition()
    self.mw.col.decks.select(did)
    self.mw.col.startTimebox()
    self.mw.moveToState("review")
    if self.mw.state == "overview":
       # more_tool_bar_off()
    	tooltip(_("No cards are due yet."))

# Event handlers
# Monkey patching


def my_studyHandler(self, url):
    if ":" in url:
        (cmd, arg) = url.split(":")
    else:
        cmd = url
        arg = ''
    if cmd == "study":
        my_studyDeck(self, arg)

aqt.deckbrowser.DeckBrowser._linkHandler = anki.hooks.wrap(
    aqt.deckbrowser.DeckBrowser._linkHandler, my_studyHandler)

# --------------------------


def nonzeroColour(acnt, colour, did):
    if not acnt:
        colour = "silver"
    achk = PARM['HIDE_BIG_NUMBERS'] and acnt > PARM['HIDE_BIG_NUMBER']
    if achk:
        cnt = "%s+" % (PARM['HIDE_BIG_NUMBER'])
    else:
        cnt = str(acnt)
    return ("""<a href="study:{}"
 style="text-decoration:none;cursor:pointer;color:{};"
 onmouseover="this.style.textDecoration='underline';"
 onmouseout="this.style.textDecoration='none';"
 >&nbsp;{}&nbsp;</a>""".format(
        did, colour, cnt) if did and acnt else
        """<span style="color:{};{}>&nbsp;{}&nbsp;</span>""".format(
            colour,
            (('%s" title="%s"' % (
                ('cursor:help;' if achk else ''),
                (acnt if achk else '')))
                if PARM['BUTTON_TITLES'] else '"'),
            cnt)) if acnt > 0 else \
        """<span style="color:{};">&nbsp;{}&nbsp;</span>""".format(
            colour, cnt)

# --------------------------


def deck_browser_render_deck_tree(self, nodes, depth=0):
    if not nodes:
        return ""

    if depth == 0:
        buf = """\n<tr>\n<th colspan=3
 style='padding-right:.25em;color:default;'>%s</th>""" \
            % ("<div style = padding-bottom:.25em; " +
               (" title = Профиль " if PARM['BUTTON_TITLES'] else "") +
               ">" + (aqt.mw.pm.name if len(aqt.mw.pm.profiles()) > 1 and
                      aqt.mw.pm.name else "") +
               "</div><div style = font-weight:400;><i>" + _("Decks") +
               ":</i></div>" +
               "</th>\n<td style='text-align:right;'>%s</td>" %
               ("<i>" + _("Cards") + ":</i>"
                if PARM['MORE_OVERVIEW_STATS'] > 1 else ""))

        if PARM['MORE_OVERVIEW_STATS'] > 1:
            buf += """\n
<td class=count style='padding-right:.25em;color:#33f;width:4em;'>%s</td>\
<td class=count style='padding-right:.25em;color:#c33;width:4em;'>%s</td>\
<td class=count style='color:#090;padding-right:.25em;width:4em;'>%s</td>\
<td class=count style='color:#999;padding-right:1em;width:4em;'>%s</td>\
\n""" % (titles[lang][11], titles[lang][12],
                titles[lang][13], titles[lang][14])

        if PARM['MORE_OVERVIEW_STATS'] > 2:
            if not PARM['GEAR_AT_END_OF_LINE']:
                buf += "<td></td>"
            buf += """\n
<td style="padding-right:.25em;text-align:right;width:4em !important;">%s</td>\
<td style="padding-right:.25em;color:#c90;text-align:right;width:3em;">%s</td>\
<td style="padding-right:.25em;color:#960;text-align:right;width:3em;">%s</td>\
""" % (th_Unseen, th_Suspended, th_Buried)

        buf += "\n</tr>\n" + self._topLevelDragRow()
    else:
        buf = ""
    for node in nodes:
        buf += deck_browser_deck_row(self, node, depth, len(nodes))
    if depth == 0:
        buf += self._topLevelDragRow()

        # Get due and new cards
        due = 0
        new = 0
        lrn = 0

        for tree in self.mw.col.sched.deckDueTree():
            #        due += tree[2] + tree[3]
            due += tree[2]
            lrn += tree[3]
            new += tree[4]

        if PARM['MORE_OVERVIEW_STATS'] > 1:
            buf += """\n
<tr style="vertical-align:top;">\
<th style="color:gray;text-align:left;">%s</th>\
<th align=left>%s</th><th align=left>%s</th>\
<th style='color:gray;text-align:right;'>%s:</th>\
<th class=count style='width:4em;'>%s</th>\
<th class=count style='width:4em;'>%s</th>\
<th class=count style='color:gray;width:4em;'>&nbsp;+&nbsp;%s</th>\
<th class=count style='color:gray;width:4em;padding-right:1em;'
>&nbsp;=&nbsp;%s</th>\n""" % (
                anki.lang.getLang(), _("Total"),
                nonzeroColour(aqt.mw.col.cardCount(), "default", False),
                nonzeroColour(new + lrn + due, "gray", False),
                nonzeroColour(new, "#33f", False),
                nonzeroColour(lrn, "#c33", False),
                nonzeroColour(due, "#090", False),
                nonzeroColour(lrn + due, "#999", False))

        # options
        if not PARM['GEAR_AT_END_OF_LINE'] and \
           PARM['MORE_OVERVIEW_STATS'] > 2:
            buf += "<td>&nbsp;</td>\n"

        if PARM['MORE_OVERVIEW_STATS'] > 2:
            unseen = self.mw.col.db.scalar(
                "select count(*) from cards where queue=0")
            suspended = self.mw.col.db.scalar(
                "select count(*) from cards where queue = -1")
            buried = self.mw.col.db.scalar(
                "select count(*) from cards where queue = -2")

            buf += """\
<td style="padding-right:.25em;width:4em !important;"\
 align=right>%s&nbsp;</td>\
<td style="padding-right:.25em;width:3em;" align=right>%s&nbsp;</td>\
<td style="padding-right:.5em;width:3em;" align=right>%s&nbsp;</td>\
""" % (
                nonzeroColour(unseen, "#DA70D6", False),
                nonzeroColour(suspended, "#c90", False),
                nonzeroColour(buried, "#960", False))  # "#555500"))

        buf += "\n</tr>\n"

    return buf

# --------------------------


def deck_browser_deck_row(self, node, depth, cnt):
    name, did, due, lrn, new, children = node
    deck = self.mw.col.decks.get(did)

    if PARM['MORE_OVERVIEW_STATS'] > 2:
        unseen = self.mw.col.db.scalar(
            "select count(*) from cards where did = %i and queue=0" % did)
        suspended = self.mw.col.db.scalar(
            "select count(*) from cards where did = %i and queue = -1" % did)
        buried = self.mw.col.db.scalar(
            "select count(*) from cards where did = %i and queue = -2" % did)

    if did == 1 and cnt > 1 and not children:
        # if the default deck is empty, hide it
        if not self.mw.col.db.scalar(
                "select 1 from cards where did = 1"):
            return ""

    # parent toggled for collapsing
    for parent in self.mw.col.decks.parents(did):
        if parent['collapsed']:
            buff = ""
            return buff
    prefix = "<big><b>&minus;</b></big>"
    if self.mw.col.decks.get(did)['collapsed']:
        prefix = "<big><b>&plus;</b></big>"

    def indent():
        return "&nbsp;" * 6 * depth

    if did == self.mw.col.conf['curDeck']:
        klass = 'deck current'
    else:
        klass = 'deck'

    buf = "\n<tr class='%s' id='%d' " % (klass, did)

    if PARM['BUTTON_TITLES']:
        buf += (' title = " ' + _('Today') + ': %s "') % (new + lrn + due)
    buf += '>'

    # deck link
    if children:
        collapse = """<a class=collapse href=#
 onclick='py.link("collapse:%d");return false;' \
 style="padding-left:.5em;padding-right:.1em;margin-right:.2em; \
 border:solid 1px transparent;border-radius:5px;display:inline-block;" \
 onmouseover="this.style.border='solid 1px silver';" \
 onmouseout="this.style.border='solid 1px transparent';" \
 title="%s">%s</a>""" % (
            did, (' title=" Свернуть/развернуть вложенные колоды "'
                  if lang == 'ru' else ' title=" ' +
                  _(' Collapse/Downfall ') + ' "')
            if PARM['BUTTON_TITLES'] else '', prefix)
    else:
        collapse = "<span class=collapse></span>"
    if deck['dyn']:
        extraclass = "filtered"
    else:
        extraclass = ""

    studydid = ('''onclick="py.link('study:%d');"''' %
                did) if (new + lrn + due) > 0 else ""
    cursorPointer = ('''cursor:pointer''') if (new + lrn + due) > 0 else ""

    buf += """<td class=decktd colspan=4 %s style="%s;"
>%s%s<a class="deck %s" href=%s>%s</a></td>""" % (
        studydid, cursorPointer, indent(), collapse, extraclass,
        ('''# onclick="py.link('open:%d');return false;"''' % did)
        if (new + lrn + due) > 0 else ("open:%d" % did),
        "<b>" + name + "</b>" if new + lrn + due > 0 else name)

    if PARM['MORE_OVERVIEW_STATS'] > 1:
        buf += """\n\
<td align=right %s style="%s;">%s</td>\
<td align=right %s style="%s;">%s</td>\
<td align=right %s style="%s;">%s</td>\
<td align=right %s style="%s;padding-right:1em;">%s</td>\
\n""" % (
            studydid, cursorPointer, nonzeroColour(new, "#33f", did),
            studydid, cursorPointer, nonzeroColour(lrn, "#c33", did),
            studydid, cursorPointer, nonzeroColour(due, "#090", did),
            studydid, cursorPointer, nonzeroColour(lrn + due, "#999", did))

    # options
    if not PARM['GEAR_AT_END_OF_LINE'] and PARM['MORE_OVERVIEW_STATS'] > 2:
        buf += """<td
 align=right class=opts style='width:1.5em!important;'
 onclick='return false;'>&nbsp;%s</td>""" % self.mw.button(
            link="opts:%d" % did,
            name="<img src='qrc:/icons/gears.png'>&#9662;")

    if PARM['MORE_OVERVIEW_STATS'] > 2:
        buf += """\
<td %s style="%s;padding-right:.25em;width:3em!important;"\
 align=right>%s&nbsp;</td>\
<td %s style="%s;padding-right:.25em;" align=right>%s&nbsp;</td>\
<td %s style="%s;padding-right:.5em;" align=right>%s&nbsp;</td>\
""" % (
            studydid, cursorPointer, nonzeroColour(unseen, "#DA70D6", did),
            studydid, cursorPointer, nonzeroColour(suspended, "#c90", did),
            studydid, cursorPointer, nonzeroColour(buried, "#960", did))

    # options
    if PARM['GEAR_AT_END_OF_LINE'] or PARM['MORE_OVERVIEW_STATS'] < 3:
        buf += """\n<td align=right class=opts
 style='width:1.5em!important;'
 onclick='return false;'>&nbsp;%s</td>""" % self.mw.button(
            link="opts:%d" % did,
            name="<img _valign=bottom src='qrc:/icons/gears.png'>&#9662;")

    if PARM['STUDY_BUTTON']:
        buf += """\n<td align=right
 style="font-size:smaller;">&nbsp;%s</td>""" % self.mw.button(
            link="study:%d" % (did),
            name="<small style = color:dodgerblue; >&#9658;</small>")

    buf += "\n</tr>\n"
    # children
    buf += deck_browser_render_deck_tree(self, children, depth + 1)
    return buf

# Copyright: Juda Kaleta <juda.kaleta@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#  Unseen and buried counts
# https://ankiweb.net/shared/info/161964983
# Show count of unseen and buried cards in deck browser.

org_DeckBrowser_renderDeckTree = aqt.deckbrowser.DeckBrowser._renderDeckTree
org_DeckBrowser_deckRow = aqt.deckbrowser.DeckBrowser._deckRow


def initDeckBro():
    if PARM['MORE_OVERVIEW_STATS']:
        aqt.deckbrowser.DeckBrowser._renderDeckTree = \
            deck_browser_render_deck_tree
        aqt.deckbrowser.DeckBrowser._deckRow = \
            deck_browser_deck_row
    else:
        aqt.deckbrowser.DeckBrowser._renderDeckTree = \
            org_DeckBrowser_renderDeckTree
        aqt.deckbrowser.DeckBrowser._deckRow = \
            org_DeckBrowser_deckRow

initDeckBro()


def maInit(self, col):
    self.queueLimit = PARM['queueLimit']
    self.reportLimit = PARM['reportLimit']  # not 1000!!!

# aqt.mw.col.sched.reportLimit = 5555  # not ready yet

anki.sched.Scheduler.__init__ = \
    anki.hooks.wrap(anki.sched.Scheduler.__init__, maInit)

#


def save_more_decks_stats():
    aqt.mw.pm.profile['ctb_more_overview_stats'] = (
        PARM['MORE_OVERVIEW_STATS'])
    aqt.mw.pm.profile['ctb_hide_big_number'] = (
        PARM['HIDE_BIG_NUMBER'])
    aqt.mw.pm.profile['ctb_hide_big_numbers'] = (
        PARM['HIDE_BIG_NUMBERS'])
    aqt.mw.pm.profile['ctb_gear_at_end_of_line'] = (
        PARM['GEAR_AT_END_OF_LINE'])
    aqt.mw.pm.profile['ctb_musthave_study'] = (
        PARM['STUDY_BUTTON'])
    aqt.mw.pm.profile['ctb_button_titles'] = (
        PARM['BUTTON_TITLES'])


def load_more_decks_stats():
    global PARM

    try:
        tmp = aqt.mw.pm.profile['ctb_more_overview_stats']
        PARM['MORE_OVERVIEW_STATS'] = tmp
    except KeyError:
        pass

    try:
        tmp = aqt.mw.pm.profile['ctb_hide_big_number']
        PARM['HIDE_BIG_NUMBER'] = tmp
    except KeyError:
        pass

    try:
        tmp = aqt.mw.pm.profile['ctb_hide_big_numbers']
        PARM['HIDE_BIG_NUMBERS'] = tmp
    except KeyError:
        pass

    try:
        tmp = aqt.mw.pm.profile['ctb_gear_at_end_of_line']
        PARM['GEAR_AT_END_OF_LINE'] = tmp
    except KeyError:
        pass

    try:
        tmp = aqt.mw.pm.profile['ctb_musthave_study']
        PARM['STUDY_BUTTON'] = tmp
    except KeyError:
        pass

    try:
        tmp = aqt.mw.pm.profile['ctb_button_titles']
        PARM['BUTTON_TITLES'] = tmp
    except KeyError:
        pass

    musthave_setup_menu()
    initDeckBro()

    if aqt.mw.state == "deckBrowser":
        aqt.mw.moveToState("deckBrowser")
    if aqt.mw.state == "overview":
        aqt.mw.moveToState("overview")


anki.hooks.addHook("unloadProfile", save_more_decks_stats)
anki.hooks.addHook("profileLoaded", load_more_decks_stats)

#
