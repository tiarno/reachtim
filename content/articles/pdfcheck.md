Title: Test PDFs with Python
Status: Draft
Date: 11-16-2014
Summary: Methods for testing PDFs using Python

**Table of Contents**

[TOC]

# Overview

# Internal and External Links

    :::python
    from PyPDF2 import PdfFileReader
    import requests
    import sys

    def check_url(url, auth=None):
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
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

        anchors = pdf.getNamedDestinations().keys()
        badlinks = [x for x in links if x not in anchors]
        return links, badlinks, urls, badurls



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



# Font Embedding

# Summary

