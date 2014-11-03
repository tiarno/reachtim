Title: Manipulate PDFs with Python
Status: Draft
Date: 11-07-2014
Summary: Methods for manipulating and extracting information from PDF documents using Python

**Table of Contents**

[TOC]

# Overview

PDF documents are beautiful things, but that beauty is often only skin deep. Inside they might have any number of structures that are difficult to understand and definitely difficult to get at. The PDF specification provides rules, but it is programmers who follow them, and they, like all programmers, are a creative bunch.

That means that in the end, that beautiful PDF document is really meant to be read and its internals are not to be messed with. Well, we are programmers too, and we are a creative bunch, so we will see how we can get at those internals.

The best advice if you have to extract or add information to a PDF is: **don't do it**. Well, don't do it if there is any way you can get access to the information further upstream. If you want to scrape that spreadsheet data in a PDF, see if you can get access to it before it became part of the PDF. Chances are, now that is is inside the PDF, it is just a bunch of lines and numbers  with no connection to its former structure of cells, formats, and headings. 

If you cannot get access to the information further upstream, this tutorial will show you some of the ways you can get to it inside the PDF using Python.

# Survey of Tools

There are several Python packages that can help. The following list displays some of the most popular ones.

 - ``pdfrw`` Last update: 9/2012. Read and write PDF files; watermarking, copying images from one PDF to another. Includes sample code. [repo](https://code.google.com/p/pdfrw/). Python 2.5--2.7. MIT License.
 - ``slate`` Last update: 8/2014. Simplifies extracting text from PDF files. Wrapper around ``PDFMiner``. Includes documentation on GitHub and PyPI. [repo](https://github.com/timClicks/slate). Python 2.6. GPL License.
 - ``PDFQuery`` Last update: 9/2014. PDF scraping with Jquery or XPath syntax. Requires ``PDFMiner``, ``pyquery`` and ``lxml`` libraries. Includes sample code, documentation. [repo](https://github.com/jcushman/pdfquery) Seems to be Python 2.x. MIT License.
 - ``PDFMiner`` Last update: 3/2014. Extracting text, images, object coordinates, metadata from PDF files. Pure Python. Includes sample code and command line interface; Google group and documentation. [repo](https://github.com/euske/pdfminer/) Python 2.x only. MIT License.
 - ``PyPdf2`` Last update: 8/2014. Split, merge, crop, etc. of PDF files. Pure Python. Includes sample code and command line interface, documentation. [repo](https://github.com/mstamy2/PyPDF2) Python 2 and 3. BSD License. 

Also, fdfmerge and reportlab

ReportLab is a software library that lets you create PDF documents. It can also create charts and data graphics in various bitmap and vector formats as well as PDF.

input 

## Related Tools

There are several non-Python tools available for manipulating PDF files in one way or another. If none of the Python solutions fit your situation, see the section [Other Tools](#othertools) for more information.

# Extracting Information: PDFMiner

The **PDFMiner** library excels at extracting data and coordinates from a PDF. In most cases, you can use the included command-line scripts to extract text (``pdf2txt.py``) or find objects and their coordinates (``dumppdf.py``), If you need to get more detailed if you're dealing with a particularly nasty PDF, you can import the package and use it as library. Install with ``pip``.

## The ``pdf2txt.py`` command line 

The library includes the ``pdf2txt.py`` command-line command, which you can use to extract text and images. The command supports many options and is very flexible. Some popular options are shown below. 

```bash
pdf2txt.py [options] filename.pdf
Options:
    -o output file name
    -p comma-separated list of page numbers to extract
    -c output codec (for examplek 'utf-8')
    -t output format (text/html/xml/tag[for Tagged PDFs])
    -I dirname (extract images from PDF into directory)
    -p password
```

It cannot recognize text drawn as images that would require optical character recognition. It also extracts the corresponding locations, font names, font sizes, writing direction (horizontal or vertical) for each text portion.

## The ``dumppdf.py`` command line 

The package also includes the ``dumppdf.py`` command-line command, which you can use to find the objects and their coordinates inside a PDF file.

```bash
dumppdf.py [options] filename.pdf
Options:
    -a dump all objects
    -p comma-separated list of page numbers to extract
    -E dirname (extract embedded files from the PDF into directory)
    -T dump the table of contents (bookmark outlines)
    -p password
```

more info in this in-depth article:
http://denis.papathanasiou.org/2010/08/04/extracting-text-images-from-pdf-files/

## Use as a Library

If you are writing Python already and you don't want to shell out to the command, you use the package as a library. For example, to extract text from a PDF:

    :::python
    from cStringIO import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, process_pdf
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams

    def to_txt(pdf_path):
        input_ = file(pdf_path, 'rb')
        output = StringIO()

        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        process_pdf(manager, converter, input_)

        return output.getvalue() 

Take this pdf for example. 

    http://www.metrovancouver.org/about/publications/Publications/2014_HILs.pdf

See the image in the header? You can find the info on which pdf object that is with the ``dumppdf.py`` command. Then you can use the same command to extract that image.

    dumppdf.py -a 2014_HILs.pdf |more

just get the toc: PDFMiner provides functions to access the document's table of contents ("Outlines").

    :::python
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument

    # Open a PDF document.
    fp = open('mypdf.pdf', 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, password)

    # Get the outlines of the document.
    outlines = document.get_outlines()
    for (level,title,dest,a,se) in outlines:
        print (level, title)


# Manipulating: PyPDF2

The original **pyPDF** library is officially no longer being developed but the **pyPDF2** library has taken up the project under the new name and continues to develop and enhance the library. The development team is dedicated to keeping the project backward compatible. Install with ``pip``.

Want to merge two PDFs? Like inserting the contents of one PDF into the content of another. Or maybe one of them is a one-page PDF containing a watermark and you want to layer the watermark onto each page of another PDF.

If your watermark PDF is named ``wmark.pdf``, this python code will stamp each page of the target PDF with the watermark.

    :::python
    from PyPDF2 import PdfFileWriter, PdfFileReader
    output = PdfFileWriter()
    
    ipdf = PdfFileReader(open('sample2e.pdf', 'rb'))
    wpdf = PdfFileReader(open('wmark.pdf', 'rb'))

    for i in xrange(ipdf.getNumPages()):
        page = ipdf.getPage(i)
        page.mergePage(wpdf.getPage(0))
        output.addPage(page)

    with open('/u/tiarno/newfile.pdf', 'wb') as f:
       output.write(f)

Split the PDF? Find out its metadata? Delete pages? No problem with **pyPDF2**. You can even rotate pages.

## Merge (like Append)

This snippet takes all the pdfs in a subdirectory named ``mypdfs`` and puts them in name-sorted order into a new pdf called ``output.pdf``

    :::python
    from PyPDF2 import PdfFileMerger, PdfFileReader
    import os
    merger = PdfFileMerger()
    files = [x for x in os.listdir('mypdfs') if x.endswith('.pdf')]
    for fname in sorted(files):
        merger.append(PdfFileReader(open(fname, 'rb')))

    merger.write("output.pdf")


## Delete

If you want to delete pages, just skip over them. For example, if you want to get rid of blank pages in ``source.pdf``:

    :::Python
    from PyPDF2 import PdfFileWriter, PdfFileReader
    infile = PdfFileReader('source.pdf', 'rb')
    output = PdfFileWriter()

    for i in xrange(infile.getNumPages()):
        p = infile.getPage(i)
        if p.getContents(): # getContent is None if blank
            output.add(p)


## Split
You want to split one pdf into separate one-page pdfs:

    :::python
    from pyPdf import PdfFileWriter, PdfFileReader 
    infile = PdfFileReader(open('source.pdf', 'rb'))

    for i in xrange(infile.getNumPages()):
        p = infile.getPage(i)
        outfile = PdfFileWriter()
        outfile.addPage(p)
        with open('page-%02d.pdf' % i, 'wb') as f:
            outfile.write(f)
     

## Slices

Say you have two pdfs resulting from scanning odd and even pages of a source document. You can merge them together, interleaving the pages as follows:

    :::python
    from pyPdf import PdfFileWriter, PdfFileReader 
    evens = PdfFileReader(open('even.pdf', 'rb'))
    odds = PdfFileReader(open('odd.pdf', 'rb'))
    all = PdfFileWriter()
    all.addBlankPage()
    for x,y in zip(odds.pages, evens.pages):
        all.addPage(x)
        all.addPage(y)
    while all.getNumPages() % 2:
        all.addBlankPage()
    with open('all.pdf', 'wb') as f:
        all.write(f)


## Other Operations

You can crop each page, add javascript, rotate, scale, and transform pages with the ``PyPDF2`` library. The documentation covers most uses and the sample code that comes with it shows you how to do each operation.

show a list of what the samples do.

possibilities:

- crop
- encrypt, decrypt
- rotate 
- get or add metadata
- create image from pdf page
- extract jpegs directly using magic numbers: http://nedbatchelder.com/blog/200712/extracting_jpgs_from_pdfs.html

set metadata

    :::python
    p = pyPdf.PdfFileWriter()
    infoDict = p._info.getObject()
    infoDict.update({pyPdf.generic.NameObject('/Cropped'):
                    pyPdf.generic.createStringObject(u'True')})

    info.get('/CreationDate')

# Other Tools [othertools]

- ``pdftk`` Merge, split PDF files and more. [info](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
- ``qpdf`` transforms PDF files. Useful for linearizing. [repo](http://qpdf.sourceforge.net/)
- ``ghostscript`` Interpreter for Postscript and PDF. [info](http://www.ghostscript.com/). [Command-line info](http://www.ghostscript.com/doc/9.15/Use.htm)
- ``XPDF`` project contains several useful tools such as ``pdffonts`` and ``pdfinfo``. [repo](http://www.foolabs.com/xpdf/)
    + ``pdffonts`` lists fonts used in a PDF file including information on font type, whether the font is embedded, etc. Part of the open-source ``Xpdf`` project. Licensed under GPL v2.
    ```bash
    > pdffonts 2014_HILs.pdf
    name                                 type              emb sub uni object ID
    ------------------------------- ----------------- --- --- --- ---------
    LFIGJB+ArialMT                  Type 1C           yes yes no      39  0
    LFIGLB+Arial-BoldMT             Type 1C           yes yes no      41  0
    ```

    + ``pdfinfo`` extracts contents of ``Info`` dictionary in a PDF file. Another part of the ``Xpdf`` project.
    ```bash
    > pdfinfo 2014_HILs.pdf
    Title:          HILs.pdf
    Subject:
    Keywords:
    Author:         Dave Ao
    Creator:        Acrobat PDFMaker 10.0 for Word
    Producer:       Acrobat Distiller 9.3.0 (Windows)
    CreationDate:   Mon Jun  2 11:16:53 2014
    ModDate:        Mon Jun  2 11:16:53 2014
    Tagged:         no
    Pages:          3
    Encrypted:      no
    Page size:      612 x 792 pts (letter)
    File size:      39177 bytes
    Optimized:      yes
    PDF version:    1.5
    ```

# Summary

There are some nasty PDFs out there. But there are several tools you can use to get what you need from them and Python enables you to get inside and scrape, split, merge, delete, and crop just about whatever you find.



