# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
BUILDOPTS = --repeat-table-rows
BUILDCMD  = rst2pdf
BUILDDIR  = _build
CONFIG    = conf.ini
INPUT     = index.rst
OUTPUT    = $(BUILDDIR)/index.pdf

ALLOPTS   = --config=$(CONFIG) $(BUILDOPTS)

.PHONY: clean

pdf:
	$(BUILDCMD) $(ALLOPTS) $(INPUT) -o $(OUTPUT)
	@echo "Build finished. The pdf pages are in $(OUTPUT)."

clean:
	-rm -rf $(BUILDDIR)/*
