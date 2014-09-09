Title: How To Pad a Book to an *N* Page Signature
Category: LaTeX
Date: 2014-Sep-20
Status: Draft
Tags: how-to
Summary: How to force a book to have a multiple of *n* pages

The printer who prints my PDF documents wants them to have the number of pages a multiple of four. That isn't exactly a **signature**, but it's the word that comes to mind. Of course this is easy to do by hand if you have Adobe Acrobat or a similar tool, but this short article shows how to use a LaTeX command to accomplish this automatically.

This example depends on the `ifthen`, `calc` packages. As usual with TeX and LaTeX there are multiple ways to solve this problem; this is just one.

What is a real **signature**? A signature is group of pages printed on a large sheet in such a way that you can fold and cut to the finished page size. This [article](http://www.designersinsights.com/designer-resources/understanding-and-working-with-print) describes in detail what `signature` means in the print world. 

What this article is about is not that; we will create a LaTeX command to pad a PDF with blank pages until the total number of pages is a multiple of four. Usually the printer will set up the signature, but in many cases they do prefer that the number of pages is an integer multiple of the final signature. 

Given the problem, it's pretty clear we're going to need a [modulo](http://en.wikipedia.org/wiki/Modulo_operation) function and LaTeX doesn't come with one built in. We can program it since $a \mod n$ is given by $a - n (a\\n)$ where the $\\$ is the `integer division` operator. When TeX does division on integers, the fractional part is discarded, which is a form (`truncated`) of integer division. Here is a little example:

    \documentclass{article}
    \usepackage{calc}
    \usepackage{ifthen}
    \newcounter{dividend}
    \newcounter{divisor}
    \newcounter{answer}

    \begin{document}
    \noindent Starting at 10:
    \setcounter{dividend}{10}
    \setcounter{divisor}{10}

    \whiledo{\thedivisor>0}{
        \setcounter{answer}{\thedividend/\thedivisor}
        \noindent divisor: \thedivisor\ answer: \theanswer\\
        \setcounter{divisor}{\thedivisor - 1}
    }
    \end{document}

Now for the macro. First set up two new counters, `modpage` and `realpage`. Our new command is called `padpages`.

I use the `memoir` class so I include a couple of commands that are specific to that class, namely `thesheetsequence` provides the number of the current page; not necessarily the same as the page number that is printed on the page, but the actual number of the page as counted from the beginning of the document. You can use the [`lastpage`](http://ctan.org/pkg/lastpage) or [`pageslts`](http://ctan.org/pkg/pageslts) package to get the same result.

I also take advantage of the `aliaspagestyle` command, aliasing the style `cleared` to be identical to `empty`. I don't want headings or page numbers on the blank pages we're going to insert.

    \newcounter{modpage}
    \newcounter{realpage}
    \newcommand\padpages{%
        \setcounter{realpage}{\thesheetsequence}
        \aliaspagestyle{cleared}{empty}%
        \pagestyle{empty}%

Manipulate the `modpage` counter to be the real page number *mod* 4. Since 
\[
a \mod(n) = a - n (a\\n)
\]
\[
\text{realpage} \mod(4) = \text{realpage} - 4 (\text{realpage}\\4)
\] 

Use the `modpage` counter to hold the intermediate calculation and at the end we have the modulo:

        \setcounter{modpage}{{\therealpage/4} * -4}
        \setcounter{modpage}{\themodpage + \therealpage}%

If it is zero, we don't need to anything since the page number is already a multiple of 4.

    \ifthenelse{\themodpage=0}%
        {\relax}%

Otherwise, we need to add the $4 - \text{realpage}\mod(4)$ pages:

        {\setcounter{modpage}{{\themodpage * -1} + 4}%
            \whiledo{\themodpage>0}{%
                \mbox{}\clearpage\mbox{}%
                \setcounter{modpage}{\themodpage - 1}%
            }% end whiledo
        }% end ifthenelse
    }% end padpages

The `\mbox{}\clearpage\mbox{}` forces a blank page to be added. 

The `\padpages` macro should come at the very end of the document; depending on what other packages you use, you might find the [`atveryend`](http://www.ctan.org/pkg/atveryend) package useful.

Finally, here is the entire code. In this example I omit the `memoir` parts and load instead the `pageslts` package. Additionally, it takes an argument--the integer which the number of pages should be a multiple of.

    \pagenumbering{arabic}
    \newcounter{modpage}
    \newcommand\padpages[1]{%
        \pagestyle{empty}%
        \setcounter{modpage}{{\theCurrentPage/#1} * -#1 + \theCurrentPage}%
        \ifthenelse{\themodpage=0}%
        {\relax}%
        {\setcounter{modpage}{#1 - \themodpage}%
            \whiledo{\themodpage>0}{%
                \mbox{}\clearpage\mbox{}%
                \setcounter{modpage}{\themodpage - 1}%
            }% end whiledo
        }% end ifthenelse
    }% end padpages

 For example, if $p = 121$ then $p \% 4 = 1$ which is defined as
\[
  121 - 4(\mbox{floor}(\frac{121}{4})) = 121-4*30 = 1
\]

    * The `ifthen` package provide the `ifthenelse` and `whiledo` commands.
    * The `calc` package enables us to do infix math to set the `modpage counter easily`
    * The `pageslts` package provides the counter `CurrentPage`