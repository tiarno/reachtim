Title: SAS Generated LaTeX Output with the StatRep Package
Status: Draft
Category: LaTeX
Slug: statrep-latex
Date: 11-16-2014
Tags: how-to
Summary: How to use StatRep with SAS-generated LaTeX output for reproducible research.

**Table of Contents**

[TOC]

# Overview

The **StatRep** package enables you to create dynamic documents using SAS and LaTeX. It is composed of one LaTeX package (``statrep.sty``) and a suite of SAS macros, (``statrep_macros.sas``) that work together. This enables you to write all of your data, code, and discussion in a single source file (your LaTeX document); that file can be shared with others and you can be sure that the output others see is generated from the code you used to create the analysis. No more copying and pasting of code blocks!

It works in four stages:
1. Write your LaTeX document using custom markup from the **StatRep** package.
2. Compile the document with pdfLaTeX; this automatically generates a SAS program to capture the output needed in your document.
3. Run that generated SAS program to produce the output.
4. Recompile the document with pdfLaTeX; now your code and output appear in the final PDF document.

# Configuration

There are several "hooks" in the **StatRep** configuration that you can set in order to make the package work with your preferences. 

These hooks are explained in detail in the *User's Guide*; see the section on customization and the installation instructions. 

While the defaults have been chosen carefully, there are two settings that are important to understand:
* The location of the file ``statrep_macros.sas`` must be set so that the generated SAS program will function correctly. Set the location with the ``\SRmacropath`` variable in your ``statrep.cfg`` file. 
* The default SAS output destination (the ODS destination) for tables is the Listing destination. If you prefer your tabular output to be generated with the LaTeX tagset: 
 - create the ``statrep.tagset`` from the included SAS program, ``statrep_tagset.sas`` 
 - set the default destination ``\SRdefaultdests`` to ``latex``.

# The StatRep Tagset and Style

The *User's Guide* provides complete details on how to create SAS-generated LaTeX output. The main points are that you must create the ``statrep.tagset`` with the included SAS program, ``statrep_tagset.sas``, and you must tell SAS to use the tagset when creating the tabular outputs. You can run the tagset generation code each time you use **StatRep** or you can save the tagset. By default, the tagset is saved to the SASUSER.TEMPLAT item store. Full details on install tagsets are available in this [Usage Note](http://support.sas.com/kb/32/394.html)

If you want to run the tagset generation code each time, you can change the way **StatRep** includes the macros:

    \SRmacroinclude{%
      \@percentchar include "statrep_tagset.sas" /nosource;
      \@percentchar include "\SRmacropath" /nosource;
    }

The generated SAS program will first create the **StatRep** tagset before creating the output for your document. Easy but not that efficient. More efficient would be to create the tagset and save it in your SASUSER item store.


# Examples

In the examples that follow, the following document preamble, data step and proc step are used. 

The text with colored background in the following explanations provides an overview of what **StatRep** and SAS are doing behind the scenes. There is no need to study them unless you want to know how it all works together.

    :::latex
    \documentclass{article}
    \usepackage[margin=1in]{geometry}
    \usepackage{statrep}
    \begin{document}
    
    The SAS datastep and analysis ...
    
    \begin{Datastep}
    data time;
       input time @@;
       datalines;
     43  90  84  87  116   95  86   99   93  92
    121  71  66  98   79  102  60  112  105  98
    ;
    \end{Datastep}

    ... discussion of the analysis ...

    \begin{Sascode}[store=myoutput]
    proc ttest h0=80 plots(showh0) sides=u alpha=0.1;
       var time;
    run;
    \end{Sascode}

    ... discussion of the results ...


The final PDF output from the preceding code looks like this:
![saslatex1](images/saslatex1.png)

The code creates a SAS data set ``time`` and invokes the TTEST procedure. 

The result is that all output created by the TTEST procedure is contained in an ODS document named ``myoutput`` as specified by the option ``store=myoutput``. So far no output is displayed--the output that is displayed is determined not by the analytical code, but the ``\Listing`` and ``\Graphic`` tags that follow. The code block above generates all the output at one time and stores it in the ODS document so it can be used at any point in the document.

In the sections that follow, the ``\Listing`` and ``\Graphic`` tags request the ODS document to replay output objects into external files (on disk). When the final document is recompiled, pdfLaTeX embeds and displays those outputs.

## Capture All Outputs as a Single Stream

In this example, the output tags make no request for specific outputs. The ``\Listing`` tag specifies 
- that output should come from the ODS document ``myoutput`` which matches the ``store=`` option on the ``Sascode`` block.
- the output destination is ``latex`` 
- caption for the output
- filename that contains the output is ``lst/myouta.lst``

    \Listing[store=myoutput, dest=latex, 
             caption={Court Case Duration Analysis}]{myouta}
    text about table

The output from the above code looks like this:
![saslatex2](images/saslatex2.png)

There are two ways you can set the type of output to be captured and displayed.
You can rely on the global setting of the ``\SRdefaultdests`` or you can explicitly specify the type of output with the ``dest=`` option on the ``\Listing`` tag. 

When you download and install the **StatRep** package, the default destination is the ODS Listing destination ``listing``. You can modify the configuration to make the default the ODS StatRep LaTeX tagset by changing the value of ``\SRdefaultdests`` to ``latex``. 

You can specify the ODS destination SAS will use on the ``\Listing`` tag itself, as in this example, which sets the ``dest=latex`` option. Note that, if the global default ``\SRdefaultdests`` is set to ``latex``, there is no need to specify it again on the ``\Listing`` tag.

When you make no explicit selection, the ``Listing`` tag selects all tables and notes. When you run the generated SAS program you can see that the SAS Log displays the ODS objects that are selected for replay. These outputs are displayed in a continuous stream with page breaks handled automatically. That is, the output can go over a page break, with breaks allowed only between ODS objects.The SAS Log displays this table that corresponds to the ``\Listing`` tag:

    Objects                   Type  Status   Group

    Ttest.time.PT             Note  Selected   1
    Ttest.time.Statistics     Table Selected   1
    Ttest.time.ConfLimits     Table Selected   2
    Ttest.time.TTests         Table Selected   3
    Ttest.time.SummaryPanel   Graph            .
    Ttest.time.QQPlot         Graph            .

The ``\Graphic`` tag specifies
- that output should come from the ODS document ``myoutput``
- caption for the output
- filename that contains the output is ``png/myoutb.png``

    \Graphic[store=myoutput, 
             caption={Court Case Duration}]{myoutb}

The ``Graphic`` tag selects all graphics by default. The log file shows the ODS graph objects that are selected for replay. These graphs are displayed in a continuous stream with page breaks handled automatically.
Page breaks can only occur between graphs.The SAS Log displays this table that corresponds to the ``\Graphic`` tag:

    Objects                   Type  Status   Group

    Ttest.time.PT             Note             .
    Ttest.time.Statistics     Table            .
    Ttest.time.ConfLimits     Table            .
    Ttest.time.TTests         Table            .
    Ttest.time.SummaryPanel   Graph Selected   1
    Ttest.time.QQPlot         Graph Selected   2

The final PDF document, which specifies the ``latex`` destination and uses the ``statrep`` tagset, looks like this:
![saslatex3a](images/saslatex3a.png)![saslatex3b](images/saslatex3b.png)![saslatex3c](images/saslatex3c.png)

For comparison, the following is what the final PDF document looks like if you use the default ``listing`` destination. Only  the tabular output has changed; the graphs are identical.
![saslatex4a](images/saslatex4a.png)![saslatex4b](images/saslatex4b.png)![saslatex4c](images/saslatex4c.png)

## Capture Specific Outputs

You don't always want the output to displayed as a continuous stream so **StatRep** provides a flexible way to select ODS objects. In the following ``\Listing``, the ``firstobj=`` option specifies that the output stream should begin with the ``conflimits`` object; the ``lastobj=`` option specifies that the output stream should end with the ``ttests`` object. 

Suppose there were several objects in the ODS document between those two specified objects; they would all be included with this one ``\Listing`` tag.
**StatRep** provides many other methods of ODS object selection; see the *User's Guide* for details.

By specifying the same ODS document in different ``\Listing`` tags, you can show the outputs in the order you want and break them up into parts so you can discuss particular outputs. Your SAS code is only run one time, when the ODS document is created. You can replay the output from that ODS document in any order you like.

    \Listing[store=myoutput, dest=latex, 
             firstobj=conflimits, lastobj=ttests,
             caption={Court Case Duration Analysis}]{myouta}

Now the log shows that the ``ConfLimits`` and ``TTests`` objects are selected.

    Objects                   Type  Status   Group

    Ttest.time.PT             Note             .
    Ttest.time.Statistics     Table            .
    Ttest.time.ConfLimits     Table Selected   1
    Ttest.time.TTests         Table Selected   2
    Ttest.time.SummaryPanel   Graph            .
    Ttest.time.QQPlot         Graph            .

The ``\Graphic`` tag specifies that a single graph is to be captured and displayed, the ``qqplot`` object.

     \Graphic[store=myoutput, 
              objects=qqplot,
              caption={Court Case Duration}]{myoutb}

The log shows that only the ``QQPlot`` object is selected.

    Objects                   Type  Status   Group

    Ttest.time.PT             Note             .
    Ttest.time.Statistics     Table            .
    Ttest.time.ConfLimits     Table            .
    Ttest.time.TTests         Table            .
    Ttest.time.SummaryPanel   Graph            .
    Ttest.time.QQPlot         Graph Selected   1

# Summary

This article provides a couple of simple examples that show you how to get started with **StatRep**. The *User's Guide* also provides simple examples, but includes more in-depth, advanced usage.

Do you have an example you'd like to see or a question about **StatRep**? Leave a comment!
















