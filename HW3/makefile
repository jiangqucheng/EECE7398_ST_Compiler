# command: 
# python df_analysis.py [--save-dir SAVE_DIR] ANALYSIS DEMO_BRIL_FILE
# example: 
# python df_analysis.py liveness ./example/in_class_example_2.bril
# 
# loop  ANALYSIS = liveness, availability, busy
# loop  DEMO_BRIL_FILE = all bril files in ./example/
# save-dir = ./output/

# write me the makefile

SAVEDIR = ./output
INPUTDIR = ./example
ANALYSES = liveness availability busy
BRIL_FILES = $(wildcard $(INPUTDIR)/*.bril)

.PHONY: all
all: $(foreach file,$(BRIL_FILES),$(SAVEDIR)/$(notdir $(file)))


$(SAVEDIR)/%: $(INPUTDIR)/%
	@mkdir -p $(SAVEDIR)
	@echo "Running analysis on $<"
	# some blank lines to run.log
	@echo "" >> $(SAVEDIR)/run.log
	@echo "Running analysis on $<" >> $(SAVEDIR)/run.log
	$(foreach analysis,$(ANALYSES), \
		python df_analysis.py --save-dir $(SAVEDIR) $(analysis) $< >> $(SAVEDIR)/run.log;)

clean:
	-@ rm -rf $(SAVEDIR)
