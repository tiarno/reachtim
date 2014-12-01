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

This article describes how you can use the **StatRep** package with SAS University Edition and SAS Studio. The main thing to keep in mind is that, with a web interface, there is no concept of a "current directory" so you must let SAS know where your files are located.

The **StatRep system** uses SAS and the LaTeX typesetting system to create documents with reproducible results. With **StatRep**, all of your data, code, and output is in a single source, your LaTeX file.  The system consists of a LaTeX package, a suite of SAS macros and the *User's Guide*S. You can find more details here:

- [SAS Global Forum (2012) paper](http://support.sas.com/resources/papers/proceedings12/324-2012.pdf)
- [Article](http://reachtim.com/articles/statrep-latex.html)
- [Download ZIP](http://support.sas.com/rnd/app/papers/statrep.html)

[SAS University Edition](http://support.sas.com/software/products/university-edition/index.html) is free and includes the SAS products Base SAS, SAS/STAT, SAS/IML, SAS/ACCESS Interface to PC Files, and SAS Studio.
[SAS Studio](http://support.sas.com/software/products/sasstudio/) is a developmental web application for SAS that you access through your web browser.

In order to use **StatRep**, SAS needs to know the following locations:
1. the directory that contains your LaTeX file.
2. the full path to the file `statrep_macros.sas`.
3. if you prefer LaTeX output (instead of Listing output), the **StatRep** ODS tagset. See the last section of this article for details on how to create and use this tagset.

### Shared Folder {: .article-title}



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
    \def\SRrootdir{/folders/myshortcuts/mydocs}
    \def\SRmacropath{/folders/myshortcuts/mydocs/statrep_macros.sas}
    \begin{document}

That ``\SRrootdir`` variable is necessary so that when SAS runs the generated program it can write the outputs where LaTeX expects them to be.


### Caveats {: .article-title}

1. x commands don't work
2. sas/graph isn't available
3. three directories are created each time you execute the SAS program (lst, pgn, tex)


### Summary {: .article-title}

It's pretty damn cool. Leave a comment!

make new dir, put tex file
add defs to tex file (or statrep.cfg):
SRrootdir (/folders/myshortcuts/dirname, SRmacropath, same pattern or not).
in terminal, pdflatex texfile

note difference in /folders/myfolders/dirname and /folders/myshortcuts/dirname

make new shared folder of new dir, select automount on the VM
start sas and sas studio
open statrep_tagsets.sas in the shared folder, run
open texfile_SR.sas in the shared folder, run.

back to terminal, pdflatex texfile twice, open pdf.




### Save the StatRep Tagset Permanently {: .article-title}

If you prefer, instead of the ODS Listing output, you can generate LaTeX output with the **StatRep** ODS tagset. You generate the tagset when you run the included program `statrep_tagset.sas`. You can generate the tagset each time you need to generate output and it is available in the WORK library.

If you'd rather not have to run the file `statrep_tagset.sas` every time you need to generate your output, you can save the tagset in a permanent location.

Add the following code block at the beginning of the file `statrep_tagset.sas`. When you run the program, the generated ODS tagset is saved in the directory `mytemplates` and you do not need to run it again.

```perl
%sysfunc(
  ifc(%sysfunc(libref(mytempl)),
    libname mytempl '/folders/myfolders/mytemplates',)
);
ods path 
  mytempl.template(update)
  sasuser.template(read)
  sashelp.tmplmst(read);
```

Once you have done that, youS tell SAS where to look for your templates whenever you want to refer to the tagset. To do so, add *the same code block* to the beginning of the automatically-generated SAS program that creates the outputs. 

