# Velvet Programing Lanugage
### Install
###### build from source
for windows:

for linux/unix/macos

###### install velvet
for windows

for linux/unix/macos

## About

Velvet is a high-performance language with simple syntax.

## Features
- Symbolic syntax (~vars, !funcs, ?if, *loops)
- Inline other languages (#lang { code })
- Macros, async, match, patterns, modules, decorators
- C-like performance via Zig backend
- Easy scripting like Python/Ruby

## Setup
- Rust: cargo build
- Python: poetry install
- Zig: zig build

## Usage
- weave build [project]
- vel repl

## BNF Grammar
See velvet_parser.py for detailed BNF.

## IR Format
JSON with deps, imports, nodes (var, func, etc.), inline.

## Libraries
library.weave format: name > url @version
