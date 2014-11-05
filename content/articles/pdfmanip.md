Title: Manipulate PDFs with Python
Status: Draft
Date: 11-07-2014
Summary: Methods for manipulating and extracting information from PDF documents using Python

**Table of Contents**

[TOC]

# Overview

PDF documents are beautiful things, but that beauty is often only skin deep. Inside, they might have any number of structures that are difficult to understand and exasperating to get at. The PDF reference specification (ISO 32000-1) provides rules, but it is programmers who follow them, and they, like all programmers, are a creative bunch.

That means that in the end, a beautiful PDF document is really meant to be read and its internals are not to be messed with. Well, we are programmers too, and we are a creative bunch, so we will see how we can get at those internals.

Still, the best advice if you have to extract or add information to a PDF is: **don't do it**. Well, don't do it if there is any way you can get access to the information further upstream. If you want to scrape that spreadsheet data in a PDF, see if you can get access to it before it became part of the PDF. Chances are, now that is is inside the PDF, it is just a bunch of lines and numbers  with no connection to its former structure of cells, formats, and headings. 

If you cannot get access to the information further upstream, this tutorial will show you some of the ways you can get to it inside the PDF using Python.

# Survey of Tools

There are several Python packages that can help. The following list displays some of the most popular ones (undoubtedly I've omitted some tools).

 ``pdfrw`` 
 : Last update: 2012. Read and write PDF files; watermarking, copying images from one PDF to another. Includes sample code. Python 2.5--2.7. MIT License.[repo](https://code.google.com/p/pdfrw/)

 ``slate``
 : Active development. Simplifies extracting text from PDF files. Wrapper around ``PDFMiner``. Includes documentation on GitHub and PyPI. Python 2.6. GPL License.  [repo](https://github.com/timClicks/slate)

 ``PDFQuery`` 
 : Active development. PDF scraping with Jquery or XPath syntax. Requires ``PDFMiner``, ``pyquery`` and ``lxml`` libraries. Includes sample code, documentation. Seems to be Python 2.x. MIT License. [repo](https://github.com/jcushman/pdfquery)

 ``PDFMiner``
 : Active development. Extracting text, images, object coordinates, metadata from PDF files. Pure Python. Includes sample code and command line interface; Google group and documentation. Python 2.x only. MIT License. [repo](https://github.com/euske/pdfminer/)

 ``PyPDF2``
 : Active development. Split, merge, crop, etc. of PDF files. Pure Python. Includes sample code and command line interface, documentation. Python 2 and 3. BSD License. [repo](https://github.com/mstamy2/PyPDF2)

## Related Tools

There are several non-Python tools available for manipulating PDF files in one way or another. If none of the Python solutions fit your situation, see the section [Other Tools][] for more information.

# Extracting: PDFMiner

The **PDFMiner** library excels at extracting data and coordinates from a PDF. In most cases, you can use the included command-line scripts to extract text (``pdf2txt.py``) or find objects and their coordinates (``dumppdf.py``). If you're dealing with a particularly nasty PDF and you need to get more detailed , you can import the package and use it as library. Install with ``pip``.

## PDFMiner: the ``pdf2txt.py`` command 

The package includes the ``pdf2txt.py`` command-line command, which you can use to extract text and images. The command supports many options and is very flexible. Some popular options are shown below. See the usage information for complete details.

```bash
pdf2txt.py [options] filename.pdf
Options:
    -o output file name
    -p comma-separated list of page numbers to extract
    -t output format (text/html/xml/tag[for Tagged PDFs])
    -O dirname (triggers extraction of images from PDF into directory)
    -P password
```

That's right, you can even use the command to convert PDF to HTML or XML!
For example, say you want the HTML version of the first and third pages of your PDF, including images.

```bash
pdf2txt.py -O myoutput -o myoutput/myfile.html -t html -p 1,3 myfile.pdf
```

Note that the package cannot recognize text drawn as images because that would require optical character recognition. It does extract the corresponding locations, font names, font sizes, etc., for each bit of text. Often this is good enough--you can extract the text and use typical Python patterns for text processing to get the text or data into a usable form.

## PDFMiner: the ``dumppdf.py`` command 

The package also includes the ``dumppdf.py`` command-line command, which you can use to find the objects and their coordinates inside a PDF file.

```bash
dumppdf.py [options] filename.pdf
Options:
    -a dump all objects
    -p comma-separated list of page numbers to extract
    -i object id
    -E dirname (extract embedded files from the PDF into directory)
    -T dump the table of contents (bookmark outlines)
    -p password
```

This is very useful when you have a problematic PDF and you want to know the exact object IDs that it contains. For example, you might need to know the object ID corresponding to an image in the PDF so you can extract only that image. Here is an example:

    :::bash
    dumppdf.py -a filename.pdf | more
    # search for the string 'Image' and find the ID; '33' for example.
    dumppdf.py -i 33 -r filename.pdf > myimage.jpg

You run the command with ``-a`` option first so you can review the objects and their IDs, find the object you want (images have a ``SubType`` of ``Image``), then re-run the command with the ``-i`` option to extract only that object.

## PDFMiner: Use as a Library

If you are writing Python code and you don't want to shell out to the command line with ``os.system`` or ``subprocess``, you use the package as a library. For example, to extract text from a PDF:

    :::python
    from cStringIO import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage

    def convert(fname, pages=None):
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)

        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)
        
        infile = file(fname, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close
        return text 

The above function ``convert`` is called with the name of the PDF file to convert, and optionally, a list of pages to convert. By default, all pages are converted to text. The function returns a string containing the text. To retrieve the text extracted from ``myfile.pdf`` on pages 6 and 8, call the function as follows (internal page numbering starts at zero).

    :::python
    convert('myfile.pdf', pages=[5,7])

PDFMiner provides functions to access the document's table of contents. We know these as bookmarks or "Outlines". If your PDF file contains bookmarks, you can retrieve them easily:

    :::!python
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument

    def get_toc(pdf_path):
        infile = open(pdf_path, 'rb')
        parser = PDFParser(infile)
        document = PDFDocument(parser)

        toc = list()
        for (level,title,dest,a,structelem) in document.get_outlines():
            toc.append((level, title))

        return toc

**Note:** If you change line 11 to read ``toc.append((level, title, a.resolve()))``, the resulting list will contain the actual internal destinations for bookmarks. A typical entry looks like this:

    (1, u'Other Commands', {'S': /GoTo, 'D': 'section.8'})
where the section "Other Commands" is a first level section and it is the 8th section in the PDF. You can use this information to construct a URL that opens the PDF at that destination. In this example, the URL would look like this:

    <a href="path/to/myfile.pdf#section.8">link text</a>

When you follow the URL, the browser opens the PDF at the location of the section titled "Other Commands".

How do you know how to piece everything together, what with the manager, the parser, the document, etc.? The documentation for the package is helpful, but in addition, the source code for the command-line commands is straightforward and shows how you can configure your own code. The source for the scripts reside in a subdirectory called ``tools``. In fact, the entire source code is readable and provides good, Pythonic, examples.

# Manipulating: PyPDF2

You can manipulate PDF files in a variety of ways using the pure-Python PyPDF2 toolkit. The original **pyPDF** library is officially no longer being developed but the **pyPDF2** library has taken up the project under the new name and continues to develop and enhance the library. The development team is dedicated to keeping the project backward compatible. Install with ``pip``.

Want to merge two PDFs? Merge can mean a couple of things--you can merge, in the sense of inserting the contents of one PDF *after* the content of another, or you can merge by applying one PDF page *on top of* another. 

## PyPDF2: Merge (layer)
For an example of the latter case, if you have a one-page PDF containing a watermark, you can layer it onto each page of another PDF.
Say you've created a PDF with transparent watermark text (using Photoshop, Gimp, or LaTeX). If this PDF is named ``wmark.pdf``, the following python code will stamp each page of the target PDF with the watermark.

    :::python
    from PyPDF2 import PdfFileWriter, PdfFileReader
    output = PdfFileWriter()
    
    ipdf = PdfFileReader(open('sample2e.pdf', 'rb'))
    wpdf = PdfFileReader(open('wmark.pdf', 'rb'))
    watermark = wpdf.getPage(0)

    for i in xrange(ipdf.getNumPages()):
        page = ipdf.getPage(i)
        page.mergePage(watermark)
        output.addPage(page)

    with open('newfile.pdf', 'wb') as f:
       output.write(f)

If your watermark PDF is not transparent it will hide the underlying text. In that case, make sure the content of the watermark displays on the header or margin so that when it is merged, no text is masked. For example, you can use this technique to stamp a logo or letterhead on each page of the target PDF.

## pyPDF2: Merge (append)

This snippet takes all the PDFs in a subdirectory named ``mypdfs`` and puts them in name-sorted order into a new PDF called ``output.pdf``

    :::python
    from PyPDF2 import PdfFileMerger, PdfFileReader
    import os

    merger = PdfFileMerger()
    files = [x for x in os.listdir('mypdfs') if x.endswith('.pdf')]
    for fname in sorted(files):
        merger.append(PdfFileReader(open(fname, 'rb')))

    merger.write("output.pdf")


## Delete

If you want to delete pages, just skip over them as you write your new PDF. For example, if you want to get rid of blank pages in ``source.pdf``:

    :::Python
    from PyPDF2 import PdfFileWriter, PdfFileReader
    infile = PdfFileReader('source.pdf', 'rb')
    output = PdfFileWriter()

    for i in xrange(infile.getNumPages()):
        p = infile.getPage(i)
        if p.getContents(): # getContents is None if  page is blank
            output.add(p)

    with open('newfile.pdf', 'wb') as f:
       output.write(f)

Since blank pages are not added to the output file, the result is that the new output file is a copy of the source but with no blank pages.

## Split
You want to split one PDF into separate one-page PDFs. Create a new file for each page and write that file as you iterate through the source PDF.

    :::python
    from PyPDF2 import PdfFileWriter, PdfFileReader 
    infile = PdfFileReader(open('source.pdf', 'rb'))

    for i in xrange(infile.getNumPages()):
        p = infile.getPage(i)
        outfile = PdfFileWriter()
        outfile.addPage(p)
        with open('page-%02d.pdf' % i, 'wb') as f:
            outfile.write(f)
     

## Slices

You can even operate on slices of a source PDF, where each item in the slice is a page.

Say you have two PDFs resulting from scanning odd and even pages of a source document. You can merge them together, interleaving the pages as follows:

    #!python
    from PyPDF2 import PdfFileWriter, PdfFileReader 
    even = PdfFileReader(open('even.pdf', 'rb'))
    odd = PdfFileReader(open('odd.pdf', 'rb'))
    all = PdfFileWriter()
    all.addBlankPage()

    for x,y in zip(odd.pages, even.pages):
        all.addPage(x)
        all.addPage(y)

    while all.getNumPages() % 2:
        all.addBlankPage()

    with open('all.pdf', 'wb') as f:
        all.write(f)

The first ``addBlankPage`` (line 5) insures that the output PDF begins with a blank page so that the first content page is on the right-hand side. This is useful when your PDFs are laid out for a two-page (book-like) spread.

The last ``addBlankPage`` sequence (lines 11-12) insures there is an even number of pages in the final PDF. Like the first ``addBlankPage``, this is an optional step of course, but could be important depending on how the final PDF will be used (for example, a print shop will appreciate that your PDFs do not end on an odd page).

## PyPDF2: Metadata

You can set your own metadata in a PDF:

    :::python
    from PyPDF2 import PdfFileMerger, PdfFileReader
    
    def add_metadata(name, **kwargs):
        merger = PdfFileMerger()
        with open('%s.pdf' % name, 'rb') as f0:
            merger.append(f0)
        
        merger.addMetadata(kwargs)
        
        with open('%s_update.pdf' % name, 'wb') as f1:
            merger.write(f1)

    metadata = {u'/hey':u'there', u'/la':'deedah'}
    add_metadata('myfile', **metadata)

The function ``add_metadata`` opens the source PDF file and appends it to a new PdfFileMerger instance, resulting in a copy of the PDF. Then it adds a special dictionary of key-value pairs into the new PDF metadata dictionary and writes the new PDF out to disk.  The dictionary keys and values are unicode strings; also, the ``key`` string begins with a forward slash.

Why would you want to add metadata to a PDF? I'm sure there are a lot of reasons, but when I have needed this ability, it was to make sure I only processed each PDF one time. So when I processed a PDF I checked for my metadata key. If it was present I skipped it and went to the next PDF. Otherwise I processed the PDF and added the metadata key to show that it had been processed. 


## PyPDF2: Other Operations

With PyPDF2, you can crop pages, add Javascript code, encrypt, rotate, scale, and transform pages. The documentation covers most uses and the sample code that comes with it shows you how to do each operation.

The distribution contains a subdirectory called ``Sample_Code`` with several scripts that show you how.

# Other Tools

If you deal with PDFs, you need a good toolbox to turn to. In addition to the tools Python provides for manipulating PDFs, the following libraries, packages, and programs enable you to do other types of tasks.

``reportlab``
: Python package. Create PDF documents as well as vector and bitmap images. [info](http://www.reportlab.com/opensource/)

``pdftk``
: GUI and command line. Merge, split PDF files, and more. [info](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)

``fdfgen``
: Python package. Generates an ``FDF`` file containing form data that can be used with ``pdftk`` to populate a PDF form. [repo](https://github.com/ccnmtl/fdfgen/)

``qpdf``
: C++ library and program suite. Transforms PDF files. Useful for linearizing/optimizing uncompressing, and encryption. [repo](http://qpdf.sourceforge.net/)

``ghostscript``
: Interpreter for Postscript and PDF. [info](http://www.ghostscript.com/). [Command-line info](http://www.ghostscript.com/doc/9.15/Use.htm)

``XPDF``
: Open source project. Contains several useful tools such as ``pdffonts`` and ``pdfinfo``. [repo](http://www.foolabs.com/xpdf/)
    + ``pdffonts`` lists fonts used in a PDF file including information on font type, whether the font is embedded, etc. Part of the open-source ``Xpdf`` project. Licensed under GPL v2.
    
    ```bash
    > pdffonts filename.pdf
    name                                 type              emb sub uni object ID
    ------------------------------- ----------------- --- --- --- ---------
    LFIGJB+ArialMT                  Type 1C           yes yes no      39  0
    LFIGLB+Arial-BoldMT             Type 1C           yes yes no      41  0
    ```

    + ``pdfinfo`` extracts contents of ``Info`` dictionary in a PDF file. Another part of the ``Xpdf`` project.
    
    ```bash
    > pdfinfo filename.pdf
    Title:          HILs.pdf
    Subject:
    Keywords:
    Author:         
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

There is some overlap in capability between ``PDFMiner`` and ``PyPDF2`` and that means you have options in which one you want to use and learn. Both libraries are in active development and the developers are dedicated to providing good code. Browsing the source is good way to learn about both Python and PDF internals.

There are some nasty PDFs out there. But there are several tools you can use to get what you need from them and Python enables you to get inside and scrape, split, merge, delete, and crop just about whatever you find.



