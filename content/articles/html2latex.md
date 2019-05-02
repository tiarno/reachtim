Title: Include HTML in LaTeX
Category: LaTeX
Date: 2019-May-06
Tags: how-to, 
Summary: How to include HTML content in your LaTeX documents.

### Introduction {: .article-title}

When I first started supporting multiple users of LaTeX in my day job,
a question I often heard was "How do I include an HTML table in my document?".
The answer was, of course, "It doesn't work that way; you can't do that."

But I found that, with some restrictions, you actually can include HTML by
converting it to PDF and including that in your LaTeX document. 

In this article I'll show how I do that for myself and how you can include
HTML pages that keep the original styles, colors and so forth once it has 
been converted to PDF. And if you need them, you can keep the internal links
from the HTML so they work in your final PDF.

### wkhtmltopdf {:.article-title}

The tool `wkhtmltopdf` converts HTML to PDF. The [wkhtmltopdf](https://wkhtmltopdf.org/)
website summarizes it:

> wkhtmltopdf and wkhtmltoimage are open source (LGPLv3) 
> command line tools to render HTML into PDF and various 
> image formats using the Qt WebKit rendering engine. 
> These run entirely "headless" and do not require a display or display service.
> 
> There is also a C library, if you're into that kind of thing.

It's a great tool. Here's the command I use (but put it all on one line):

```bash
/usr/local/bin/wkhtmltopdf -s Letter --no-background 
    --minimum-font-size 20 --no-outline --no-pdf-compression 
    --disable-external-links --enable-internal-links filename.html filename.pdf
```

Those options request the conversion to be rendered at letter-size with no background.
You can play around with the font size so it matches your documents font size.

Run this and you will have a single PDF with possibly multiple pages, using the same style, 
colors, and links that are in the HTML. 

#### If You Need to Create an Appendix  {:.article-title}

If you want the html you are including to be a separate chapter or appendix, then
instead of `--no-outline`, use this command instead:

```bash
--outline-depth 2 toc --xsl-style-sheet wk_toc.xsl --toc-header-text "Appendix A"
```

This asks for a table of contents using an XSL stylesheet with the specified header text.
Get my version of the `wk_toc.xsl` stylesheet here:

[gist.github.com/tiarno](https://gist.github.com/tiarno/094ca5dc7f9c3ae560af9ace975881d3)

Alternatively, you can get the file `wk_toc.xsl` yourself and if you know a 
little XSL, you can modify it for your needs. To generate the file, 
give this command::

    wkhtmltopdf --dump-default-toc-xsl

You can read more about the options in the `wkhtmltopdf` help documentation.

#### If You Need to Preserve Internal Links  {:.article-title}

Skip this section if you don't need to preserve internal links in 
the original HTML.  

If you do need internal links, you'll find that there is already a 
package to help with that, the `pax` package.
From the documentation:

> If PDF files are in­cluded us­ing pdfTEX, PDF an­no­ta­tions are stripped. 
> The pax project of­fers a so­lu­tion with­out al­ter­ing pdfTEX. 
> A Java pro­gram (pax.jar) parses the PDF file that will later be in­cluded. 
> The pro­gram then writes the data of the an­no­ta­tions into a file that can be read by TEX.

You can find it on [CTAN](https://www.ctan.org/pkg/pax).

This package works to retain the internal links from the included PDF. Unfortunately,
`wkhtmltopdf` creates the PDF in a way that is incompatible with this
Java program mentioned in the `pax` package documentation. 

I mention it here to save you going down the rabbit hole of trying to get 
it to work. You still need the `pax` package itself. But even though the 
Java jar file is fantastic for other pdfs,  with `wkhtmltopdf`, you need a 
different solution.  

Enter `PAXMaker`.

#### PAXMaker {:.article-title}

This little tool is available on my GitHub repository:
[PAXMaker](https://github.com/tiarno/paxmaker)

It requires the PyPDF2 Python package.
As you can read on that repo, you can use it by following these steps:

- Convert your html file to pdf with wkhtmltopdf
- Run `paxmaker.py` on the pdf (the program takes a single argument, the name of the pdf file)
- In the LaTeX file in which you want this pdf inserted: load the 
  `pdfpages` and `pax` packages, and include the pdf as described in the
  next section.

The `paxmaker.py` file does for the wkhtmltopdf-generated pdfs what the 
pax java program does for normal pdfs. It writes a `.pax` file that will be
read by the LaTeX `pax` package when you compile your final document.


### pdfpages {:.article-title}

So far you have generated a PDF file from the HTML, possibly preserving internal
links, and possibly creating it as an appendix. 
Now lets get that generated PDF into your LaTeX document.

You include external PDFs in a LaTeX document with the `pdfpages` package, by Andreas Matthias.
Get it on [CTAN](https://www.ctan.org/pkg/pdfpages).

> This package simplifies the insertion of external multi-page PDF
> documents into LaTeX documents. Pages can be freely selected and
> similar to psnup it is possible to put several logical pages onto
> each sheet of paper. Furthermore a lot of hypertext features like
> hyperlinks and article threads are provided. This package supports
> pdfTeX, VTeX, and XeTeX. With VTeX it is even possible to use
> this package to insert PostScript files, in addition to PDF files.

Then, at the location you want the original HTML pages to be included,
use this tag:

```latex
\IfFileExists{filename.pdf}
    {\includepdf[pages=-,addtotoc={1,subsection,2,title,htmllabel}]{filename}} 
    {\par\textcolor{red}{MISSING FILE!}}
```

The `\IfFileExists` command executes its first argument if the file exists or
its second argument if it doesn't exist. 

So if the file is present, you 
invoke the `includepdf` command from the `pdfpages` package, specifying
that it should include all pages (`pages=-`), it should add a title in the table
of contents at the subsection level with the  text `title`. 

If the file 
does not exist, it will put a paragraph in your document with a big red 
"MISSING FILE" warning.


### Summary {:.article-title}

You can include HTML in your LaTeX document as follows:

- convert your HTML to PDF with `wkhtmltopdf`
- *if you need internal links*, use PAXMaker to write a helper `pax` file
  and make sure you use the `pax` package in your LaTeX document
- use the `pdfpages` LaTeX package to include the PDF rendering of the HTML file.
- compile your final LaTeX document

This is a powerful method to include possibly many HTML pages into a LaTeX document.
You can use CSS with the HTML to make the included pages match your document.

