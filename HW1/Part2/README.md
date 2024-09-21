# Part 2: Implementing a Bril Analyzer/Transformer

In the second part, I created 2 tools to analyze and transform Bril programs. The tools are implemented in Python and are designed to modify Bril code by adding print statements, one adds before each `jmp`/`br` instruction, and the other adds print after each `add`/`fadd` instruction.

## Stub-Analyzer Impl Details
The tool reads Bril programs in JSON format, add additional print statements before or after specific instruction. The results are stored back into json format and dump to standard output.

The source code is located in the `Part2/analyzer` directory. 

### `pin_stub_print_add`

This stub program processes a Bril program, adding print instructions after each `add` or `fadd` operation. The script consists of three main functions: `is_add_or_fadd`, `add_print_after_add_or_fadd`, and `main`.

The `is_add_or_fadd` function checks if a given operation is either `add` or `fadd`. It takes a single parameter `op` of type `str` and returns a boolean value. If the operation is either `add` or `fadd`, the function returns `True`; otherwise, it returns `False`. This function is used to identify the specific operations in the Bril program that require additional print instructions.

The `add_print_after_add_or_fadd` function modifies a given Bril program by adding a print instruction after each `add` or `fadd` instruction. The function takes a single parameter `bril`, which is a dictionary representing the Bril program. It iterates over each function in the Bril program and then over each instruction within those functions. If an instruction is identified as an `add` or `fadd` operation using the `is_add_or_fadd` function, a new print instruction is created and appended immediately after the original instruction. This print instruction includes the arguments and the destination of the `add` or `fadd` operation. The modified list of instructions is then assigned back to the function. The function returns the modified Bril program.

The `main` function serves as the entry point of the script. It reads a Bril program from an input file specified as a command-line argument, processes the program using the `add_print_after_add_or_fadd` function, and writes the modified program to the standard output. The function first checks if the correct number of command-line arguments is provided. If not, it prints a usage message and exits. It then reads the input file, parses it as a JSON object, and processes it to add the print instructions. Finally, it writes the modified Bril program to the standard output in a formatted JSON structure.

The script is designed to be run from the command line, with the input file specified as an argument. When executed, it reads the Bril program, modifies it by adding print instructions after each `add` or `fadd` operation, and outputs the modified program. This can be useful for debugging or analyzing the behavior of Bril programs by providing additional runtime information.

### `pin_stub_print_jmp`

This stub program processes a Bril program, adding print instructions before each branch or jump instruction. The script consists of three main functions: `is_branch_or_jump`, `add_print_before_branch_or_jump`, and `main`.

The `is_branch_or_jump` function checks if a given operation is a branch or jump instruction. It takes a single parameter `op` of type `str` and returns a boolean value. If the operation is either "jmp" or "br", the function returns `True`; otherwise, it returns `False`. This function is used to identify specific operations in the Bril program that require additional print instructions.

The `add_print_before_branch_or_jump` function modifies a given Bril program by adding a print instruction before each branch or jump instruction. The function takes a single parameter `bril`, which is a dictionary representing the Bril program. It iterates over each function in the Bril program and then over each instruction within those functions. If an instruction is identified as a branch or jump operation using the `is_branch_or_jump` function, a new print instruction is created and appended immediately before the original instruction. This print instruction includes the arguments from the previous instruction if available. The modified list of instructions is then assigned back to the function. The function returns the modified Bril program.

The `main` function serves as the entry point of the script. It reads a Bril program from an input file specified as a command-line argument, processes the program using the `add_print_before_branch_or_jump` function, and writes the modified program to the standard output. The function first checks if the correct number of command-line arguments is provided. If not, it prints a usage message and exits. It then reads the input file, parses it as a JSON object, and processes it to add the print instructions. Finally, it writes the modified Bril program to the standard output in a formatted JSON structure.

The script is designed to be run from the command line, with the input file specified as an argument. When executed, it reads the Bril program, modifies it by adding print instructions before each branch or jump operation, and outputs the modified program. This can be useful for debugging or analyzing the behavior of Bril programs by providing additional runtime information.

## `turnt` Verification

For implementation details, you can check the `makefile` and `turnt.toml` in current folder. The `makefile` contains targets for running the tests using Turnt, while the `turnt.toml` file specifies the command to be tested and any additional configuration options.

### Stub-analyzer program selection
As you can see in `makefile`, the selection of which Stub-analyzer program is controled by `turnt -a $$stub ...`. Using this method, it is much easier to manage different stub-analyzer program once they have a same interface and program naming strategy. 

### `*.stub-out` check

This `*.stub-out` check task uses `turnt` toolset to test the direct generated bril json program output of each analyzer. Comparing the bril program of `*.bril.json` and `*.bril.stub-out`, you can see there's some additional lines of operation instructions are added to the program, depending on the selected stub program. The focus of this check task is to verify that stub program generates the correct bril script that is able to run. This check is triggered by `turnt -e pin_stub_print ...` from `makefile`. 

### `*.exe-out` check

This `*.exe-out` checks the execution output of the modified bril script that is passing throw the stub-analyzer. This check is triggered by `turnt -e pin_stub_print-brili ...` from `makefile`. 



# Homework Compliance Check Requirement

## Test methods, inputs, and quantitative results

### Testing Methods and Inputs

## Testing Methods and Inputs
I tested the tool with various Bril programs to ensure it correctly counted add instructions and inserted print statements. I created a set of test programs, including `add.bril` and `euler.bril`, which included multiple arithmetic and control flow instructions.

Automated Testing with Turnt: I used turnt to automate the testing process. Each test case was run through the analyzer, and the output was compared against saved outputs.

```bash
make turnt
```

### Quantitative Results
For each demo bril application and each stub-analyzer, I recorded the stub-analyzer output of the `STDERR` channel, which is the log generated during stub-analyzer process. The results are summarized below:

```log
Stub-analyzer[jmp] on [euler.bril.json] : 3 op(s) match 
Stub-analyzer[jmp] on [add.bril.json] : 0 op(s) match 
Stub-analyzer[add] on [euler.bril.json] : 2 op(s) match 
Stub-analyzer[add] on [add.bril.json] : 1 op(s) match 
```

### Full test log
```bash
❯ cd EECE7398_ST_Compiler/HW1/Part2
❯ make turnt
🧪 Running turnt tests...
1..2
ok 1 - demo/pin_stub_print_jmp/euler.bril.json pin_stub_print-brili
ok 2 - demo/pin_stub_print_jmp/add.bril.json pin_stub_print-brili
1..2
ok 1 - demo/pin_stub_print_add/euler.bril.json pin_stub_print-brili
ok 2 - demo/pin_stub_print_add/add.bril.json pin_stub_print-brili
1..2
ok 1 - demo/pin_stub_print_jmp/euler.bril.json pin_stub_print
ok 2 - demo/pin_stub_print_jmp/add.bril.json pin_stub_print
1..2
ok 1 - demo/pin_stub_print_add/euler.bril.json pin_stub_print
ok 2 - demo/pin_stub_print_add/add.bril.json pin_stub_print
❯ 
❯ make run
💡 Run all Stub-analyzer

🚀 Running Stub-analyzer[jmp] on [euler.bril.json] ...
Added print instruction before {'op': 'br', 'args': ['v3'], 'labels': ['then.0', 'else.0']}.
Added print instruction before {'op': 'br', 'args': ['v5'], 'labels': ['for.body.1', 'for.end.1']}.
Added print instruction before {'op': 'jmp', 'args': [], 'labels': ['for.cond.1']}.


🚀 Running Stub-analyzer[jmp] on [add.bril.json] ...


🚀 Running Stub-analyzer[add] on [euler.bril.json] ...
Added print instruction after {'op': 'fadd', 'dest': 'v11', 'type': 'float', 'args': ['v9', 'v10']}.
Added print instruction after {'op': 'fadd', 'dest': 'v14', 'type': 'float', 'args': ['v12', 'v13']}.


🚀 Running Stub-analyzer[add] on [add.bril.json] ...
Added print instruction after {'args': ['v0', 'v1'], 'dest': 'v2', 'op': 'add', 'type': 'int'}.


❯ 
❯ make diff
🧐 Show diff before & after...
🔍 [euler.bril.json] vs [euler.bril.stub-out]
114a115,120
>           "op": "print",
>           "args": [
>             "v3"
>           ]
>         },
>         {
267a274,279
>           "op": "print",
>           "args": [
>             "v5"
>           ]
>         },
>         {
367a380,385
>           ]
>         },
>         {
>           "op": "print",
>           "args": [
>             "i"
🔍 [add.bril.json] vs [add.bril.stub-out]
🔍 [euler.bril.json] vs [euler.bril.stub-out]
331a332,339
>           "op": "print",
>           "args": [
>             "v9",
>             "v10",
>             "v11"
>           ]
>         },
>         {
359a368,375
>           ]
>         },
>         {
>           "op": "print",
>           "args": [
>             "v12",
>             "v13",
>             "v14"
🔍 [add.bril.json] vs [add.bril.stub-out]
26a27,34
>           "op": "print",
>           "args": [
>             "v0",
>             "v1",
>             "v2"
>           ]
>         },
>         {
```

## Challenges
No specific challenge occur in this part. 