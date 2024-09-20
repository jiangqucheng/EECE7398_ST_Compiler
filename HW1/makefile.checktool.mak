# List of required tools
REQUIRED_TOOLS = deno bril2json bril2txt brili ts2bril

# Check if each tool in the list exists
check-tools:
	@$(foreach tool, $(REQUIRED_TOOLS), \
		$(if $(shell command -v $(tool) 2> /dev/null), \
			echo "Checking for $(tool): Found", \
			(echo "Error: $(tool) is not installed!" && exit 1) || exit 1) \
	;)
	@echo "All tools are available!"
