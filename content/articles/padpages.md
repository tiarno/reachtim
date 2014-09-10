Title: How To Pad a Book to an *N* Page Signature
Category: LaTeX
Date: 2014-Sep-20
Status: Draft
Tags: how-to
Summary: How to force a book to have a multiple of *n* pages

Does your printer want the number of pages in your PDFs to be an integer multiple? Mine does. The number of pages in my documents must be a multiple of four. That isn't exactly a **signature**, but that's the first word that comes to mind. Of course this is easy to do by hand if you have Adobe Acrobat or a similar tool, but this short article shows how to create and use a LaTeX command that will do it for you automatically.

This example depends on the `ifthen`, `calc`, and `pageslts` packages. As usual with TeX and LaTeX there are multiple ways to solve this problem; this is just one.

What is a real **signature**? A signature is group of pages printed on a large sheet in such a way that you can fold and cut to the finished page size. This [article](http://www.designersinsights.com/designer-resources/understanding-and-working-with-print) describes in detail what `signature` means in the print world. 

What this article is about is not that; we will create a LaTeX command to pad a PDF with blank pages until the total number of pages is a multiple of four. Usually the printer will set up the signature, but in many cases they do prefer that the number of pages is an integer multiple of the final signature. 

Given the problem, it's pretty clear we're going to need a [modulo](http://en.wikipedia.org/wiki/Modulo_operation) function and LaTeX doesn't come with one built in. We can program it since $a \mod n$ is given by $a - n (a\\n)$ where the $\\$ is the `integer division` operator. When TeX does division on integers, the fractional part is discarded, which is a form (`truncated`) of integer division. Here is a little example you might enjoy playing with:

    :::latex
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

Now for the macro. We'll name it `padpages`. First, create a new counter, `modpage`. 

If you use the the `memoir` class, you can take advantage of the command `thesheetsequence`, which provides the number of the current page; not necessarily the same as the page number that is printed on the page, but the actual number of the page as counted from the beginning of the document. In this example, we'll use the [`pageslts`](http://ctan.org/pkg/pageslts) package to get the same result.

For the blank pages we're going to insert, we don't want headings or page numbers so set the page style to `empty`.

    :::latex
    \pagenumbering{arabic}
    \newcounter{modpage}
    \newcommand\padpages{%
        \pagestyle{empty}%

Manipulate the `modpage` counter to be the real page number *mod* 4. Since 
\[
a \mod(n) = a - n (a\\n)
\]
\[
\text{pagenum} \mod(4) = \text{pagenum} - 4 (\text{pagenum}\\4)
\] 

Use the `modpage` counter to hold the intermediate calculation and at the end we have the modulo:

    :::latex
        \setcounter{modpage}{\theCurrentPage - 4*{\theCurrentPage/4}}

If it is zero, we don't need to anything since the page number is already a multiple of 4.

    :::latex
    \ifthenelse{\themodpage=0}%
        {\relax}%

Otherwise, we need to add $4 - \text{pagenum}\mod(4)$ pages:

    :::latex
        {\setcounter{modpage}{4 - \themodpage}%
            \whiledo{\themodpage>0}{%
                \mbox{}\clearpage\mbox{}%
                \setcounter{modpage}{\themodpage - 1}%
            }% end whiledo
        }% end ifthenelse
    }% end padpages

The `\mbox{}\clearpage\mbox{}` forces a blank page to be added. 

The `\padpages` macro should come at the very end of the document; depending on what other packages you use, you might find the [`atveryend`](http://www.ctan.org/pkg/atveryend) package useful.

Finally, here is the entire code and this time it takes an argument--the integer which the number of pages should be a multiple of.

    :::latex
    \pagenumbering{arabic}
    \newcounter{modpage}
    \newcommand\padpages[1]{%
        \pagestyle{empty}%
        \setcounter{modpage}{\theCurrentPage - #1*{\theCurrentPage/#1}}%
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
  121 - 4(\text{floor}(\frac{121}{4})) = 121-4*30 = 1
\]

    * The `ifthen` package provide the `ifthenelse` and `whiledo` commands.
    * The `calc` package enables us to do infix math to set the `modpage counter easily`
    * The `pageslts` package provides the counter `CurrentPage`