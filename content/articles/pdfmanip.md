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

merge
split, reorder, delete
encrypt, decrypt
rotate 
crop
add header/footer
watermark
extract images
forms: delete fields, flatten(merge data), list fields
add metadata
create image from page

https://github.com/pboehm/pdfcrop

http://stackoverflow.com/questions/23631755/python-pypdf2-merge-rotated-pages

http://stackoverflow.com/questions/2925484/place-image-over-pdf

http://stackoverflow.com/questions/6041244/how-to-merge-two-landscape-pdf-pages-using-pypdf/17392824#17392824

http://www.blog.pythonlibrary.org/2012/07/11/pypdf2-the-new-fork-of-pypdf/


https://blog.idrsolutions.com/2013/01/understanding-the-pdf-file-format-overview/#pdf-format

http://phaseit.net/claird/comp.text.pdf/PDF_converters.html

http://www.itworld.com/article/2756098/enterprise-software/friends-don-t-let-friends-extract-pdf-content.html

http://www.propublica.org/nerds/item/heart-of-nerd-darkness-why-dollars-for-docs-was-so-difficult

https://pypi.python.org/pypi/pdftable/

## Extracting Text {. article-title}

pdfminer is your uncle. use the cli or if you need more customized approach, do it yourself with the library

## Extract JPegs

http://nedbatchelder.com/blog/200712/extracting_jpgs_from_pdfs.html

## Populate Form (fdfgen)

get the name of the form fields with pdfminer (dump?) and merge the entries with fdfgen

https://github.com/ccnmtl/fdfgen

http://stackoverflow.com/questions/3984003/how-to-extract-pdf-fields-from-a-filled-out-form-in-python?rq=1

http://stackoverflow.com/questions/10476265/batch-fill-pdf-forms-from-python-or-bash?lq=1

## 4-up
https://code.google.com/p/pdfrw/source/browse/trunk/examples/4up.py


## Merging and Splitting

pypdf, make a new pdf or multiple new pdfs 

## PDF Document Information

get is easy, add info is a little more complex.

http://stackoverflow.com/questions/14209214/reading-the-pdf-properties-metadata-in-python?rq=1

## Add text to PDF

http://stackoverflow.com/questions/1180115/add-text-to-existing-pdf-using-python

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



    def write_page(filename, obj, pagenum, crop=False):
        '''Write a PDF object to disk.

            Args:
              :filename: the file to create
              :obj: the PDF object in memory
              :pagenum: the page in the PDF to write
              :crop: flag indicating whether the function is
                     called from the cropping process

            Used for splitting pdfs by page and writing cropped objects
            to disk. If called from the cropping process, add metadata to
            the PDF so we don't try to split or crop it in some subsequent run.

            Returns: None

        '''
        p = pyPdf.PdfFileWriter()
        if crop:
            infoDict = p._info.getObject()
            infoDict.update({pyPdf.generic.NameObject('/Cropped'):
                             pyPdf.generic.createStringObject(u'True')})

        page = obj.getPage(pagenum)
        p.addPage(page)
        p.write(open(filename, 'wb'))





more stuff

    def get_date(info):
        d = info.get('/CreationDate')
        if d:
            datestring = d[2:-7]
            ts = strptime(datestring, "%Y%m%d%H%M%S")
            dt = datetime.datetime.fromtimestamp(mktime(ts))
            return dt
        else:
            return datetime.date(1900, 1, 1).strftime('%Y-%m-%d')

more stuff

            info = book_pdf.documentInfo
            title = info.title
            self.book_title = title
            date = get_date(info)
            self.results = {
                'name': self.name,
                'title': title,
                'date': date,
                'chapters': list(),
                'filename': os.path.basename(book),
                'filesize': os.path.getsize(book),
                'errors': errors,
                'error_text': error_text,
                'urls': urls,
                'badurls': badurls,
                'badlinks': badlinks,


more stuff

    def read(self, q, name):
        '''Read a PDF file, find the number of pages it contains and whether
           it contains metadata indicating it has been cropped in a previous
           run. Save the information and place it in a queue that is used after
           all processes have completed.
        '''
        print '.',
        obj = pyPdf.PdfFileReader(open(os.path.join(self.source_dir, name), 'rb'))
        docinfo = obj.getDocumentInfo()
        cropped = docinfo and docinfo.has_key('/Cropped')
        pages = obj.getNumPages()
        q.put({'name': name, 'cropped': cropped, 'pages':pages})
        obj.stream.close()

    def split(self):
        '''Create a data structure, `stem_info`, which contains an ordered list
           of the files that match to each file-stem.

           Process each list of files by file-stem. If no pdf files in the list
           have multiple pages, this method does nothing.

           If multiple pages do exist for at least one file in the list, split the
           files from that point on so that each pdf file contains one page.
           Then write the pages to files, renumbering so the information stream
           keeps its original order.

           Rename the files so the original files are overwritten after all processes
           are complete.

        '''
        stem_info = dict()
        for stem in get_stems(self.pdffiles):
            'Create the data structure to match a list of files according to its stem'
            stem_matches = ['%s.pdf' % stem]
            stem_matches.extend([x for x in self.pdffiles if re.match(r'%s\d+\.pdf' % stem, x)])

            stem_info[stem] = [{'name': x['name'], 'pages': x['pages']}
                               for x in self.file_info if x['name'] in stem_matches]

        for stem in stem_info:
            'if no file in the list contains multiple pages, do nothing'
            if sum(x['pages'] for x in stem_info[stem]) == len(stem_info[stem]):
                continue

            start_splitting = False
            filedigit = 0
            files_info = sorted(stem_info[stem], key=get_filedigit)

            for pdfdict in files_info:
                name = pdfdict['name']
                pages = pdfdict['pages']

                if not start_splitting and pages > 1:
                    start_splitting = True
                if not start_splitting:
                    print 'skipping %s' % name
                    filedigit += 1
                    continue

                print '%30s (%d pages)' % (name, pages)
                '''Write a new one-page file for each page in the stream
                   naming the files consecutively.
                '''
                obj = pyPdf.PdfFileReader(open(os.path.join(self.source_dir, name), 'rb'))
                for pagenum in range(0, pages):
                    if filedigit == 0:
                        fname = os.path.join(self.source_dir, '%s_SPLIT.pdf' % stem)
                        rname = '%s.pdf' % stem
                    else:
                        fname = os.path.join(self.source_dir, '%s%d_SPLIT.pdf' % (stem, filedigit))
                        rname = '%s%d.pdf' % (stem, filedigit)
                    write_page(fname, obj, pagenum)

                    if self.cropped.count(rname):
                        self.cropped.remove(rname)
                    filedigit += 1

                obj.stream.close()

        rename_files(self.source_dir, '_SPLIT.pdf')


    def crop(self):
        '''For each file in the directory, start a subprocess (within multiprocess)
           to crop the file. Rename the files to overwrite the original when all
           processes are complete.
        '''
        processes = dict()
        filenames = [x for x in os.listdir(self.source_dir)
                     if x not in self.cropped and x.endswith('.pdf')]
        if filenames:
            print 'Cropping %d files' % len(filenames)

        for name in filenames:
            processes[name] = multiprocessing.Process(target=self.crop_process, args=(name,))
            processes[name].start()

        for name in processes:
            processes[name].join()
        print
        rename_files(self.source_dir, '_CROP.pdf')

    def crop_process(self, name):
        '''Get the bounding box for each file and set the new dimensions
           on the page object. Write the page object to disk.
        '''
        fullname = os.path.join(self.source_dir, name)
        obj = pyPdf.PdfFileReader(open(fullname, 'rb'))

        print '+',
        bounds = get_bbox(self.ghostscript, fullname)
        if bounds and int(sum(bounds)):
            lx, ly, ux, uy = bounds

            page = obj.getPage(0)
            page.mediaBox.lowerLeft = lx, ly
            page.mediaBox.lowerRight = ux, ly
            page.mediaBox.upperLeft = lx, uy
            page.mediaBox.upperRight = ux, uy

            new_name = os.path.join(self.source_dir, '%s_CROP.pdf' % os.path.splitext(name)[0])
            write_page(new_name, obj, 0, crop=True)