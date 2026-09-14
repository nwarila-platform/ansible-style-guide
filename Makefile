SHELL := /bin/sh
.ONESHELL:

.PHONY: install selftest lint check fleet clean

install:
	set -eu
	python3 -m pip install --require-hashes -r requirements.txt -r requirements-dev.txt
	ansible-galaxy collection install --force -r collections/requirements.yml
	printf 'OK: %s\n' 'install'

selftest:
	set -eu
	mkdir -p .audit
	python3 -m rolecheck check --report-only fixtures/style/applications/fail_role > .audit/selftest-style.txt
	test -s .audit/selftest-style.txt
	sed '/^== /,$$d' .audit/selftest-style.txt > .audit/selftest-style.findings
	test -s .audit/selftest-style.findings
	diff -u fixtures/style/expected-fail.txt .audit/selftest-style.findings
	python3 -m rolecheck check fixtures/style/applications/pass_role fixtures/style/applications/boundary_role > .audit/selftest-clean.txt
	test -s .audit/selftest-clean.txt
	test "$$(tail -n 1 .audit/selftest-clean.txt)" = '== total: 2 role(s), 0 finding(s)'
	! awk '$$2 == "TOOL" || $$3 == "TOOL" { found = 1 } END { exit found ? 0 : 1 }' .audit/selftest-clean.txt
	python3 -m rolecheck check --report-only fixtures/structure/struct_fail > .audit/selftest-structure.txt
	test -s .audit/selftest-structure.txt
	sed '/^== /,$$d' .audit/selftest-structure.txt > .audit/selftest-structure.findings
	test -s .audit/selftest-structure.findings
	diff -u fixtures/structure/expected-fail.txt .audit/selftest-structure.findings
	python3 -m unittest discover -s tests -p 'test_*.py'
	printf 'OK: %s\n' 'selftest'

lint:
	set -eu
	python3 -m ruff check rolecheck tests
	printf 'OK: %s\n' 'lint'

check:
	set -eu
	test -n "$(strip $(PATHS))" || { printf '%s\n' 'error: PATHS is empty' >&2; exit 2; }
	python3 -m rolecheck check $(PATHS)
	printf 'OK: %s\n' 'check'

fleet:
	set -eu
	test -n "$(strip $(ROOTS))" || { printf '%s\n' 'error: ROOTS is empty' >&2; exit 2; }
	mkdir -p reports
	rm -f reports/*.txt
	index=1
	for root in $(ROOTS); do
		number=$$(printf '%02d' "$$index")
		report="reports/$$number-$$(basename "$$root").txt"
		python3 -m rolecheck check --report-only "$$root" > "$$report"
		test -s "$$report"
		count=$$(grep -c '^== total:' "$$report")
		test "$$count" -eq 1
		index=$$((index + 1))
	done
	grep -H '^== total:' reports/*.txt
	printf 'OK: %s\n' 'fleet'

clean:
	set -eu
	if test -d reports; then rm -r reports; fi
	rm -f .audit/selftest-*
	find . -type d -name __pycache__ -exec rm -r {} +
	printf 'OK: %s\n' 'clean'
