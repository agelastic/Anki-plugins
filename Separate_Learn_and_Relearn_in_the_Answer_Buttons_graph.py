# -*- coding: utf-8 -*-
# Relearn Stats 1.0, an Anki addon to separate Learn and Relearn in the Answer Buttons graph
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Modified from Anki source code (2.0.31 and possibly earlier versions) in 2014-2015 by Teemu Pudas
# Anki is Copyright: Damien Elmes <anki@ichi2.net> 
# (I include his email address because that's how it is in the original copyright notice in the Anki source code.
# Don't contact him about bugs in this addon (they're not his fault), use http://anki.tenderapp.com/discussions/add-ons instead)

from anki.db import DB
from anki.stats import *
import anki

def myExecute(self, sql, *a, **kw):
	
	# _eases() - add a fourth category for relearn
	if "(case when type in (0,2) and ease = 4 then 3 else ease end), count() from revlog" in sql:
		sql = sql.replace("when type in (0,2) then 0", """
when type = 0 then 0
when type = 2 then 3
""", 1)

	return oldExecute(self, sql, *a, **kw)


oldExecute = DB.execute
DB.execute = myExecute

def easeGraph(self):
	# 3 + 4 + 4 + 4 + spaces on sides and middle = 18
	# yng starts at 3+1 = 4
	# mtr starts at 4+4+1 = 9
	# rel starts at 9+4+1 = 14
	d = {'lrn':[], 'yng':[], 'mtr':[], 'rel': []}
	types = ("lrn", "yng", "mtr", "rel")
	eases = self._eases()
	nonzero = False
	for (type, ease, cnt) in eases:
		if type == 1:
			ease += 4
		elif type == 2:
			ease += 9
		elif type == 3:
			ease += 14
		n = types[type]
		if cnt > 0:
			nonzero = True
		d[n].append((ease, cnt))
	if not nonzero:
		return ""
	ticks = [[1,1],[2,2],[3,3],
			 [5,1],[6,2],[7,3],[8,4],
			 [10, 1],[11,2],[12,3],[13,4],
			 [15, 1],[16,2],[17,3]]
	txt = self._title(_("Answer Buttons"),
					  _("The number of times you have pressed each button."))
	txt += self._graph(id="ease", data=[
		dict(data=d['lrn'], color=colLearn, label=_("Learning")),
		dict(data=d['yng'], color=colYoung, label=_("Young")),
		dict(data=d['mtr'], color=colMature, label=_("Mature")),
		dict(data=d['rel'], color=colRelearn, label=_("Relearn")),
		], type="barsLine", conf=dict(
			xaxis=dict(ticks=ticks, min=0, max=18)),
		ylabel=_("Answers"))
	txt += self._easeInfo(eases)
	return txt

def _easeInfo(self, eases):
	types = {0: [0, 0], 1: [0, 0], 2: [0,0], 3: [0, 0]}
	for (type, ease, cnt) in eases:
		if ease == 1:
			types[type][0] += cnt
		else:
			types[type][1] += cnt
	i = []
	for type in range(4):
		(bad, good) = types[type]
		tot = bad + good
		try:
			pct = good / float(tot) * 100
		except:
			pct = 0
		i.append(_(
			"Correct: <b>%(pct)0.2f%%</b><br>(%(good)d of %(tot)d)") % dict(
			pct=pct, good=good, tot=tot))
	return ("""
<center><table width=%dpx><tr><td width=50></td><td align=center>""" % self.width +
			"</td><td align=center>".join(i) +
			"</td></tr></table></center>")

CollectionStats._easeInfo = _easeInfo
CollectionStats.easeGraph = easeGraph