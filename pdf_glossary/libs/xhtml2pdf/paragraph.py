#!/bin/env/python
# -*- coding: utf-8 -*-

# Copyright 2010 Dirk Holtwick, holtwick.it
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A paragraph class to be used with ReportLab Platypus.

TODO
====

- Bullets
- Weblinks and internal links
- Borders and margins (Box)
- Underline, Background, Strike
- Images
- Hyphenation
+ Alignment
+ Breakline, empty lines
+ TextIndent
- Sub and super

"""

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
import six

class Style(dict):
    """
    Style.

    Single place for style definitions: Paragraphs and Fragments. The
    naming follows the convention of CSS written in camelCase letters.
    """

    DEFAULT = {
        "textAlign": TA_LEFT,
        "textIndent": 0.0,
        "width": None,
        "height": None,
        "fontName": "Times-Roman",
        "fontSize": 10.0,
        "color": Color(0, 0, 0),
        "lineHeight": 1.5,
        "lineHeightAbsolute": None,
        "pdfLineSpacing": 0,
        "link": None,
    }

    def __init__(self, **kw):
        self.update(self.DEFAULT)
        self.update(kw)
        self.spaceBefore = 0
        self.spaceAfter = 0
        self.keepWithNext = False


class Box(dict):
    """
    Box.

    Handles the following styles:

        backgroundColor, backgroundImage
        paddingLeft, paddingRight, paddingTop, paddingBottom
        marginLeft, marginRight, marginTop, marginBottom
        borderLeftColor, borderLeftWidth, borderLeftStyle
        borderRightColor, borderRightWidth, borderRightStyle
        borderTopColor, borderTopWidth, borderTopStyle
        borderBottomColor, borderBottomWidth, borderBottomStyle

    Not used in inline Elements:

        paddingTop, paddingBottom
        marginTop, marginBottom

    """

    name = "box"

    def drawBox(self, canvas, x, y, w, h):
        canvas.saveState()

        # Background
        bg = self.get("backgroundColor", None)
        if bg is not None:
            # draw a filled rectangle (with no stroke) using bg color
            canvas.setFillColor(bg)
            canvas.rect(x, y, w, h, fill=1, stroke=0)

        # Borders
        def _drawBorderLine(bstyle, width, color, x1, y1, x2, y2):
            # We need width and border style to be able to draw a border
            if width and bstyle:
                # If no color for border is given, the text color is used (like defined by W3C)
                if color is None:
                    color = self.get("textColor", Color(0, 0, 0))
                    # print "Border", bstyle, width, color
                if color is not None:
                    canvas.setStrokeColor(color)
                    canvas.setLineWidth(width)
                    canvas.line(x1, y1, x2, y2)

        _drawBorderLine(self.get("borderLeftStyle", None),
                        self.get("borderLeftWidth", None),
                        self.get("borderLeftColor", None),
                        x, y, x, y + h)
        _drawBorderLine(self.get("borderRightStyle", None),
                        self.get("borderRightWidth", None),
                        self.get("borderRightColor", None),
                        x + w, y, x + w, y + h)
        _drawBorderLine(self.get("borderTopStyle", None),
                        self.get("borderTopWidth", None),
                        self.get("borderTopColor", None),
                        x, y + h, x + w, y + h)
        _drawBorderLine(self.get("borderBottomStyle", None),
                        self.get("borderBottomWidth", None),
                        self.get("borderBottomColor", None),
                        x, y, x + w, y)

        canvas.restoreState()


class Fragment(Box):
    """
    Fragment.

    text:       String containing text
    fontName:
    fontSize:
    width:      Width of string
    height:     Height of string
    """

    name = "fragment"
    isSoft = False
    isText = False
    isLF = False


    def calc(self):
        self["width"] = 0


class Word(Fragment):
    """
    A single word.
    """

    name = "word"
    isText = True

    def calc(self):
        """
        XXX Cache stringWith if not accelerated?!
        """
        self["width"] = stringWidth(self["text"], self["fontName"], self["fontSize"])


class Space(Fragment):
    """
    A space between fragments that is the usual place for line breaking.
    """

    name = "space"
    isSoft = True

    def calc(self):
        self["width"] = stringWidth(" ", self["fontName"], self["fontSize"])


class LineBreak(Fragment):
    """
    Line break.
    """

    name = "br"
    isSoft = True
    isLF = True

    pass


class BoxBegin(Fragment):
    name = "begin"

    def calc(self):
        self["width"] = self.get("marginLeft", 0) + self.get("paddingLeft", 0) # + border if border

    def draw(self, canvas, y):
        # if not self["length"]:
        x = self.get("marginLeft", 0) + self["x"]
        w = self["length"] + self.get("paddingRight", 0)
        h = self["fontSize"]
        self.drawBox(canvas, x, y, w, h)


class BoxEnd(Fragment):
    name = "end"

    def calc(self):
        self["width"] = self.get("marginRight", 0) + self.get("paddingRight", 0) # + border


class Image(Fragment):
    name = "image"

    pass


class Line(list):
    """
    Container for line fragments.
    """

    LINEHEIGHT = 1.0

    def __init__(self, style):
        self.width = 0
        self.height = 0
        self.isLast = False
        self.style = style
        self.boxStack = []
        list.__init__(self)

    def doAlignment(self, width, alignment):
        # Apply alignment
        if alignment != TA_LEFT:
            lineWidth = self[- 1]["x"] + self[- 1]["width"]
            emptySpace = width - lineWidth
            if alignment == TA_RIGHT:
                for frag in self:
                    frag["x"] += emptySpace
            elif alignment == TA_CENTER:
                for frag in self:
                    frag["x"] += emptySpace / 2.0
            elif alignment == TA_JUSTIFY and not self.isLast: # XXX last line before split
                delta = emptySpace / (len(self) - 1)
                for i, frag in enumerate(self):
                    frag["x"] += i * delta

        # Boxes
        for frag in self:
            x = frag["x"] + frag["width"]
            # print "***", x, frag["x"]
            if isinstance(frag, BoxBegin):
                self.boxStack.append(frag)
            elif isinstance(frag, BoxEnd):
                if self.boxStack:
                    frag = self.boxStack.pop()
                    frag["length"] = x - frag["x"]

        # Handle the rest
        for frag in self.boxStack:
            # print "***", x, frag["x"]
            frag["length"] = x - frag["x"]

    def doLayout(self, width):
        """
        Align words in previous line.
        """

        # Calculate dimensions
        self.width = width
        self.height = self.lineHeight = max(frag.get("fontSize", 0) * self.LINEHEIGHT for frag in self)

        # Apply line height
        self.fontSize = max(frag.get("fontSize", 0) for frag in self)
        y = (self.lineHeight - self.fontSize) # / 2
        for frag in self:
            frag["y"] = y

        return self.height

    def dumpFragments(self):
        print ("Line", 40 * "-")
        for frag in self:
            print ("%s") % frag.get("text", frag.name.upper()),
        print()


class Text(list):
    """
    Container for text fragments.

    Helper functions for splitting text into lines and calculating sizes
    and positions.
    """

    def __init__(self, data=None, style=None):
        # Mutable arguments are a shit idea
        if data is None:
            data = []

        self.lines = []
        self.width = 0
        self.height = 0
        self.maxWidth = 0
        self.maxHeight = 0
        self.style = style
        list.__init__(self, data)

    def calc(self):
        """
        Calculate sizes of fragments.
        """
        for word in self:
            word.calc()

    def splitIntoLines(self, maxWidth, maxHeight, splitted=False):
        """
        Split text into lines and calculate X positions. If we need more
        space in height than available we return the rest of the text
        """
        self.lines = []
        self.height = 0
        self.maxWidth = self.width = maxWidth
        self.maxHeight = maxHeight
        boxStack = []

        style = self.style
        x = 0

        # Start with indent in first line of text
        if not splitted:
            x = style["textIndent"]

        lenText = len(self)
        pos = 0
        while pos < lenText:

            # Reset values for new line
            posBegin = pos
            line = Line(style)

            # Update boxes for next line
            for box in copy.copy(boxStack):
                box["x"] = 0
                line.append(BoxBegin(box))

            while pos < lenText:

                # Get fragment, its width and set X
                frag = self[pos]
                fragWidth = frag["width"]
                frag["x"] = x
                pos += 1

                # Keep in mind boxes for next lines
                if isinstance(frag, BoxBegin):
                    boxStack.append(frag)
                elif isinstance(frag, BoxEnd):
                    boxStack.pop()

                # If space or linebreak handle special way
                if frag.isSoft:
                    if frag.isLF:
                        line.append(frag)
                        break
                        # First element of line should not be a space
                    if x == 0:
                        continue
                        # Keep in mind last possible line break

                # The elements exceed the current line
                elif fragWidth + x > maxWidth:
                    break

                # Add fragment to line and update x
                x += fragWidth
                line.append(frag)

            # Remove trailing white spaces
            while line and line[-1].name in ("space", "br"):
                # print "Pop",
                line.pop()

            # Add line to list
            line.dumpFragments()
            # if line:
            self.height += line.doLayout(self.width)
            self.lines.append(line)

            # If not enough space for current line force to split
            if self.height > maxHeight:
                return posBegin

            # Reset variables
            x = 0

        # Apply alignment
        self.lines[- 1].isLast = True
        for line in self.lines:
            line.doAlignment(maxWidth, style["textAlign"])

        return None

    def dumpLines(self):
        """
        For debugging dump all line and their content
        """
        for i, line in enumerate(self.lines):
            print ("Line %d:") % i,
            line.dumpFragments()


class Paragraph(Flowable):
    """
    A simple Paragraph class respecting alignment.

    Does text without tags.

    Respects only the following global style attributes:
    fontName, fontSize, leading, firstLineIndent, leftIndent,
    rightIndent, textColor, alignment.
    (spaceBefore, spaceAfter are handled by the Platypus framework.)

    """
    def __init__(self, text, style, debug=False, splitted=False, **kwDict):

        Flowable.__init__(self)

        self.text = text
        self.text.calc()
        self.style = style
        self.text.style = style

        self.debug = debug
        self.splitted = splitted

        # More attributes
        for k, v in six.iteritems(kwDict):
            setattr(self, k, v)

        # set later...
        self.splitIndex = None

    # overwritten methods from Flowable class
    def wrap(self, availWidth, availHeight):
        """
        Determine the rectangle this paragraph really needs.
        """

        # memorize available space
        self.avWidth = availWidth
        self.avHeight = availHeight

        if self.debug:
            print ("*** wrap (%f, %f)") % (availWidth, availHeight)

        if not self.text:
            if self.debug:
                print ("*** wrap (%f, %f) needed") % (0, 0)
            return 0, 0

        # Split lines
        width = availWidth
        self.splitIndex = self.text.splitIntoLines(width, availHeight)

        self.width, self.height = availWidth, self.text.height

        if self.debug:
            print ("*** wrap (%f, %f) needed, splitIndex %r") % (self.width, self.height, self.splitIndex)

        return self.width, self.height

    def split(self, availWidth, availHeight):
        """
        Split ourself in two paragraphs.
        """

        if self.debug:
            print ("*** split (%f, %f)") % (availWidth, availHeight)

        splitted = []
        if self.splitIndex:
            text1 = self.text[:self.splitIndex]
            text2 = self.text[self.splitIndex:]
            p1 = Paragraph(Text(text1), self.style, debug=self.debug)
            p2 = Paragraph(Text(text2), self.style, debug=self.debug, splitted=True)
            splitted = [p1, p2]

            if self.debug:
                print ("*** text1 %s / text %s") % (len(text1), len(text2))

        if self.debug:
            print ('*** return %s') % self.splitted

        return splitted

    def draw(self):
        """
        Render the content of the paragraph.
        """

        if self.debug:
            print ("*** draw")

        if not self.text:
            return

        canvas = self.canv
        style = self.style

        canvas.saveState()

        # Draw box arround paragraph for debugging
        if self.debug:
            bw = 0.5
            bc = Color(1, 1, 0)
            bg = Color(0.9, 0.9, 0.9)
            canvas.setStrokeColor(bc)
            canvas.setLineWidth(bw)
            canvas.setFillColor(bg)
            canvas.rect(
                style.leftIndent,
                0,
                self.width,
                self.height,
                fill=1,
                stroke=1)

        y = 0
        dy = self.height
        for line in self.text.lines:
            y += line.height
            for frag in line:

                # Box
                if hasattr(frag, "draw"):
                    frag.draw(canvas, dy - y)

                # Text
                if frag.get("text", ""):
                    canvas.setFont(frag["fontName"], frag["fontSize"])
                    canvas.setFillColor(frag.get("color", style["color"]))
                    canvas.drawString(frag["x"], dy - y + frag["y"], frag["text"])

                # XXX LINK
                link = frag.get("link", None)
                if link:
                    _scheme_re = re.compile('^[a-zA-Z][-+a-zA-Z0-9]+$')
                    x, y, w, h = frag["x"], dy - y, frag["width"], frag["fontSize"]
                    rect = (x, y, w, h)
                    if isinstance(link, six.text_type):
                        link = link.encode('utf8')
                    parts = link.split(':', 1)
                    scheme = len(parts) == 2 and parts[0].lower() or ''
                    if _scheme_re.match(scheme) and scheme != 'document':
                        kind = scheme.lower() == 'pdf' and 'GoToR' or 'URI'
                        if kind == 'GoToR':
                            link = parts[1]

                        canvas.linkURL(link, rect, relative=1, kind=kind)
                    else:
                        if link[0] == '#':
                            link = link[1:]
                            scheme = ''
                        canvas.linkRect("", scheme != 'document' and link or parts[1], rect, relative=1)

        canvas.restoreState()


if __name__ == "__main__":
    # TODO: This should be a test, not a main!
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.styles import *
    from reportlab.rl_config import *
    from reportlab.lib.units import *

    import os
    import copy
    import re

    styles = getSampleStyleSheet()

    ALIGNMENTS = (TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY)

    TEXT = """
    Lörem ipsum dolor sit amet, consectetur adipisicing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
    ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
    officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet,
    consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore
    et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
    ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
    dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat
    nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt
    in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum
    dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
    incididunt ut labore et dolore magna aliqua.
    """.strip()

    def textGenerator(data, fn, fs):
        i = 1
        for word in re.split('\s+', data):
            if word:
                yield Word(
                    text="[%d|%s]" % (i, word),
                    fontName=fn,
                    fontSize=fs
                )
                yield Space(
                    fontName=fn,
                    fontSize=fs
                )

    def createText(data, fn, fs):
        text = Text(list(textGenerator(data, fn, fs)))
        return text

    def makeBorder(width, style="solid", color=Color(1, 0, 0)):
        return dict(
            borderLeftColor=color,
            borderLeftWidth=width,
            borderLeftStyle=style,
            borderRightColor=color,
            borderRightWidth=width,
            borderRightStyle=style,
            borderTopColor=color,
            borderTopWidth=width,
            borderTopStyle=style,
            borderBottomColor=color,
            borderBottomWidth=width,
            borderBottomStyle=style
        )

    def test():
        doc = SimpleDocTemplate("test.pdf")
        story = []

        style = Style(fontName="Helvetica", textIndent=24.0)
        fn = style["fontName"]
        fs = style["fontSize"]
        sampleText1 = createText(TEXT[:100], fn, fs)
        sampleText2 = createText(TEXT[100:], fn, fs)

        text = Text(sampleText1 + [
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="TrennbarTrennbar",
                pairs=[("Trenn-", "barTrennbar")],
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Normal",
                color=Color(1, 0, 0),
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="gGrößer",
                fontName=fn,
                fontSize=fs * 1.5),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Bold",
                fontName="Times-Bold",
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="jItalic",
                fontName="Times-Italic",
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),

            # <span style="border: 1px solid red;">ipsum <span style="border: 1px solid green; padding: 4px; padding-left: 20px; background: yellow; margin-bottom: 8px; margin-left: 10px;">
            # Lo<font size="12pt">re</font>m</span> <span style="background:blue; height: 30px;">ipsum</span> Lorem</span>

            BoxBegin(
                fontName=fn,
                fontSize=fs,
                **makeBorder(0.5, "solid", Color(0, 1, 0))),
            Word(
                text="Lorem",
                fontName="Times-Bold",
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName="Times-Bold",
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            BoxBegin(
                fontName=fn,
                fontSize=fs,
                backgroundColor=Color(1, 1, 0),
                **makeBorder(1, "solid", Color(1, 0, 0))),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            BoxEnd(),
            Space(
                fontName=fn,
                fontSize=fs),
            Word(
                text="Lorem",
                fontName=fn,
                fontSize=fs),
            Space(
                fontName=fn,
                fontSize=fs),
            BoxEnd(),

            LineBreak(
                fontName=fn,
                fontSize=fs),
            LineBreak(
                fontName=fn,
                fontSize=fs),
        ] + sampleText2)

        story.append(Paragraph(
            copy.copy(text),
            style,
            debug=0))

        for i in range(10):
            style = copy.deepcopy(style)
            style["textAlign"] = ALIGNMENTS[i % 4]
            text = createText(("(%d) " % i) + TEXT, fn, fs)
            story.append(Paragraph(
                copy.copy(text),
                style,
                debug=0))
        doc.build(story)

    test()
    os.system("start test.pdf")

    # FIXME: Useless line?
    # createText(TEXT, styles["Normal"].fontName, styles["Normal"].fontSize)
