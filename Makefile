BUILDDIR = build
VERSION = 0.7

.PHONY: clean rpm deb test

clean:
	-rm -rf tests/*.pyc
	-rm -rf saboteur/*.pyc
	-rm -rf $(BUILDDIR)

rpm:
	-mkdir -p build
	fpm -s dir -t rpm -d "python >= 2.6" -p build -n saboteur --license "Apache 2.0" --vendor "Tom Akehurst" -m "Tom Akehurst" --url "https://github.com/tomakehurst/saboteur" --description "A fault injection tool for resilience testing" -a noarch -v $(VERSION) --before-install packaging/before-install.sh --after-install packaging/after-install.sh --after-remove packaging/after-remove.sh --rpm-user saboteur --rpm-group saboteur saboteur=/usr/lib/ packaging/saboteur.sudo=/etc/sudoers.d/saboteur packaging/saboteur.init=/etc/init.d/saboteur-agent

deb:
	-mkdir -p build
	fpm -s dir -t deb -d "python >= 2.6" -n saboteur --license "Apache 2.0" --vendor "Tom Akehurst" -m "Tom Akehurst" --url "https://github.com/tomakehurst/saboteur" --description "A fault injection tool for resilience testing" -a all -v $(VERSION) --before-install packaging/before-install.sh --after-install packaging/after-install.sh --after-remove packaging/after-remove.sh --deb-user saboteur --deb-group saboteur saboteur=/usr/lib/ packaging/saboteur.sudo=/etc/sudoers.d/saboteur packaging/saboteur.init=/etc/init.d/saboteur-agent
	mv saboteur*.deb build

test:
	python -m tests
