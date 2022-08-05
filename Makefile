CODE_DIR = TheAntFarm

run: init
	$(MAKE) -C $(CODE_DIR) qtrc qtui
	./env/bin/python3 -m TheAntFarm

# Setup the virtual environment if the requirements change.
init: requirements.txt
	python3 -m venv ./env
	./env/bin/pip3 install -r requirements.txt

clean:
	rm -fr __pycache__
	rm -fr app_resources_rc.py
	rm -fr ui_the_ant_farm.py
	$(MAKE) -C $(CODE_DIR) clean

clean-env:
	rm -fr ./env

