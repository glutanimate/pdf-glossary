Export your decks as compact HTML/PDF glossaries that are ideal for printing reference sheets of your cards!

**SCREENSHOTS**

*Two-column format*

![](https://raw.githubusercontent.com/glutanimate/pdf-glossary/master/screenshots/twocol.png)

*One-column format*

![](https://raw.githubusercontent.com/glutanimate/pdf-glossary/master/screenshots/onecol.png)

**COMPATIBILITY**

This add-on only works with Anki's stable release branch (2.0.x ≥ 2.0.30). The 2.1 beta branch is **not supported** at this point in time.

**USAGE**

The add-on integrates itself with Anki's regular Export menu, which can be invoked either through *File* → *Export*, or by clicking on the gear next to a deck and selecting *Export*. With the add-on installed, you will be able to choose from 5 additional export options:

- **Two-column HTML glossary** – This will generate an HTML file that is designed to be printed in Chrome. The page layout might not work properly on other browsers.

    You should use this when exporting large collections, or cards with complex formatting as Chrome will be able to parse them much better than the PDF Exporter. In order to convert these HTML exports to PDF documents you can use Chrome's "Print to PDF" option.

- **One-column PDF Glossary** (page size either *A4* or *Letter*) – Will directly generate a PDF glossary in a one-column page layout

- **Two-column PDF Glossary** (page size either *A4* or *Letter*) – Will directly generate a PDF glossary in a two-column page layout

The add-on also has limited abilites to export some of your scheduling information. If you check the corresponding checkbox, all cards that surpass or fall below a certain ease percentage will be highlighted in green or red, respectively.

**CONFIGURATION**

*Overview*

Depending on your card templates and the type of formatting you use, it could be important to adjust the styling of your content before exporting it. For these use cases the add-on comes with a user-customizable CSS file that is located under `user_data/user.css` in the add-on directory. CSS rules you add to this file will be respected both for HTML and CSS exports. The file is read anew on each export, so you can edit it while running Anki in parallel.

Please note, however, that PDF exports only support a subset of CSS rules. These are listed in [xhtml2pdf`s reference guide](https://xhtml2pdf.readthedocs.io/en/latest/reference.html#supported-css-properties).

*Examples*

Changing the text-alignment in question and answer columns:

    td.question, td.answer {
        text-align: center;
    }

Setting the answer and question column sizes to be equal:

    td.question {
        width: 100%; /* default: 50% */
    }
    td.answer {
        width: 100%; /* default: 100% */
    }

Setting a custom image width:

    img {
        width: 100px;
    }

Hiding a specific HTML element that you might not want to export:

    div.myClass {
        display: none;
    }

**LIMITATIONS**

The PDF export is pretty slow, so please don't use it on a deck with too many cards. Exporting a deck of ≈6400 cards takes my machine about 5 minutes. The process can also be very memory-intensive, in some instances going up as far as 2GB. How much RAM is used depends on a number of factors, including the card formatting and number of embedded images. This memory cache might not be cleared properly after an export session. For that reason you might consider restarting Anki after exporting a larger card collection.

The performance issues can largely be attributed to the PDF exporting library used. Unfortunately there is no way to further optimize it. Nor is there another viable alternative that would work with Anki 2.0. Once Anki 2.1 becomes stable it might be possible to switch to a better alternative.

Another limitation lies in the type of content the add-on can process. As pointed out above, xhtml2pdf only supports a subset of CSS properties. The same also applies to advanced formatting that might rely on JavaScript or complex HTML layouts. Any particularly involved formatting will not work properly. For instance, if your cards contain larger tables created with the Power Format Pack add-on, chances are that they won't be rendered correctly simpy because they just don't fit inside the limited space on each page / column.

**CHANGELOG**

2017-09-12 – Initial release

**SUPPORT**

Please **do not report issues or bugs in the review section below**, as I will not be able to reply to them nor help you. Instead, please report all issues you encounter either on [GitHub](https://github.com/glutanimate/pdf-glossary/issues), or by posting a new thread on the [Anki add-on support forums](https://anki.tenderapp.com/discussions/add-ons) while mentioning the name of the affected add-on in your thread title.

**CREDITS AND LICENSE**

*Copyright (c) 2017 [Glutanimate](https://github.com/Glutanimate)*

This add-on was made possible with the kind support of Evan (runninreb23). All credit for the initial idea goes to him.

The deck samples in the screenshots are based on the [Brosencephalon deck](https://www.brosencephalon.com/) and used with the kind permission of Amreet Siddhu.

Licensed under the [GNU AGPLv3](https://www.gnu.org/licenses/agpl.html). The code for this add-on is available on [![GitHub icon](https://glutanimate.com/logos/github.svg) GitHub](https://github.com/Glutanimate/pdf-glossary). For more information on the licensing terms and other software shipped with this package please check out the [README](https://github.com/Glutanimate/pdf-glossary#credits).

**MORE RESOURCES**

A lot of my add-ons were commissioned by other Anki users. If you enjoy my work and would like to hire my services to work on an add-on or new feature, please feel free to reach out to me at:  ![Email icon](https://glutanimate.com/logos/email.svg) <em>ankiglutanimate [αt] gmail . com</em>

Want to stay up-to-date with my latest add-on releases and updates? Feel free to follow me on Twitter: [![Twitter bird](https://glutanimate.com/logos/twitter.svg)@Glutanimate](https://twitter.com/glutanimate)

New to Anki? Make sure to check out my YouTube channel where I post weekly tutorials on Anki add-ons and related topics: [![YouTube playbutton](https://glutanimate.com/logos/youtube.svg) / Glutanimate](https://www.youtube.com/c/glutanimate)
