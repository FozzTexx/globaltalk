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

run: $(IMAGE)
	docker run -it --rm -p 5910:5910 -v ${PWD}:/$(IMAGE) $(IMAGE):latest
