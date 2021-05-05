PYTHON = python3

.DEFAULT_GOAL = pcfg_tool

pcfg_tool:
	@#@${PYTHON} -m venv vir_env
	@#@. vir_env/bin/activate
	@#@mkdir -p output
	@cp pcfg_tool.py pcfg_tool
	@chmod +x pcfg_tool
	@#@cp induce_grammar.py vir_env/induce_grammar.py
	@#@cd vir_env;./bin/pip3 install -r ../requirements.txt; cd ..

clean:
	@rm pcfg_tool || true
	@#@rm vir_env/induce_grammar.py || true
	@#@rm output/* || true
	@#@rmdir vir_env/output || true
