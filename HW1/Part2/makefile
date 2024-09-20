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
