clean:
	rm -rf .tox .cache .eggs *.egg-info .coverage .DS_Store
	find . -name '*.pyc' -exec rm '{}' ';'

sort:
	isort -rc shopit tests
