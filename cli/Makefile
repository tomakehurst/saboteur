BUILDDIR = build
VERSION = 0.4

.PHONY: clean rpm

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n saboteur-cli -a noarch -v $(VERSION) sab=/usr/bin/bbox
