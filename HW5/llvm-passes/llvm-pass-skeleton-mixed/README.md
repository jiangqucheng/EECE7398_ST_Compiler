# llvm-pass-skeleton

A completely useless LLVM pass.
It's for LLVM 17.

Build:
```bash
$ cd llvm-pass-skeleton
$ mkdir build
$ cd build
$ cmake ..
$ make
$ cd ..
```

Run:
```bash
$ clang -fpass-plugin=`echo build/skeleton/SkeletonPass.*` something.c
```
