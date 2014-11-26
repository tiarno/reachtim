Title: StatRep and SAS University Edition/SAS Studio
Category: LaTeX
Slug: statrep-university
Tags: how-to, statrep
Status: Draft
Date: 12-23-2014
Summary: How to use StatRep with the SAS University Edition or SAS Studio

**Table of Contents**

[TOC]

### Overview {: .article-title}

This article describes how you can use the **StatRep** package with SAS University Edition and SAS Studio. 

The **StatRep system** uses SAS and the LaTeX typesetting system to create documents with reproducible results. It consists of a LaTeX package, a suite of SAS macros and a user guide. You can find more details here:

- [SAS Global Forum (2012) paper](http://support.sas.com/resources/papers/proceedings12/324-2012.pdf)
- [Article](http://reachtim.com/articles/statrep-latex.html)
- [Download ZIP](http://support.sas.com/rnd/app/papers/statrep.html)

[SAS University Edition](http://support.sas.com/software/products/university-edition/index.html) is free and includes the SAS products Base SAS, SAS/STAT, SAS/IML, SAS/ACCESS Interface to PC Files, and SAS Studio.
[SAS Studio](http://support.sas.com/software/products/sasstudio/) is a developmental web application for SAS that you access through your web browser. 

### Shared Folder {: .article-title}

If you are not using SAS University Edition or SAS Studio, you can skip this step.

from SAS doc:
The following LIBNAME statement assigns the ``mydata`` libref to your shared folder. The directory that you associate with the libref must already exist before you can assign it to the libref.

    :::sas
    libname mydata '/folders/myfolders/';

On your computer, create a folder for your document, 'mydocs' for example.
in SAS+VM, create a folder shortcut to that folder. It will look something like this:

![center](images/vm.png)
![center](images/sasvm.png)

You write your document in your ``mydocs`` directory, and you must set the ``\SRrootdir`` variable: it is defined with the absolute path, like this:

    :::latex
    \documentclass{article}
    \usepackage[margin=1in]{geometry}
    \usepackage[color]{statrep}
    \def\SRrootdir{/home/tiarno/tests/mydocs}
    \begin{document}

That ``\SRrootdir`` variable is necessary so that when SAS runs the generated program it can write the outputs where LaTeX expects them to be.


### StatRep Style and Tagset {: .article-title}

either you have a place to save this stuff or not. If you do, specify a libname in the statrep_tagset.sas file. otherwise, set things up so the tagset code is created in each run.

Provide some kind of example here

### Caveats {: .article-title}

1. x commands don't work
2. sas/graph isn't available
3. three directories are created each time you execute the SAS program (lst, pgn, tex)


### Summary {: .article-title}

It's pretty damn cool. Leave a comment!

