install:
	@pip install -r requirements.txt

test:
	@export ENV=test && pytest

run:
ifdef path
	@export ENV=local && python main.py -s $(start) -e $(end) -p $(path)
else
	@export ENV=local && python main.py -s $(start) -e $(end)
endif