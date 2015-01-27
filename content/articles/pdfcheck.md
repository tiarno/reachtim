Title: Test PDF Links with Python
Date: 01-26-2015
Slug: PDF-Testing
Category: Python
Tags: how-to, pdf
Summary: Methods for testing PDFs using Python

**Table of Contents**

[TOC]

# Overview

When you generate PDFs, you need a way to test their integrity--not only must they be valid, but they should behave correctly and display consistently, even on different platforms. This article describes how you can use the PyPDF2 library to test your PDF files for broken links (both internal and external), and how to find fonts that are not embedded in the PDF.

Note that some PDF readers are 'smart' and will create a live hyperlink from a string of text that looks like a URL, even though the text is not coded as a URL in the PDF file. The technique described in this article does not address this issue--it only tests the actual URLs present in the PDF file.

Code from this article is available as a [gist](https://gist.github.com/tiarno/dea01f70a54cac52f6a6#file-pdf-testing-md) on GitHub. Get a copy and play along.


# Testing Internal and External Links

To test the links, we'll create a function to check the urls found inside the PDF file. This function uses the `requests` library, which you can install with `pip`. 

There may be some `ftp` links, which are not directly supported by the `requests` library. You can either use the `urllib` package as in the following code, or you can use the `requests-ftp` package, available on `pypi`.

    :::python
    from PyPDF2 import PdfFileReader
    from pprint import pprint
    import requests
    import sys
    import urllib

The `check_ftp` function checks a given url for a response. If it fails, or if the response is empty, it returns `False`, along with the reason; otherwise it returns `True`.

    def check_ftp(url):
        try:
            response = urllib.urlopen(url)
        except IOError as e:
            result, reason = False, e
        else:
            if response.read():
                result, reason = True, 'okay'
            else:
                result, reason = False, 'Empty Page'
        return result, reason

The `check_url` function is also simple: If the url starts with `ftp`, it delegates to the `check_ftp` function. Otherwise, it attempts to `get` the url with some timeout value using typical header values. The the function returns the response along with the reason it succeeded or failed.

    def check_url(url, auth=None):
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
        if url.startswith('ftp://'):
            result, reason = check_ftp(url)
        else:
            try:
                response = requests.get(url, timeout=6, auth=auth, headers=headers)
            except (requests.ConnectionError,
                    requests.HTTPError,
                    requests.Timeout) as e:
                result, reason = False, e
            else:
                if response.text:
                    result, reason = response.status_code, response.reason
                else:
                    result, reason = False, 'Empty Page'

        return result, reason

Now that we have this utility, we can check the PDF file. We will create four lists:

- **links** The internal PDF links in the file; for example, a reference to a section or figure.

- **badlinks** Of the internal links in the file, these are links that target a missing destination (broken link).

- **urls** The links from the PDF to an external location; for example, a hyperlink to a web site.

- **badurls** Of the external links in the file, these are the urls that target a missing destination (broken url)

Now for the PyPDF2 goodies. The following `check_pdf` function loops over the pages in the PDF file object. For each page, it walks through the `Annots` dictionary. If that dictionary has an action (`\A`) with a key of `\D` (destination?), that is an internal link, so update the `links` list with the destination.

If the dictionary has an action with a key of `\URI`, it is an external link. Check the external links with the `check_url` function and update the `urls` and `bad_urls` lists.

After checking each page, get a list of all the anchors in the PDF with the `getNamedDestinations` attribute; compare that list of all known anchors to the list of internal links we just created. If there is a link with no matching anchor, that link belongs in the `badlinks` list.

    :::python
    def check_pdf(pdf):
        links = list()
        urls = list()
        badurls = list()

        for page in pdf.pages:
            obj = page.getObject()
            for annot in [x.getObject() for x in obj.get('/Annots', [])]:
                dst = annot['/A'].get('/D')
                url = annot['/A'].get('/URI')
                if dst:
                    links.append(dst)
                elif url:
                    urls.append(url)
                    result, reason = check_url(url)
                    if not result:
                        badurls.append({'url':url, 'reason': '%r' % reason})

        anchors = pdf.namedDestinations.keys()
        badlinks = [x for x in links if x not in anchors]
        return links, badlinks, urls, badurls

Finally, make the code into a callable script that takes a single argument, the path to the PDF file. Then print the results of the `check_pdf` function on `stdout`.

    :::python
    if __name__ == '__main__':
        fname = sys.argv[1]
        print 'Checking %s' % fname
        pdf = PdfFileReader(fname)
        links, badlinks, urls, badurls = check_pdf(pdf)
        print 'urls: ', urls
        print
        print 'bad links: ', badlinks
        print
        print 'bad urls: ',badurls

# Test for Embedded Fonts

Test to make sure that the fonts used in the PDF file are embedded. If a font is not embedded, your PDF file may display differently on different machines, even if it is a font that is putatively "standard", like `Times Roman` or `Helvetica`. To insure that your PDF displays as intended on any machine, all fonts must be embedded.

In the following code, the `walk` function is a recursive function that takes a dictionary-like object (`obj`)  and two sets (`fnt` and `emb`). It walks the given dictionary object: for every key in the given dictionary, the function calls itself on the corresponding value (if that value is a nested dictionary).

If the dictionary has a key called `BaseFont`, the value corresponding to that key is the name of a font used in the PDF; add that font name to the `fnt` set of **fonts used**.

If the dictionary has a key called `FontName`, the dictionary is a descriptor for that font, so check for another key in the same font descriptor dictionary that begins with `FontFile` (the key could be `FontFile`, `FontFile2`, or `FontFile3`). If that key exists, the font is embedded; add that font name to the set of **fonts embedded**.

If the two sets are not identical, there are unembedded fonts in the PDF.

    :::python
    fontkeys = set(['/FontFile', '/FontFile2', '/FontFile3'])
    
    def walk(obj, fnt, emb):
        if '/BaseFont' in obj:
            fnt.add(obj['/BaseFont'])

        elif '/FontName' in obj and fontkeys.intersection(set(obj)):
            emb.add(obj['/FontName'])

        for k in obj:
            if hasattr(obj[k], 'keys'):
                walk(obj[k], fnt, emb)

        return fnt, emb

Finally, make the code into a callable script that takes a single argument, the path to the PDF file. 

Start with two empty sets, `fonts` and `embedded`. Open the file with PyPDF2. The library gives us access to the internal structure of the PDF. We loop over each page in the PDF, passing the page's `Resources` dictionary to the `walk` function, described above. Add the corresponding results to the two sets and calculate the unembedded fonts by differencing the sets.

Print the fonts used in the PDF file and if there are unembedded fonts, print their names as well. Of course here you can do anything you want with the information such as save it to test database, print a report, and so on.

    :::python
    if __name__ == '__main__':
        fname = sys.argv[1]
        pdf = PdfFileReader(fname)
        fonts = set()
        embedded = set()
        
        for page in pdf.pages:
            obj = page.getObject()
            f, e = walk(obj['/Resources'], fonts, embedded)
            fonts = fonts.union(f)
            embedded = embedded.union(e)
        
        unembedded = fonts - embedded
        print 'Font List'
        pprint(sorted(list(fonts)))
        if unembedded:
            print '\nUnembedded Fonts'
            pprint(unembedded)

# Using PyPDF2 Methods 

Obviously, the more you can specify about the PDFs you produce, the more you can test. For example, you may know that your PDF should have specific metadata, should be encrypted, contain a certain number of pages, and so on.

You can test for those conditions with the built-in tools that the PDFFileReader in pyPDF2 provides. If you have a PDFFileReader instance, you can use the following properties for testing:

documentInfo
: returns the document metadata such as author, creator, producer, subject, and title.

isEncrypted
: returns boolean value specifiying whether the document is encrypted

numPages
: returns the number of pages in the document


# Summary

If you produce PDF documents, you need to test them. The more you can specify about your PDFs, the more you can test. This article describes how you can test that the links (internal and external) are valid and that the fonts used in the document are embedded.

Get a copy of this code and play:
Code from this article is available as a [gist](https://gist.github.com/tiarno/dea01f70a54cac52f6a6#file-pdf-testing-md) on GitHub.

Do you test other things in your own PDF documents? Leave a comment!