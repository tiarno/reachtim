Title: SAS Generated LaTeX Output with the StatRep Package
Status: Draft
Slug: statrep-latex
Date: 11-16-2014
Summary: How to use StatRep with SAS-generated LaTeX output for reproducible research.

**Table of Contents**

[TOC]

# Overview

# Configuration

# The StatRep Tagset and Style

# Examples

In the examples that follow, the following document preamble, data step and proc step are used. 

The text with colored background in the following explanations provides an overview of what **StatRep** and SAS are doing behind the scenes. There is no need to study them unless you want to know how it all works together.

    :::latex
    \documentclass{article}
    \usepackage[margin=1in]{geometry}
    \usepackage{statrep}
    \begin{document}
    
    The SAS datastep and analysis follows.
    
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

The code creates a SAS data set ``time`` and invokes the TTEST procedure. 

The result is that all output created by the TTEST procedure is contained in an ODS document named ``myoutput``. The way that output is displayed is determined not by the analytical code, but the ``\Listing`` and ``\Graphic`` tags; these tags request the ODS document to replay output objects into external files (on disk).

## Capture All Outputs as a Single Stream

In this example, the output tags make no specific request for output. The ``\Listing`` tag specifies 
- that output should come from the ODS document ``myoutput`` which matches the ``store=`` option on the ``Sascode`` block.
- the output destination is ``latex`` 
- caption for the output
- filename that contains the output is ``lst/myouta.lst``

Note that, if the global default ``\SRdefaultdests`` is set to ``latex``, there is no need to specify it again on the ``\Listing`` tag.

    \Listing[store=myoutput, dest=latex, 
             caption={Court Case Duration Analysis}]{myouta}
    text about table

By default, the ``Listing`` tag selects all tables and notes. When you run the generated SAS program you can see that the log file shows the ODS objects that are selected for replay. These outputs are displayed in a continuous stream with page breaks handled automatically.

Page breaks can only occur between output objects.

    Objects                   Type  Status   Group

    Ttest.time.PT             Note  Selected   1
    Ttest.time.Statistics     Table Selected   1
    Ttest.time.ConfLimits     Table Selected   2
    Ttest.time.TTests         Table Selected   3
    Ttest.time.SummaryPanel   Graph            .
    Ttest.time.QQPlot         Graph            .

The ``\Graphic`` tag specifies
- that output should come from the ODS document ``myoutput``
- the output destination is ``latex`` (this doesn't really change the output but it's okay to leave it)
- caption for the output
- filename that contains the output is ``png/myoutb.png``

    \Graphic[store=myoutput, dest=latex,
             caption={Court Case Duration}]{myoutb}

The ``Graphic`` tag selects all graphics by default. The log file shows the ODS graph objects that are selected for replay. These graphs are displayed in a continuous stream with page breaks handled automatically.

Page breaks can only occur between graphs.

    Objects                   Type  Status   Group

    Ttest.time.PT             Note             .
    Ttest.time.Statistics     Table            .
    Ttest.time.ConfLimits     Table            .
    Ttest.time.TTests         Table            .
    Ttest.time.SummaryPanel   Graph Selected   1
    Ttest.time.QQPlot         Graph Selected   2

## Capture Specific Outputs

You don't always want the output to displayed as a continuous stream so **StatRep** provides a flexible way to select ODS objects. In the following ``\Listing``, the ``firstobj=`` option specifies that the output stream should begin with the ``conflimits`` object; the ``lastobj=`` option specifies that the output stream should end with the ``ttests`` object. 

Suppose there were several objects in the ODS document between those two specified objects; they would all be included with this one ``\Listing`` tag.
**StatRep** provides many other methods of ODS object selection; see the *User's Guide* for details.

By specifying the same ODS document in different ``\Listing`` tags, you can show the outputs in the order you want and break them up into parts so you can talk about particular objects. Your SAS code is only run one time, when the ODS document is created. You can replay the output from that ODS document in any order you like.

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

     \Graphic[store=myoutput, dest=latex,
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

Unlike the *StatRep User's Guide*, this article provides a couple of simple examples that show you how to get started with **StatRep**. The *User's Guide* provides simple examples, plus more in-depth, advanced usage.

Do you have an example you'd like to see or a question about **StatRep**? Leave a comment!
















