Subshift
========

Description
-----------
This package contains a tool for handling times in movie subtitles.
Basic features are moving subtitles forward and backward from specified title 
or for all titles, supporting 'SubRip(srt)' and 'MicroDVD(sub)' formats.

Formats
-------
Note that 'SubRip(srt)' file have to be terminated by empty line, 
and input file have to be in UNIX format (newline=#10)

Requirements
------------
The code is written in the Python language and uses 
modules sys, getopt and re.

Ussage
------
You can find out all information about parameters 
in help text ('subshift -h')

Examples
--------
'$ subshift -t +0:0:3,5 file.srt > newfile.srt'
Add to times in subtitles 3 seconds and !005! miliseconds

'$ subshift -t -0:0:4,500 file.srt > newfile.srt'
Subtract 4 seconds and 500 miliseconds (half second)

Program can be used also as filter:

---------------------------------------------------
$ cat file.srt | subshift -t +0:0:3,0 > newfile.srt	
$ subshift -i srt -o sub:25.0 file.srt > newfile.sub	
$ subshift -i sub:25.00 -o srt file.sub > newfile.srt
$ subshift -i sub:25.00 -o sub:23.97 file.sub > newfile.sub
---------------------------------------------------
