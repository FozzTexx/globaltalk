IMAGE=globaltalk
VERSION=1.0

$(IMAGE): Dockerfile
	env BUILDKIT_PROGRESS=plain \
	  docker buildx build $(REBUILDFLAGS) -f $< \
	    --build-arg http_proxy=$(http_proxy) \
	    --build-arg https_proxy=$(https_proxy) \
	    --build-arg no_proxy=$(no_proxy) \
	    --rm -t $(IMAGE):$(VERSION) . \
	&& docker tag $(IMAGE):$(VERSION) $(IMAGE):latest

run: $(IMAGE) pram.img classic/declrom
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

classicvirtio-drivers-latest.zip:
	wget https://github.com/elliotnunn/classicvirtio/releases/download/latest/$@

classic/declrom: classicvirtio-drivers-latest.zip
	unzip $<
