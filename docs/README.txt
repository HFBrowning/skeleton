A readme to describe the contents of 'docs'
Hilary Browning
1:21 PM 9/13/2018

This folder contains files to build documentation content, as well as the finalized output of the documentation in two formats.

source 
------
- These files in here can build the Sphinx code documentation, if Sphinx exists in the system. Some essential elements of the build are not git-tracked (a makefile, etc) but all of the content is.
- Each .rst is a page in the documentation and can be edited by hand as a text file to reflect new introduction material, etc. 
- conf.py controls the way the documentation looks


build
-----
- html is the complete html documentation
