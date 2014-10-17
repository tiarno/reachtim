Title: Manipulate PDFs with Python (pyPdf and PDFMiner)
Category: Python
Status: Draft
Date: 2014-Oct-30
Tags: how-to, pdf
Summary: How to manipulate PDFs using Python

When working with PDFs using Python, there are two popular libraries you can use. **PDFMiner** works well for extracting information (like converting to text); **pyPDF** works well for splitting, cropping, and merging. It is also useful for getting information about the objects in the PDF.

This article shows how you can use these libraries to manipulate your PDF files. You can install both packages using `pip`, but note that `pyPDF` is no longer developed; development continues under new management and a new name `pyPDF2` (so that's the one to install if you don't have `pyPDF`).

**Table of Contents**

[TOC]

## Extracting Text {. article-title}

## Merging and Splitting

## PDF Document Information



# PDFMiner
PDFMiner is a tool for extracting information from PDF documents. Unlike other PDF-related tools, it focuses entirely on getting and analyzing text data. PDFMiner allows one to obtain the exact location of text in a page, as well as other information such as fonts or lines. It includes a PDF converter that can transform PDF files into other text formats (such as HTML). It has an extensible PDF parser that can be used for other purposes than text analysis.

also check out slate:
https://pypi.python.org/pypi/slate
can find boxes of text and output text + box coords
includes pdf2txt.py
extracts text contents from a PDF file. It extracts all the text that are to be rendered programmatically, i.e. text represented as ASCII or Unicode strings. It cannot recognize text drawn as images that would require optical character recognition. It also extracts the corresponding locations, font names, font sizes, writing direction (horizontal or vertical) for each text portion.

 and 

dumppdf.py dumps the internal contents of a PDF file in pseudo-XML format. This program is primarily for debugging purposes, but it's also possible to extract some meaningful contents (such as images).

http://denis.papathanasiou.org/2010/08/04/extracting-text-images-from-pdf-files/
http://stackoverflow.com/questions/9343781/return-text-string-from-physical-coordinates-in-a-pdf-with-python/9344123#9344123

PDFQuery
a light wrapper around pdfminer, lxml and pyquery. It's designed to reliably extract data from sets of PDFs with as little code as possible.
http://stackoverflow.com/questions/16988102/error-trying-to-run-pdfquery-example

PyPDF
A Pure-Python library built as a PDF toolkit. It is capable of:

extracting document information (title, author, ...),
splitting documents page by page,
merging documents page by page,
cropping pages,
merging multiple pages into a single page,
encrypting and decrypting PDF files.


PyPDF2
PyPDF2 is a pure-python PDF library capable of splitting, merging together, cropping, and transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF files. It can retrieve text and metadata from PDFs as well as merge entire files together.

PyPDF2 is largely about metadata: PyPDF2 manages metadata, merges PDF instances, and so on.

ReportLab
This is a software library that lets you directly create documents in Adobe's Portable Document Format
(PDF) using the Python programming language. It also creates charts and data graphics in various bitmap and
vector formats as well as PDF.


As expected, pyPDF (and maybe its fork pyPDF2) is better for PDF manipulation, and PDFMiner better for text conversion. There are also other PDF-to-text conversion or extraction tools, such as PDFBox (Java) that I might try in the future.
-----------

read your PDF using PdfFileReader(), we'll call this input

create a new pdf containing your text to add using ReportLab, save this as a string object

read the string object using PdfFileReader(), we'll call this text

create a new PDF object using PdfFileWriter(), we'll call this output

iterate through input and apply .mergePage(text.getPage(0)) for each page you want the text added to, then use output.addPage() to add the modified pages to a new document


burst
merge
extract/change metadata
add text to all blank pages
remove all blank pages
