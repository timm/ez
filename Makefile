SHELL := /bin/bash
GIT_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null)

help: ## show help.
	@gawk -f $(GIT_ROOT)/sh/makehelp.awk $(MAKEFILE_LIST)

ok: ~/gits/moot ## set up baseline
	@chmod +x *.py

push: ## save to cloud
	@read -p "Reason? " msg; git commit -am "$$msg"; git push; git status

clean: ## remove pycadhe
	rm -rf __pycache__

ghReset:  
	git remote set-url origin https://timmenzies@github.com/timmenzies/ez.git

lint: $f.py  ## Lint python file x.py using `make lint f=x`    
	# disable naming, docstring, and formatting rules
	#ruff check $f.py  --ignore  E401,E701,E702
	@pylint --disable=C0103,C0104,C0105,C0115,C0116,C0321,C0410 \
	 	      --disable=E0213 \
	 				--disable=R1735 \
	 				--disable=W0106,W0201,W0311 $f.py

#------------------------
# repo speicif stuff
Data=~/gits/moot/optimize/misc/auto93.csv

SA    : ok $(Data); ./sa.py 1 $(Data) ## simulated annelling
KMEANS: ok $(Data); ./kmeans.py 1 $(Data) ## K-Means
KDTREE: ok $(Data); ./kdtree.py 1 $(Data) ## KD-Tree
FASTMAP: ok $(Data); ./fastmap.py 1 $(Data) ## Fastmap

YS: ## show y shorting
	@./ez.py --ys ~/gits/moot/optimize/misc/auto93.csv  | column -t

TREE: ## show y shorting
	@./ez.py --tree ~/gits/moot/optimize/misc/auto93.csv  

~/gits/moot:  ## get the data
	mkdir -p ~/gits
	git clone http://tiny.cc/moot $@

~/tmp/ez_test.log:  ## run ezrtest on many files
	@mkdir -p ~/tmp
	@$(MAKE) todo=test files="$(HOME)/gits/moot/optimize/*/*.csv" run | tee $@ 

run:
	@time ls -r $(files) | xargs -P 24 -n 1 -I{} sh -c 'python3 -B ez.py --$(todo) "{}"'

#--------------------------
MY=@bash sh/ell

.PHONY: sh
.IGNORE: sh
sh: ## demo of my shell
	@-bash --init-file $(GIT_ROOT)/sh/ell -i

mytree: ## demo of my tree
	$(MY) tree

ls: ## demo of my ls
	$(MY) ls

tmux: ## demo of my tmux
	$(MY) tmux

grep: ## demo of my grep
	$(MY) grep es Makefile

col: ## demo of my col
	printf "name,age,city\nalice,30,raleigh\nbob,25,boston\ncarol,40,denver\n" \
		| bash $(GIT_ROOT)/sh/ell col

~/tmp/%.pdf: %.py  ## .py ==> .pdf
	@mkdir -p ~/tmp
	@echo "pdf-ing $@ ... "
	@a2ps               \
		-Br               \
		--quiet            \
		--landscape          \
		--chars-per-line=85  \
		--line-numbers=1      \
		--borders=no           \
		--pro=color             \
		--columns=3              \
		-M letter                 \
		-o - $< | ps2pdf - $@
	@open $@
