build:
	npm install --package-lock-only
	sudo docker build --tag=kyoheiu.dev:$(VER) .
	sudo docker save -o ./image.tar kyoheiu.dev:${VER}
