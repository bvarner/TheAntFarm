# Regenerate the QT Resources if the source file changes.
qtrc: app_resources.qrc
	../env/bin/pyside2-rcc app_resources.qrc -o app_resources_rc.py

# Regenerate the QT Python source if the ui Design changes.
qtui: app_resources.qrc the_ant_farm.ui
	../env/bin/pyside2-uic --from-imports the_ant_farm.ui > ui_the_ant_farm.py

clean:
	rm -fr __pycache__
	rm -fr app_resources_rc.py
	rm -fr ui_the_ant_farm.py



