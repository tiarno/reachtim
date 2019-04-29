Title: StatRep and SAS Studio/SAS University Edition
Category: LaTeX
Slug: statrep-university
Tags: how-to, statrep
Status: Draft
Date: 01-30-2015
Summary: How to use StatRep with SAS Studio or SAS University Edition

**Table of Contents**

[TOC]

### Overview {: .article-title}

This article describes how you can use the **StatRep** package with SAS Studio or SAS University Edition. If you want general information on how to use **StatRep**, see the links listed below.

The **StatRep system** uses SAS and the LaTeX typesetting system to create documents with reproducible results. With **StatRep**, all of your data, code, and output is in a single source, your LaTeX file.  The system consists of a LaTeX package, a suite of SAS macros and the *User's Guide*. You can find more details here:
- [SAS Global Forum (2012) paper](http://support.sas.com/resources/papers/proceedings12/324-2012.pdf)
- [Article](http://reachtim.com/articles/statrep-latex.html)
- [Download ZIP](http://support.sas.com/rnd/app/papers/statrep.html)
{: .callout}

Additionally, information on the SAS Studio web-based interface and SAS University Edition is available:

[SAS University Edition](http://support.sas.com/software/products/university-edition/index.html)
:is free and includes the SAS products Base SAS, SAS/STAT, SAS/IML, SAS/ACCESS Interface to PC Files, and SAS Studio.
[SAS Studio](http://support.sas.com/software/products/sasstudio/)
:is a developmental web application for SAS that you access through your web browser.

With a web interface, there is no concept of a "current directory," so you must let SAS know where your files are located. In order to use **StatRep**, SAS needs to know the following locations:

1. the directory that contains your LaTeX file.
2. the full path to the file `statrep_macros.sas`.
3. if you prefer LaTeX output (instead of Listing output), you can use the **StatRep** ODS tagset. SAS needs to know where to locate that tagset. See the last section of this article for details on how to create and use this tagset.

### A Place to Work: The Shared Folder {: .article-title}

First of all, you need a place to work and SAS needs to know where it is. You either have a directory you already use or you can create one to house your LaTeX file. For example, say you have a directory called `mydocs` that contains your LaTeX file. You create a shared folder in the virtual machine as shown in the following screenshot:

![center](images/vm1.png)

When you select `Shared Folders` and click to add a new path, enter the information (path and name) as shown in the following screenshot:

![center](images/vm2.png)

The `Folder Path` is the absolute path to the directory and the folder name is the last part of that path. The name is a short-hand name that is used later in your code. Make sure to select `Auto-mount` if you want to use the folder in later SAS sessions (as you probably will). The result of entering the information is shown in the following screenshot. 

![center](images/vm3.png)

When you start SAS Studio, the `Folder` panel shows your new shared folder as a *Folder Shortcut*. SAS will know this folder by the full name `/folders/myshortcuts/mydocs`, which means you can use that name to assign filerefs and libnames as you normally would in any SAS program. Notice the `Folder` panel in the following screenshot. You can disregard most of the code in the program editor window, but do notice the first line that references the new shared folder.

![center](images/sasuniv1.png)

The LIBNAME statement in the code window assigns the `mytempl` libref to your shared folder. 

### The Bridge Between LaTeX and SAS {: .article-title}

Now you have your working directory and SAS knows that there is such a location. The final bit is to define a bridge between your LaTeX document and SAS. You connect the two by defining a LaTeX tag called `\SRrootdir`, which contains the path to your shared folder as displayed in the following LaTeX code:

    :::latex
    \documentclass{article}
    \usepackage[margin=1in]{geometry}
    \usepackage[color]{statrep}
    \def\SRrootdir{/folders/myshortcuts/mydocs}
    \def\SRmacropath{/folders/myshortcuts/mydocs/statrep_macros.sas}
    \begin{document}

This document preamble performs the following:

1. Specifies that the document use the `article` class.
2. Loads the `geometry` package and specifies 1 inch margins on all sides.
3. Loads the `statrep` package and specifies that outputs can include color.
4. Defines the `\SRrootdir` path (the path to the working directory) as the shared folder you created in the previous steps.
5. Defines the `\SRmacropath` that contains the full path and file name of the `statrep_macros.sas` file that is part of the **StatRep** package. This example shows that it is in the same directory as the LaTeX file, but you can put the macros anywhere you like, as long as SAS can find the file (that is, as long as the macros are in a shared folder)

With this preamble, you can start writing your content; when **StatRep** automatically generates the SAS program to create your output, the paths you have defined here are used so SAS can find the macros it needs and so it can write the requested outputs to your working directory.

From this point on, you use **StatRep** just as you would normally. Complete details are given in the *User's Guide*, which is bundled with the download.

Briefly, you perform four steps to create your final PDF that contains your data, code, output, and analysis:

1. Write your LaTeX document using custom markup from the **StatRep** package.
2. Compile the document with pdfLaTeX; this step generates a SAS program to capture the output needed in your document.
3. Run that generated SAS program to produce the output.
4. Recompile the document with pdfLaTeX; now your code and output appear in the final PDF document.

### Caveats {: .article-title}

Some things are different when you have a web-based interface and some SAS products are not available in the free (for non-commercial use) SAS University Edition.

- Shell commands (`x` commands) are not available.
- Base SAS, SAS/STAT, SAS/IML and SAS/ACCESS products are available; other SAS products are not loaded in the SAS University Edition.
- Three subdirectories are created and wiped clean each time you execute the SAS program (`lst`, `png`, `tex`). Make sure you never put your own files in these subdirectories because they are automatically removed when you execute your SAS program.

### Summary {: .article-title}

The **StatRep** system enables you to create dynamic documents with SAS and LaTeX. With the latest release, you can use it with SAS Studio and SAS University Edition, but there are a few extra steps you must take to set things up; with a web-based interface, there is no concept of a "current directory".

By defining the working directory as a shared folder and the defining the location of the **StatRep** macros, you can use SAS Studio and SAS University Edition to create reports with reproducible results and share it with others.

Have a question or suggestion? Leave a comment!

### Save the StatRep Tagset Permanently {: .article-title}

If you prefer, instead of the ODS Listing output, you can generate LaTeX output with the **StatRep** ODS tagset. You generate the tagset when you run the included program `statrep_tagset.sas`. You can generate the tagset each time you need to generate output and it is available during the current SAS session.

That is all you need to do, but if you'd rather not have to run the file `statrep_tagset.sas` every time you want to generate your output, you can save the tagset in a permanent location.

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

Once you have done that, you tell SAS where to look for your templates whenever you want to refer to the tagset. To do so, add *the same code block* to the beginning of the automatically-generated SAS program that creates the outputs. 
