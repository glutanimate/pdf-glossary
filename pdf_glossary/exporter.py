# -*- coding: utf-8 -*-

"""
This file is part of the PDF Glossary add-on for Anki

Custom Anki exporter classes

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals

######## USER CONFIGURATION START ########

EASE_THRESHOLD_LOWER = 210
EASE_THRESHOLD_UPPER = 260
REMOVE_EXTRA_LINEBREAKS = True

######## USER CONFIGURATION STOP ########

import sys, os, subprocess
import re, datetime
from BeautifulSoup import BeautifulSoup # anki21!

# local libraries
sys_encoding = sys.getfilesystemencoding()
addon_path = os.path.dirname(__file__).decode(sys_encoding)
libs_path = os.path.join(addon_path, u"libs")
sys.path.insert(0, libs_path)
pisa = None

from aqt.qt import *
from aqt import mw
from aqt.exporting import ExportDialog
from aqt.utils import tooltip, getBase

from anki.exporting import Exporter
from anki.hooks import addHook
from anki.utils import isWin, isMac

# workaround for xhtml2pdf logging error
import logging
logger = logging.getLogger("xhtml2pdf")
logger.addHandler(logging.NullHandler())

from .templates import *


def openLink(path):
    """Open local URL in default browser"""
    if isWin or isMac:
        # plagued by Qt bugs, might lead to erros on Linux:
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    else:
        url = u"file://" + unicode(path, "utf-8")
        subprocess.Popen(('xdg-open', url))


def openFile(path):
    """Open file in default viewer"""
    if isWin:
        try:
            # print >> sys.stderr, path
            os.startfile(path.decode("utf-8").encode(sys_encoding))
        except (OSError, UnicodeDecodeError):
            pass
    elif isMac:
        subprocess.call(('open', path))
    else:
        subprocess.call(("xdg-open", path))



class GlossaryExporter(Exporter):
    """
    Glossary superclass, never instantiated directly
    """

    key = ""
    ext = ".html"
    hideTags = True
    includeSched = False
    glossary = True
    
    exportclass = "htmlglossary"
    html_opening = html_start
    html_ending = html_stop
    user_style = default_user_style
    base = ""
    header = ""
    card_element = ""
    style = ""

    def __init__(self, col):
        Exporter.__init__(self, col)
        
        # Support for custom user CSS
        data_path = os.path.join(addon_path, "user_data")
        user_css_file = os.path.join(data_path, "user.css")
        try:
            with open(user_css_file, "r") as f:
                self.user_style = f.read()
        except (IOError, OSError):
            try:
                with open(user_css_file, "w+") as f:
                    # write default style
                    f.write(self.user_style)
            except (IOError, OSError):
                pass

        if isWin:
            # xhtml2pdf needs the media collection base path for images
            # to work. Weirdly enough, supplying the path on Linux
            # causes images to stop rendering. Not sure if macOS
            # behaves the same.
            self.media_path = mw.col.media.dir().encode(sys_encoding)
        else:
            self.media_path = None


    def escapeText(self, text):
        """Adjust source text formatting for use in glossaries"""
        # Strip off the repeated question in answer if exists
        text = re.sub("(?si)^.*<hr id=answer>\n*", "", text)
        text = re.sub("(?si)<style.*?>.*?</style>", "", text)
        # Escape newlines, tabs and CSS.
        text = text.replace("\n", "")
        text = text.replace("\t", "")
        text = re.sub("(?i)<style>.*?</style>", "", text)
        # Remove extraneous line-breaks
        if REMOVE_EXTRA_LINEBREAKS:
            # extra <br>s
            text = re.sub("(<br>|<br />|<br/>){3,}", "<br /><br />", text)
            # empty divs, etc.
            soup = BeautifulSoup(text)
            for x in soup.findAll():
                # don't remove if elm contains singleton tag we want to preserve
                if (
                    x.name not in ("br", "hr", "img") 
                    and not x.findAll(("img", "hr"), recursive=True) 
                    and not x.text
                ):
                    x.extract()
            text = unicode(soup)
        return text


    def getCountCSS(self, cnt, card):
        if self.includeSched:
            ease = card.factor/10.0
            if ease < EASE_THRESHOLD_LOWER:
                return "color:white;background-color:#F68787;"
            elif ease > EASE_THRESHOLD_UPPER:
                return "color:white;background-color:#7CFF9E;"
        return ""


    def doExport(self, file):
        cids = self.cardIds()
        deckname = self.col.decks.nameOrNone(self.did) or ""
        deckname = deckname.replace("::", " > ")
        total = len(cids)
        date = datetime.datetime.today().strftime('%Y-%m-%d')

        cnt, body_elms = 1, []
        for cid in cids:
            c = self.col.getCard(cid)

            countcss = self.getCountCSS(cnt, c)
            countstyle = """style='{}'""".format(countcss)

            card_elm = self.card_element.format(
                exportclass=self.exportclass,
                count=cnt, countstyle=countstyle,
                question=self.escapeText(c.q()),
                answer=self.escapeText(c.a())
            )
            body_elms.append(card_elm)
            cnt += 1

        html_opening = self.html_opening.format(
                            style=self.style + self.user_style,
                            base=self.base)
        if self.header:
            html_opening += self.header.format(
                title=deckname, total=total, date=date)
        html = html_opening + "".join(body_elms) + self.html_ending

        self.writeExportFile(html, file)


    def writeExportFile(self, html, file):
        file.write(html.encode("utf8"))


class HTMLGlossaryExporter(GlossaryExporter):
    """
    HTML Exporter for printing in Chrome
    """

    key = "Export Two-column HTML Glossary"
    html_opening = html_start
    html_ending = browser_wrapper_close + html_stop
    header = browser_static + browser_wrapper_open
    card_element = card_element_table
    style = xpdf_style_table + browser_style_twocol

    def __init__(self, col):
        GlossaryExporter.__init__(self, col)
        self.base = getBase(mw.col).encode("utf8")

    def exportInto(self, path):
        GlossaryExporter.exportInto(self, path)
        openLink(path.encode("utf-8"))


class PDFGlossaryExporter(GlossaryExporter):
    """
    PDF Glossary superclass, never instantiated directly
    """

    ext = ".pdf"
    exportclass = "pdfglossary"

    def __init__(self, col):
        GlossaryExporter.__init__(self, col)
        global pisa
        if not pisa:
            # import on first execution to improve Anki startup times
            from xhtml2pdf import pisa


    def escapeText(self, text):
        text = GlossaryExporter.escapeText(self, text)
        # prevent side-by-side images from overextending into other columns
        text = re.sub(r"(<img.+?>)(\s+)?(<img.+?>)", r"\1<br />\3", text)
        # remove nbsps causing word-wrap issues
        text = text.replace("&nbsp;", " ")
        return text


    def getCountCSS(self, cnt, card):
        css = GlossaryExporter.getCountCSS(self, cnt, card)

        # set column width manually since xhtml2pdf doesn't support
        # dynamic widths
        if cnt >= 10000:
            pct = "16"
        elif cnt >= 1000:
            pct = "13"
        elif cnt >= 100:
            pct = "10"
        elif cnt >= 10:
            pct = "8"
        elif cnt < 10:
            pct = "5"

        css += "width: {}%;".format(pct)

        return css
        

    def writeExportFile(self, html, file):
        # convert HTML to PDF (dest is a file handle)
        pisa.CreatePDF(html,
            dest=file,
            path=self.media_path # required on Windows
        )


    def exportInto(self, path):
        tooltip("Generating PDF. This might take a while.")
        GlossaryExporter.exportInto(self, path)
        openFile(path.encode("utf-8"))


class TwoColA4PDFGlossaryExporter(PDFGlossaryExporter):
    """
    PDF Glossary exporter: Two-column layout, A4 page
    """

    key = "Two-column PDF Glossary [A4]"
    header = xpdf_static
    card_element = card_element_table
    style = xpdf_page_twocol_a4 + xpdf_style_table

    def __init__(self, col):
        PDFGlossaryExporter.__init__(self, col)


class TwoColLetterPDFGlossaryExporter(PDFGlossaryExporter):
    """
    PDF Glossary exporter: Two-column layout, Letter page
    """

    key = "Two-column PDF Glossary [Letter]"
    header = xpdf_static
    card_element = card_element_table
    style = xpdf_page_twocol_letter + xpdf_style_table

    def __init__(self, col):
        PDFGlossaryExporter.__init__(self, col)


class OneColPDFGlossaryExporter(PDFGlossaryExporter):
    """
    One-column PDF Glossary superclass, never instantiated directly
    """

    def __init__(self, col):
        PDFGlossaryExporter.__init__(self, col)

    def getCountCSS(self, cnt, card):
        css = GlossaryExporter.getCountCSS(self, cnt, card)

        # set column width manually since xhtml2pdf doesn't support
        # dynamic widths
        if cnt >= 10000:
            pct = "10"
        elif cnt >= 1000:
            pct = "8"
        elif cnt >= 100:
            pct = "6"
        elif cnt >= 10:
            pct = "4"
        elif cnt < 10:
            pct = "4"

        css += "width: {}%;".format(pct)

        return css


class OneColA4PDFGlossaryExporter(OneColPDFGlossaryExporter):
    """
    PDF Glossary exporter: Two-column layout, A4 page
    """

    key = "One-column PDF Glossary [A4]"
    header = xpdf_static
    card_element = card_element_table
    style = xpdf_page_onecol_a4 + xpdf_style_table + xpdf_style_table_onecol

    def __init__(self, col):
        OneColPDFGlossaryExporter.__init__(self, col)


class OneColLetterPDFGlossaryExporter(OneColPDFGlossaryExporter):
    """
    PDF Glossary exporter: Two-column layout, A4 page
    """

    key = "One-column PDF Glossary [Letter]"
    header = xpdf_static
    card_element = card_element_table
    style = xpdf_page_onecol_letter + xpdf_style_table + xpdf_style_table_onecol

    def __init__(self, col):
        OneColPDFGlossaryExporter.__init__(self, col)


exporters = (HTMLGlossaryExporter,
    OneColA4PDFGlossaryExporter, OneColLetterPDFGlossaryExporter,
    TwoColA4PDFGlossaryExporter, TwoColLetterPDFGlossaryExporter,
)


# Hooks

def exporterChanged(self, idx):
    """Ability to only show includeSched checkbutton for our exporters"""
    from anki.exporting import exporters
    self.exporter = exporters()[idx][1](self.col)
    self.isApkg = (hasattr(self.exporter, "includeSched") 
                        and not hasattr(self.exporter, "glossary"))
    hasSchedToggle = hasattr(self.exporter, "glossary")
    self.isTextNote = hasattr(self.exporter, "includeTags")
    self.hideTags = hasattr(self.exporter, "hideTags")
    self.frm.includeSched.setVisible(self.isApkg or hasSchedToggle)
    if hasSchedToggle:
        self.frm.includeSched.setChecked(False)
    self.frm.includeMedia.setVisible(self.isApkg)
    self.frm.includeTags.setVisible(
        not self.isApkg and not self.hideTags)

ExportDialog.exporterChanged = exporterChanged


def addExporters(exps):
    """Add exporters to export dialog"""
    def theid(obj):
        return ("%s (*%s)" % (obj.key, obj.ext), obj)
    for exporter in exporters:
        exps.append(theid(exporter))
    

addHook("exportersList", addExporters)