BUILDDIR = build
VERSION = 0.5

.PHONY: clean rpm test

clean:
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n saboteur-agent -m "Tom Akehurst" --description "A fault injection agent for resilience testing" -a noarch -v $(VERSION) --before-install before-install.sh --after-remove after-remove.sh saboteur.py=/usr/bin/saboteur-agent saboteur.sudo=/etc/sudoers.d/saboteur saboteur.init=/etc/init.d/saboteur-agent

test:
	python saboteur-tests.py
