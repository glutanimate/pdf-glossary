# -*- coding: utf-8 -*-

"""
This file is part of the PDF Glossary add-on for Anki

HTML / CSS templates

Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

from __future__ import unicode_literals


default_user_style = """\
.cloze {
    font-weight: bold;
    color: blue;
}
"""


html_start = """\
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <style>{style}</style>
    {base}
</head>
<body>"""


html_stop = """\
</body>
</html>"""


xpdf_page_twocol_letter = """\
@page {
    size: letter portrait;
    @frame header_frame_left {           /* Static frame */
        -pdf-frame-content: header_content_left;
        left: 12.5mm; width: 150mm; top: 10mm; height: 10mm;
    }
    @frame header_frame_right {           /* Static frame */
        -pdf-frame-content: header_content_right;
        left: 170mm; width: 40mm; top: 10mm; height: 10mm;
    }
    @frame col1_frame {             /* Content frame 1 */
        left: 12.5mm; width: 90mm; top: 20mm; height: 220mm;
    }
    @frame col2_frame {             /* Content frame 2 */
        left: 115mm; width: 90mm; top: 20mm; height: 220mm;
    }
    @frame footer_frame {           /* Static frame */
        -pdf-frame-content: footer_content;
        left: 12.5mm; width: 190mm; top: 260mm; height: 10mm;
    }
}
"""

xpdf_page_onecol_letter = """\
@page {
    size: letter portrait;
    @frame header_frame_left {           /* Static frame */
        -pdf-frame-content: header_content_left;
        left: 12.5mm; width: 150mm; top: 10mm; height: 10mm;
    }
    @frame header_frame_right {           /* Static frame */
        -pdf-frame-content: header_content_right;
        left: 164mm; width: 40mm; top: 10mm; height: 10mm;
    }
    @frame main_frame {             /* Content frame 1 */
        left: 12.5mm; width: 187.5mm; top: 20mm; height: 220mm;
    }
    @frame footer_frame {           /* Static frame */
        -pdf-frame-content: footer_content;
        left: 12.5mm; width: 190mm; top: 260mm; height: 10mm;
    }
}
"""

xpdf_page_twocol_a4 = """\
@page {
    size: a4 portrait;
    @frame header_frame_left {           /* Static frame */
        -pdf-frame-content: header_content_left;
        left: 10mm; width: 150mm; top: 10mm; height: 10mm;
    }
    @frame header_frame_right {           /* Static frame */
        -pdf-frame-content: header_content_right;
        left: 166mm; width: 50mm; top: 10mm; height: 10mm;
    }
    @frame col1_frame {             /* Content frame 1 */
        left: 10mm; width: 90mm; top: 20mm; height: 260mm;
    }
    @frame col2_frame {             /* Content frame 2 */
        left: 110mm; width: 90mm; top: 20mm; height: 260mm;
    }
    @frame footer_frame {           /* Static frame */
        -pdf-frame-content: footer_content;
        left: 10mm; width: 190mm; top: 283mm; height: 10mm;
    }
}
"""

xpdf_page_onecol_a4 = """\
@page {
    size: a4 portrait;
    @frame header_frame_left {           /* Static frame */
        -pdf-frame-content: header_content_left;
        left: 10mm; width: 110mm; top: 10mm; height: 10mm;
    }
    @frame header_frame_right {           /* Static frame */
        -pdf-frame-content: header_content_right;
        left: 163mm; width: 40mm; top: 10mm; height: 10mm;
    }
    @frame main_frame {
        left: 10mm; width: 190mm; top: 20mm; height: 260mm;
    }
    @frame footer_frame {           /* Static frame */
        -pdf-frame-content: footer_content;
        left: 10mm; width: 190mm; top: 283mm; height: 10mm;
    }
}
"""

xpdf_style_table = """\
body {
    font-size: 8pt;
}
.header_content {
    font-size: 8pt;
    color: #616161;
}
#footer_content {
    text-align: right;
    font-size: 10pt;
}
hr {
    color: #C1C1C1;
    height: 1px;
}
table {
    font-size: 8pt;
}
td {
    vertical-align: top
}
td.count {
    width: 10%;
    font-size: 7pt;
    color: #888888;
}
td.question {
    width: 50%;
    font-weight: normal;
}
td.spacer {
    width: 7%;
}
"""

xpdf_style_table_onecol = """
body {
    font-size: 10pt;
}
.header_content {
    font-size: 9pt;
}
table {
    font-size: 10pt;
}
td.count {
    font-size: 8pt;
}
"""

browser_style_twocol = """\
body {
    font-size: 10pt;
    font-family: Helvetica, "Helvetia Neue", Arial, sans-serif;
}
.twocol {
    column-count: 2;
}
table {
    font-size: 10pt;
}
img {
    width: 100%;
}
td.question, td.answer {
    word-break: break-all;
    word-break: break-word;
    hyphens: auto;
}
td.count {
    font-size: 9pt;
    width: 5%;
}
td.question {
    width:30%;
}
td.spacer {
    width: 3%;
}
hr {
    color: #DADADA;
    border-width: 1px;
    height: 0px;
    border-style: solid;
}
.card {
    page-break-inside:avoid;
    page-break-after:auto;
}
.title {
    font-size: 11pt;
    margin-bottom: 1em;
}
"""

browser_wrapper_open = """<div class="twocol">"""
browser_wrapper_close = """</div>"""

browser_script_print = """\
<script>
    window.onload = window.print;
</script>
"""

browser_static = """\
<div class="header_content title">
    <span style="float: left;">Anki Glossary: {title} ({total} cards)</span> 
    <span style="float: right;">Created on {date}</span>
    <div style="clear:both;"></div>
</div>
"""


xpdf_static = """\
<div class="header_content" id="header_content_left">Anki Glossary: {title} ({total} cards)</div>
<div class="header_content" id="header_content_right">Generated on {date}</div>
<div id="footer_content"><pdf:pagenumber>
    of <pdf:pagecount>
</div>\
"""

card_element_table = """\
<div class="card {exportclass}">
    <table>
        <tr>
            <td class="count" {countstyle}>{count}.</td>
            <td class="question">{question}</td>
            <td class="spacer">&nbsp;</td>
            <td class="answer">{answer}</td>
        </tr>
    </table>
</div>
<hr>
"""

card_element_card = """
"""