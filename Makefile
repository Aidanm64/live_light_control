
build:
	docker build -t live-light-control .

run: build
	docker run -ti live-light-control

test_it: build
	docker run -ti live-light-control pytest -s

run_script: build
	docker run -ti live-light-control python /app/scripts/${s}