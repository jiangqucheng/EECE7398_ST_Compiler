temp:
	clang -emit-llvm -S -o - temp.c

pass-plugin:
	clang -fpass-plugin=llvm-pass-skeleton/build/skeleton/SkeletonPass.so temp.c
