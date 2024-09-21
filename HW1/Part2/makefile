DEMOS = euler.bril.json add.bril.json
STUB_PASSES = jmp add

all: turnt

turnt:
	@echo "🧪 Running turnt tests..."

	@for stub in $(STUB_PASSES); do \
		turnt -e pin_stub_print-brili -a $$stub $(addprefix demo/pin_stub_print_$$stub/, $(DEMOS)) ; \
	done

	@for stub in $(STUB_PASSES); do \
		turnt -e pin_stub_print -a $$stub $(addprefix demo/pin_stub_print_$$stub/, $(DEMOS)) ; \
	done

diff:
	@echo "🧐 Show diff before & after..."
	@for stub in $(STUB_PASSES); do \
		for demo in $(DEMOS); do \
			stub_out=$$(echo $$demo | sed 's/\.json/\.stub-out/'); \
			echo "🔍 [$$demo] vs [$$stub_out]" ; \
			diff --color $(addprefix demo/pin_stub_print_$$stub/, $$demo) $(addprefix demo/pin_stub_print_$$stub/, $$stub_out) ; \
		done \
	done

run:
	@echo "💡 Run all Stub-analyzer\n"
	@for stub in $(STUB_PASSES); do \
		for demo in $(DEMOS); do \
			echo "🚀 Running Stub-analyzer[$$stub] on [$$demo] ..." ; \
			python analyzer/pin_stub_print_$$stub.py demo/pin_stub_print_$$stub/$$demo > /dev/null ; \
			echo "\n" ; \
		done \
	done