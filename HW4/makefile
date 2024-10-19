# command: 
# python dom_analysis.py [--save-dir SAVE_DIR] DEMO_BRIL_FILE
# example: 
# python dom_analysis.py ./example/in_class_example_2.bril
# 
# loop  DEMO_BRIL_FILE = all bril files in ./example/
# save-dir = ./output/

SAVEDIR = ./output
INPUTDIR = ./example
BRIL_FILES = $(wildcard $(INPUTDIR)/**/*.bril)
TARGET_TASKS = $(patsubst $(INPUTDIR)/%.bril,$(SAVEDIR)/%,$(BRIL_FILES))

.PHONY: all $(TARGET_TASKS) clean turnt 

all: $(TARGET_TASKS)

$(TARGET_TASKS): $(SAVEDIR)/%: $(INPUTDIR)/%.bril $(SAVEDIR)
	@ echo "Running analysis on $< \n" | tee -a $(SAVEDIR)/run.log
	@ rm -rf $(SAVEDIR)/tmp
	@ mkdir -p $(SAVEDIR)/tmp
	python dom_analysis.py --save-dir $@ $< | tee $(SAVEDIR)/tmp/run.log;
	@ cp $(SAVEDIR)/tmp/run.log $@/
	@ cat $@/run.log | tee -a $(SAVEDIR)/run.log
	@ rm -rf $(SAVEDIR)/tmp
	@ echo "\n\n" | tee -a $(SAVEDIR)/run.log

# run the turnt test suite. Make sure result is same as the golden expected
turnt:
	turnt -e dom_analysis $(BRIL_FILES)

$(SAVEDIR):
	@ mkdir -p $(SAVEDIR)

clean:
	-@ rm -rf $(SAVEDIR)
