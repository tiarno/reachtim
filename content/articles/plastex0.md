Title: Convert LaTeX to HTML or XML with Python
Status: Draft
Date: 01-20-2015
Summary: How to convert LaTeX documents using the plasTeX Python package.

**Table of Contents**

[TOC]

# Overview

plasTeX is a pure Python framework for LaTeX document processing. It comes bundled with an XHTML and DocBook XML renderer, as well as a way to simply dump the document to a generic form of XML. 

plasTeX differs from other tools like LaTeX2HTML , TeX4ht , TtH , etc. in that the parsing and rendering of the document are completely separated. This separation makes it possible to render the document in multiple output formats. It also allows the parser to create a cleaner document object, so that the rendering process is easier.

Since the renderer has complete control over which pieces of the document are rendered, your resulting document can be structured quite differently than the input document. 

If you have standard ’plain-vanilla’ LaTeX files, plasTeX will work for you already (see the main user documentation to use the plastex command). And if you have simple customizations, plasTeX can read your package files and work as-is. But when you have more complex styles or classes, you’ll need to extend plasTeX to work with your customized files. It’s quite easily done: there are two tasks to get started:

- add a Python class corresponding to each macro you have defined. You’ll inherit from a standard plasTeX class; often there’s little more to it than that. You define the classes so plasTeX can understand how to parse your new commands.

- add a template to render the content resulting from plasTex parsing. Your command will have some data or text that needs to be handled in some way in order to display itself correctly, depending on what format you want to render to. The template tells the renderer how to do that.

Once you have those tasks completed, you set your environment PATHs and run plastex. That’s all there is to it. 



    plasTeX version 1.0

    General Options:
      -c, --config=          Load additional configuration file
      --no-theme-extras, --copy-theme-extras
                             Copy files associated with the theme to the output
                             directory [yes]
      --kpsewhich=           Program which locates LaTeX files and packages
                             [kpsewhich]
      --paux-dirs=val1,val2,...
                             Directories where *.paux files should be loaded
                             from. [[]]
      --renderer=            Renderer to use for conversion [XHTML]
      --theme=               Theme for the renderer to use [default]
      --xml                  Dump XML representation of the document (for
                             debugging) [no]

    Document Options:
      --base-url=            Base URL for inter-node links
      --counter=[ ... ]      Set initial counter values
      --index-columns=n      Number of columns to split the index entries into
                             [2]
      --lang-terms=          Specifies a ':' delimited list of files that
                             contain language terms []
      --link=[ ... ]         Set links for use in navigation
      --sec-num-depth=n      Maximum section depth to display section numbers
                             [2]
      --title=               Title for the document
      --toc-depth=n          Number of levels to display in the table of
                             contents [3]
      --toc-non-files        Display sections that do not create files in the
                             table of contents [no]

    File Handling Options:
      --bad-filename-chars=  Characters that should not be allowed in a filename
                             [: #$%^&*!~`"'=?/{}[]()|<>;\,.]
      --bad-filename-chars-sub=
                             Character that should be used instead of an illegal
                             character [-]
      -d, --dir=             Directory to put output files into [$jobname]
      --escape-high-chars    Escape characters that are higher than 7-bit [no]
      --filename=            Template for output filenames [index [$id,
                             sect$num(4)]]
      --input-encoding=      Input file encoding [utf-8]
      --log                  Log messages go to log file instead of console [no]
      --output-encoding=     Output file encoding [utf-8]
      --split-level=n        Highest section level that generates a new file [2]

    Image Generation Options:
      --enable-image-cache, --disable-image-cache
                             Enable image caching between runs [no]
      --enable-images, --disable-images
                             Enable image generation [yes]
      --image-baseline-padding=n
                             Amount to pad the image below the baseline [0]
      --image-base-url=      Base URL for all images
      --image-compiler=      LaTeX command to use when compiling image document
      --image-filenames=     Template for image filenames [images/img-$num(4)]
      --imager=              LaTeX to image program [dvipng dvi2bitmap pdftoppm
                             gspdfpng gsdvipng OSXCoreGraphics]
      --image-resolution=n   Resolution of images document [0]
      --image-scale-factor=num
                             Factor to scale externally included images by [1.0]
     --save-image-file, --delete-image-file
                             Should the temporary images.tex file be saved for
                             debugging? [no]
      --opaque-images, --transparent-images
                             Specifies whether the image backgrounds should be
                             transparent or not [no]
      --vector-imager=       LaTeX to vector image program [none dvisvgm]
