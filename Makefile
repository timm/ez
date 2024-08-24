SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

Top=$(shell git rev-parse --show-toplevel)
Data ?= $(Top)/data/optimize
Tmp  ?= $(HOME)/tmp
Act  ?= _mqs

help: ## print help
	printf "\nmake [OPTIONS]\n\nOPTIONS:\n"
	grep -E '^[a-zA-Z_\.-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

pull    : ## download
	git pull

push    : ## save
	echo -en "Why this push? "; read x; git commit -am "$$x"; git push; git status

$(Tmp)/%.pdf: %.py  ## make doco: .py ==> .pdf
	mkdir -p ~/tmp
	echo "pdf-ing $@ ... "
	a2ps                 \
		-Br                 \
		--chars-per-line=90 \
		--file-align=fill      \
		--line-numbers=1        \
		--pro=color               \
		--left-title=""            \
		--borders=no             \
	    --left-footer="$<  "               \
	    --right-footer="page %s. of %s#"               \
		--columns 3                 \
		-M letter                     \
	  -o	 $@.ps $<
	ps2pdf $@.ps $@; rm $@.ps
	open $@

$(Tmp)/%.html : %.py etc/py2html.awk etc/b4.html docs/ezr.css Makefile ## make doco: md -> html
	echo "$< ... "
	gawk -f etc/py2html.awk $< \
	| pandoc -s  -f markdown --number-sections --toc --toc-depth=5 \
					-B etc/b4.html --mathjax \
  		     --css ezr.css --highlight-style tango \
					 --metadata title="$<" \
	  			 -o $@ 

# another commaned
Out=$(HOME)/tmp
acts: ## experiment: mqs
	mkdir -p ~/tmp
	$(MAKE)  actb4  > $(Tmp)/acts.sh
	bash $(Tmp)/acts.sh

actb4: ## experiment: mqs
	mkdir -p $(Out)/$(Act)
	$(foreach d, config hpo misc process,         \
		$(foreach f, $(wildcard $(Data)/$d/*.csv),   \
				echo "python3 $(PWD)/ezr.py -D -t $f -e $(Act)  | tee $(Out)/$(Act)/$(shell basename $f) & "; ))
