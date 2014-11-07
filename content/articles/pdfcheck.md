Title: Test PDFs with Python
Status: Draft
Date: 11-16-2014
Summary: Methods for testing PDFs using Python

**Table of Contents**

[TOC]

# Overview

# External Links

    :::python
    from PyPDF2 import PdfFileReader
    import requests

    def get_urls(pdf):
        badurls = list()
        links = list()
        url_checker = URLChecker() # a helper to test the URL (urllib2)
        for pg in range(pdf.getNumPages()):
            page = pdf.getPage(pg)
            obj = page.getObject()

            for a in obj.get('/Annots', []):
                u = a.getObject()
                lnk = u['/A'].get('/D')
                url = u['/A'].get('/URI')
                if lnk:
                    links.append(lnk)
                if url:
                    urls.append(url)
                    result, reason = url_checker.check(url)
                    if not result:
                        badurls.append({'url':url, 'reason': '%r' % reason})

        anchors = pdf.getNamedDestinations().keys()
        badlinks = [x for x in links if x not in anchors]
        return urls, badurls, badlinks


# Internal Links

# Font Embedding

# Summary

