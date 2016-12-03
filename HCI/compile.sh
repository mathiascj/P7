#!/bin/bash
bash clean.sh         
pdflatex master.tex
bibtex master
pdflatex master.tex
pdflatex master.tex
evince master.pdf
bash clean.sh
