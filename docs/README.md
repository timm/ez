# Prompts

## [xai.1](xai.pdf)

Generate a groff man page for xai.py. include a para describing the data format. list all flags (eg. -s and --all)

    man ./xai1 # terminal browsing
    xai,pdf genrated from groff -man -Tps xai.1 | ps2pdf - xai.pdf # pdf

## [xai_pdoc.html](https://timm.github.io/xai/docs/xai_pdoc)

pdoc -o ~/tmp --force --html xai.py ; open ~/tmp/xai.html

## [xai.html](https://timm.github.io/xai/docs/xai)


See prompt in the "about" page.


