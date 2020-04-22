
PYTHON?=python3

all:
	@echo "Available targets"
	@echo "  test              - Run unit tests"
	@echo "  coverage          - Run test coverage"
	@echo "  lint              - Run pylint"

test:
	PYTHONPATH=`pwd` $(PYTHON) unittests/test_all.py

lint:
	$(PYTHON) -m pylint pyqtcmd

coverage:
	PYTHONPATH=`pwd`:`pwd`/unittests $(PYTHON) -m coverage run --branch --omit 'unittests/*,/usr/*' unittests/test_all.py
	$(PYTHON) -m coverage html
