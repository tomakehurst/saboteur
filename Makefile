BUILDDIR = build
VERSION = 0.6

.PHONY: clean rpm deb test

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n saboteur --license "Apache 2.0" --vendor "Tom Akehurst" -m "Tom Akehurst" --url "https://github.com/tomakehurst/saboteur" --description "A fault injection tool for resilience testing" -a noarch -v $(VERSION) --before-install packaging/before-install.sh --after-remove packaging/after-remove.sh saboteur/saboteur.py=/usr/bin/saboteur-agent packaging/saboteur.sudo=/etc/sudoers.d/saboteur packaging/saboteur.init=/etc/init.d/saboteur-agent sab=/usr/bin/sab

deb:
	-mkdir -p build
	fpm -s dir -t deb -d "python >= 2.6" -n saboteur --license "Apache 2.0" --vendor "Tom Akehurst" -m "Tom Akehurst" --url "https://github.com/tomakehurst/saboteur" --description "A fault injection tool for resilience testing" -a all -v $(VERSION) --before-install packaging/before-install.sh --after-remove packaging/after-remove.sh saboteur/saboteur.py=/usr/bin/saboteur-agent packaging/saboteur.sudo=/etc/sudoers.d/saboteur packaging/saboteur.init=/etc/init.d/saboteur-agent sab=/usr/bin/sab
	mv saboteur*.deb build

test:
	python -m saboteur.tests.saboteur-tests
