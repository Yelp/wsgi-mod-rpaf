.PHONY: all
all: venv test

.PHONY: venv
venv:
	tox -e venv

.PHONY: test
test:
	tox $(REBUILD_FLAG)

.PHONY: clean
clean:
	find -name '*.pyc' -delete
	rm -rf .tox
	rm -rf ./venv
