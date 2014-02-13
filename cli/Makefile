BUILDDIR = build
VERSION = 0.2

.PHONY: clean rpm

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n breakbox-cli -a noarch -v $(VERSION) breakbox-cli.py=/usr/bin/bbox
