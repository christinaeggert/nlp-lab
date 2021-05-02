PYTHON = python3

.DEFAULT_GOAL = pcfg_tool

pcfg_tool:
	mkdir output
	${PYTHON} pcfg_tool.py

clean:
	rm -r *.pyc
	rmdir -r output
