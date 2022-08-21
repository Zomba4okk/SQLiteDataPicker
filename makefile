install:
	@pip install -r requirements.txt

test:
	@export ENV=test && pytest