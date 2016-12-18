#!/bin/bash
bash clean.sh         
pdflatex master.tex -interaction=nonstop
bibtex master
pdflatex master.tex -interaction=nonstop
pdflatex master.tex -interaction=nonstop
evince master.pdf
bash clean.sh
