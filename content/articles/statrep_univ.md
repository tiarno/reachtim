Title: StatRep and SAS University Edition
Category: LaTeX
Slug: statrep-university
Tags: how-to, statrep
Status: Draft
Date: 12-23-2014
Summary: How to use StatRep with the SAS University Edition

**Table of Contents**

[TOC]

### Overview {: .article-title}

pointer to general info on StatRep. this is about how to use it with SAS University Edition. Pointer to info on university edition.

### Shared Folder {: .article-title}

create a folder for your doc, share it in the vm, check it in the folder shortcuts panel in sas studio. add a rootdir macro variable.

### StatRep Style and Tagset {: .article-title}

either you have a place to save this stuff or not. If you do, specify a libname in the statrep_tagset.sas file. otherwise, set things up so the tagset code is created in each run.

### Caveats {: .article-title}

hostdel isn't going to work, so be careful you don't overwrite files you care about or mix old outputs with new. sas/graph isn't going to work either.

### Summary {: .article-title}

It's pretty damn cool. Leave a comment!

