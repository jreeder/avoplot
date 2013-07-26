#Makefile for creating AvoPlot distributions


docs:
	@echo "Auto-generating API documentation"
	sphinx-apidoc -f -o doc/source src/avoplot
	@echo "Building HTML documetation"
	cd doc; make html
	@echo "setting MIME types"
	cd doc; ./set_mime_types.sh
	@echo "Done building documentation"


.PHONY: icons
icons:
	@echo "Generating sized icons from SVG files"
	cd icons; python create_sized_icons.py

clean:
	@echo "Removing build dir"
	rm -rf build
	@echo "Removing dist dir"
	rm -rf dist
	@echo "Removing sized icons"
	rm -rf icons/??x??
	@echo "Removing MANIFEST file"
	rm MANIFEST

dist: docs icons
	@echo "Creating source dist"
	python setup.py sdist
	@echo "Creating Windows installer"
	wine "C:\\Python27\\python.exe" setup.py bdist_wininst --install-script=avoplot_win32_postinstall.py
    
