# EECE7398_ST_Compiler


## Setup Env
### Init history
```bash
git submodule add https://github.com/sampsyo/bril.git
conda create -n course-eece7398-st-compiler python=3.10.14
conda install conda-forge::deno
conda install flit
pip install turnt
# dump venv
conda env export > environment.yml
```

### bril interpreter, ts2bril
```bash
cd bril
deno install brili.ts 
deno install --allow-env --allow-read ts2bril.ts
```
> Verification
> ```bash
> ❯ which ts2bril
> /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/ts2bril
> ❯ which brili
> /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/brili
> ❯ brili < test/print/add.json
> 3
> ❯ brili -p < test/print/add.json
> 3
> total_dyn_inst: 4
> ```

### bril2json, bril2txt
```bash
cd bril-txt
flit install --symlink
```
> Verification
> ```bash
> ❯ which bril2json
> /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/bril2json
> ❯ which bril2txt
> /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/bril2txt
> ❯ bril2txt < test/print/add.json
> @main {
>   v0: int = const 1;
>   v1: int = const 2;
>   v2: int = add v0 v1;
>   print v2;
> }
> ❯ bril2txt < test/print/add.json | bril2json
> {
>   "functions": [
>     {
>       "instrs": [
>           ...
>       ],
>       "name": "main"
>     }
>   ]
> }
> ❯ cat test/print/add.json
> {
>   "functions": [
>     {
>       "name": "main",
>       "instrs": [
>         { "op": "const", "type": "int", "dest": "v0", "value": 1 },
>         { "op": "const", "type": "int", "dest": "v1", "value": 2 },
>         { "op": "add", "type": "int", "dest": "v2",
>           "args": ["v0", "v1"] },
>         { "op": "print", "args": ["v2"] }
>       ],
>       "args": []
>     }
>   ]
> }
> ```

### Brench (HW2)
```bash
cd brench
flit install --symlink
```
> Verification
> ```bash
> ❯ which brench
> /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/brench
> ```

### Start Env
```bash
conda activate course-eece7398-st-compiler
```

