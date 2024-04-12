IMAGE=globaltalk
VERSION=1.0
TABLET_DRIVER=classic/declrom
VIRTIO_REPO=https://github.com/elliotnunn/classicvirtio
VIRTIO_RELEASE=releases/download/latest/classicvirtio-drivers-latest.zip
SCRIPTS=README.md setup.cfg setup.py $(shell git ls-tree --full-tree -r --name-only --full-name HEAD | sed -ne '/^globaltalk\//p')

$(IMAGE): Dockerfile globaltalk.tar
	env BUILDKIT_PROGRESS=plain \
	  docker buildx build $(REBUILDFLAGS) -f $< \
	    --build-arg http_proxy=$(http_proxy) \
	    --build-arg https_proxy=$(https_proxy) \
	    --build-arg no_proxy=$(no_proxy) \
	    --rm -t $(IMAGE):$(VERSION) . \
	&& docker tag $(IMAGE):$(VERSION) $(IMAGE):latest

run: $(IMAGE) pram.img $(TABLET_DRIVER)
	docker run \
	  -it \
	  --rm \
	  -p [::1]:5910:5910 \
	  --network host \
	  --cap-add=NET_ADMIN --device /dev/net/tun:/dev/net/tun \
	  -v ${PWD}:/$(IMAGE) \
	  $(IMAGE):latest

pram.img:
	 dd if=/dev/zero of=$@ bs=256 count=1

$(TABLET_DRIVER):
	wget $(VIRTIO_REPO)/$(VIRTIO_RELEASE)
	unzip $<

globaltalk.tar: $(SCRIPTS)
	tar -cf $@ $(SCRIPTS)
