all: pcfg_tool

pcfg_tool:
	@echo "build tool..."
	pcfg_tool

clean:
	find . -type f -name *.pyc -delete
    find . -type d -name __pycache__ -delete

