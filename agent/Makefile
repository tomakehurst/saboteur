BUILDDIR = build
VERSION = 0.3

.PHONY: clean rpm test

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n breakbox-agent -a noarch -v $(VERSION) --before-install before-install.sh --after-remove after-remove.sh breakbox.py=/usr/bin/breakbox-agent breakbox.sudo=/etc/sudoers.d/breakbox breakbox.init=/etc/init.d/breakbox-agent

test:
	python breakbox-tests.py
