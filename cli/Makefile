BUILDDIR = build
VERSION = 0.5

.PHONY: clean rpm

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n saboteur-cli -m "Tom Akehurst" --description "A command-line interface for controlling Saboteur" -a noarch -v $(VERSION) sab=/usr/bin/sab
