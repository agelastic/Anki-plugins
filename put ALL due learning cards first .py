# -*- coding: utf-8 -*-
# by Anki user rjgoif
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# ####################################################################

# This is a simple add-on that inserts the daily-learning cards, i.e.
# cards in the learning queue with intervals that crossed the day turnover,
# before starting other reviews (new cards, review cards). Normally these cards
# go last, but I want them to go first. 


# ####################################################################



import anki.sched as oldSched

def _getCardReordered(self):
	"Return the next due card id, or None."
	# learning card due?
	c = self._getLrnCard()
	if c:
		return c
	# day learning card due?
	c = self._getLrnDayCard()
	if c:
		return c
	# new first, or time for one?
	if self._timeForNewCard():
		c = self._getNewCard()
		if c:
			return c
	# card due for review?
	c = self._getRevCard()
	if c:
		return c
	# new cards left?
	c = self._getNewCard()
	if c:
		return c
	# collapse or finish
	return self._getLrnCard(collapse=True)
	
	
oldSched.Scheduler._getCard = _getCardReordered