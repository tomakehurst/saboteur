BUILDDIR = build
VERSION = 0.1

.PHONY: clean rpm

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -p build -n breakbox-agent -a noarch -v $(VERSION) --before-install before-install.sh --after-remove after-remove.sh breakbox.py=/usr/bin/breakbox-agent breakbox.sudo=/etc/sudoers.d/breakbox breakbox.init=/etc/init.d/breakbox-agent

