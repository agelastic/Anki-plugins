# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/hssm/advanced-browser

import time

from aqt import *
from aqt.main import AnkiQt
from anki.hooks import addHook, wrap
from anki.utils import fmtTimeSpan
from anki.stats import CardStats

class CustomFields:

    def onAdvBrowserLoad(self, advBrowser):
        """Called when the Advanced Browser add-on has finished
        loading. Create and add all custom columns owned by this
        module."""

        # Store a list of CustomColumns managed by this module. We later
        # use this to build our part of the context menu.
        self.customColumns = []

        # Convenience method to create lambdas without scope clobbering
        def getOnSort(f): return lambda: f

        # Dummy CardStats object so we can use the time() function without
        # creating the object every time.
        cs = CardStats(None, None)
        
        # -- Columns -- #
        
        # First review
        def cFirstOnData(c, n, t):
            first = mw.col.db.scalar(
                "select min(id) from revlog where cid = ?", c.id)
            if first:
                return time.strftime("%Y-%m-%d", time.localtime(first / 1000))
       
        cc = advBrowser.newCustomColumn(
            type = 'cfirst',
            name = 'First Review',
            onData = cFirstOnData,
            onSort = lambda: "(select min(id) from revlog where cid = c.id)"
        )
        self.customColumns.append(cc)


        # Last review
        def cLastOnData(c, n, t):
            last = mw.col.db.scalar(
                "select max(id) from revlog where cid = ?", c.id)
            if last:
                return time.strftime("%Y-%m-%d", time.localtime(last / 1000))
       
        cc = advBrowser.newCustomColumn(
            type = 'clast',
            name = 'Last Review',
            onData = cLastOnData,
            onSort = lambda: "(select max(id) from revlog where cid = c.id)"
        )
        self.customColumns.append(cc)


        # Average time
        def cAvgtimeOnData(c, n, t):
            avgtime = mw.col.db.scalar(
                "select avg(time) from revlog where cid = ?", c.id)
            if avgtime:
                return str(round(avgtime / 1000, 1)) + "s"
        
        cc = advBrowser.newCustomColumn(
            type = 'cavgtime',
            name = 'Time (Average)',
            onData = cAvgtimeOnData,
            onSort = lambda: "(select avg(time) from revlog where cid = c.id)"
        )
        self.customColumns.append(cc)


        # Total time
        def cTottimeOnDAta(c, n, t):
            tottime = mw.col.db.scalar(
                "select sum(time) from revlog where cid = ?", c.id)
            if tottime:
                return str(round(tottime / 1000, 1)) + "s"
    
        cc = advBrowser.newCustomColumn(
            type = 'ctottime',
            name = 'Time (Total)',
            onData = cTottimeOnDAta,
            onSort = lambda: "(select sum(time) from revlog where cid = c.id)"
        )
        self.customColumns.append(cc)


        # Tags
        cc = advBrowser.newCustomColumn(
            type = 'ntags',
            name = 'Tags',
            onData = lambda c, n, t: " ".join(unicode(tag) for tag in n.tags),
            # Lazy shortcut. Treat the "Tags" column as if it were a note field
            # (it is!) so we get all the benefits of our custom work on those
            # fields.
            onSort = lambda: "(select valueForField(mid, flds, 'Tags') "
                             "from notes where id = c.nid)",
        )
        self.customColumns.append(cc)
        # Remove the built-in tags column.
        advBrowser.removeColumn("noteTags")
        
        
        # Overdue interval
        def cOverdueIvl(c, n, t):
            val = self.valueForOverdue(c.odid, c.queue, c.type, c.due)
            if val:
                return str(val) + " day" + ('s' if val > 1 else '')
                
        srt = ("(select valueForOverdue(odid, queue, type, due) "
               "from cards where id = c.id)")

        cc = advBrowser.newCustomColumn(
            type = 'coverdueivl',
            name = "Overdue Interval",
            onData = cOverdueIvl,
            onSort = getOnSort(srt)
        )
        self.customColumns.append(cc)


        # Previous interval
        def cPrevIvl(c, n, t):
            ivl = mw.col.db.scalar(
                "select ivl from revlog where cid = ? "
                "order by id desc limit 1 offset 1", c.id)
            if ivl is None:
                return
            elif ivl == 0:
                return "0 days"
            elif ivl > 0:
                return fmtTimeSpan(ivl*86400)
            else:
                return cs.time(-ivl)
        
        srt = ("(select ivl from revlog where cid = c.id "
               "order by id desc limit 1 offset 1)")
        
        cc = advBrowser.newCustomColumn(
            type = 'cprevivl',
            name = "Previous Interval",
            onData = cPrevIvl,
            onSort = getOnSort(srt)
        )
        self.customColumns.append(cc)
        
    def onBuildContextMenu(self, contextMenu):
        """Build our part of the browser columns context menu."""

        for column in self.customColumns:
            contextMenu.addItem(column)

    def valueForOverdue(self, odid, queue, type, due):
        if odid or queue == 1:
            return
        elif queue == 0 or type == 0:
            return
        elif queue in (2,3) or (type == 2 and queue < 0):
            diff = due - mw.col.sched.today
            if diff < 0:
                return diff * -1
            else:
                return
    
    def myLoadCollection(self, _self):
        """Wrap collection load so we can add our custom DB function.
        We do this here instead of on startup because the collection
        might get closed/reopened while Anki is still open (e.g., after
        sync), which clears the DB function we added."""
        
        # Create a new SQL function that we can use in our queries.
        mw.col.db._db.create_function("valueForOverdue", 4, self.valueForOverdue)


cf = CustomFields()
addHook("advBrowserLoaded", cf.onAdvBrowserLoad)
addHook("advBrowserBuildContext", cf.onBuildContextMenu)
AnkiQt.loadCollection = wrap(AnkiQt.loadCollection, cf.myLoadCollection)
