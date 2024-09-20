BENCHMARKS = euler 
BENCHMARK_FOLDER = benchmark

# TypeScript source file
SRC_TS = $(addprefix $(BENCHMARK_FOLDER)/, $(addsuffix .ts, $(BENCHMARKS)))
# Bril source file
SRC_BRIL = $(addprefix $(BENCHMARK_FOLDER)/, $(addsuffix .bril, $(BENCHMARKS)))
# Bril source file
INTERL_BRIL_JSON = $(addprefix $(BENCHMARK_FOLDER)/, $(addsuffix .bril.json, $(BENCHMARKS)))

# Default BENCHMARKS
all: check-tools run turnt
	@echo "Current directory: $(shell pwd)"

# make rules for check-tools
include makefile.checktool.mak

%.bril: %.ts
	@echo "🎯 Generate [$<] -> [$@]"
	ts2bril $< | bril2txt > $@

%.bril.json: %.bril
	@echo "🎯 Generate [$<] -> [$@]"
	cat $< | bril2json > $@

%.bril.json: %.ts
	@echo "🎯 Generate [$<] -> [$@]"
	ts2bril $< > $@

run_%: $(BENCHMARK_FOLDER)/%.bril.json
	@echo "🧐 Running test on [$<]"
	brili -p < $<

run: $(addprefix run_, $(BENCHMARKS))
	@echo "🧐 Running tests on all benchmarks..."

turnt:
	@echo "🧪 Running turnt tests..."
	@for benchmark in $(BENCHMARKS); do \
		turnt -e ts2bril-brili benchmark/$$benchmark.ts; \
	done

clean:
	@echo "🧹🧺🧼💦✨ Cleaning up..."
	-@rm -f $(INTERL_BRIL_JSON)

.PHONY: all check-tools clean run bril_json