# Command-Line Text Processing

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Utilize stream editors (`sed`) and pattern scanners (`awk`) for rapid text manipulation.
    - Implement complex text transformations using Perl and Python one-liners.
    - Apply regular expressions to identify and modify patterns across multiple files.
    - Select the appropriate tool based on the complexity of the task and available system environment.

Text processing is a fundamental skill for system administration and DevOps engineering. Much of the configuration and logging in Unix-like systems is stored in plain text, making the ability to surgically edit files from the command line essential for efficiency and automation.

While full-featured text editors are suitable for manual changes, "one-liners"—single commands that perform complex operations—allow for the automation of repetitive tasks across thousands of files. This capability is typically achieved through a combination of specialized stream editors and general-purpose programming languages executed in a condensed form.

## Fundamental Tools for Text Processing

The Linux ecosystem provides several utilities designed for different levels of text manipulation, ranging from simple character translation to complex pattern matching.

### Stream Editing with sed

The `sed` (stream editor) utility is used for performing basic text transformations on an input stream. It is most commonly used for search-and-replace operations.

The basic syntax for substitution is:
`sed 's/regexp/replacement/flags' filename`

Common flags include `g` (global, replacing all occurrences on a line) and `-i` (in-place, modifying the file directly).

### Pattern Scanning with awk

`awk` is a complete programming language designed for processing data in columns (fields). It is particularly effective for log analysis and report generation.

By default, `awk` treats whitespace as the field separator. To change the separator (e.g., to a comma for CSV files), the `-F` flag is used.

### Character Translation with tr

The `tr` (translate) utility operates at the character level. It is used for deleting characters, squeezing repeated characters, or replacing one set of characters with another. Unlike `sed` and `awk`, `tr` does not support regular expressions.

## Advanced One-Liner Techniques

When the requirements exceed the capabilities of simple stream editors, general-purpose languages like Perl and Python can be invoked as one-liners.

### Perl for Complex Regular Expressions

Perl was designed specifically for text processing and supports advanced regular expression features, such as non-greedy matching and look-aheads, which are not available in standard `sed`.

The `-pe` flags are commonly used: `-p` creates a loop that prints every line, and `-e` indicates that the following string is the code to execute.

### Python for Structured Logic

Python provides a more readable syntax for tasks that require logic beyond a simple substitution, such as conditional replacements or interacting with the file system via the `os` and `glob` modules.

Python one-liners are executed using the `-c` (command) flag.

## Practical Implementation Patterns

The following patterns represent common administrative tasks implemented across different toolsets.

### Whitespace and Formatting Cleanup

Removing trailing whitespace is a common requirement for maintaining clean configuration files and avoiding git diff noise.

Perl implementation:

```perl
perl -lpe 's/\s*$//' FILENAME
```

Python implementation:

```bash
python3 -c "import sys; [print(line.rstrip()) for line in sys.stdin]" < FILENAME
```

Shell (sed) implementation:

```bash
sed -i 's/[[:space:]]*$//' FILENAME
```

Shell (awk) implementation:

```bash
awk '{sub(/[[:space:]]*$/, ""); print}' FILENAME
```

### Character and String Replacement

Replacing specific characters, such as correcting quotation marks in markdown files, can be performed across multiple files simultaneously.

Perl implementation:

```perl
perl -i -p -e "s/'/'/g;" *.md
```

Shell (sed) implementation:

```bash
sed -i "s/'/'/g" *.md
```

Shell (awk) implementation:

```bash
awk '{gsub(/\'/\', \"'\"); print}' *.md
```

Python implementation:

```bash
python3 -c "import glob, os; [open(f, 'w').write(open(f).read().replace(\"'\", \"'\")) for f in glob.glob('*.md')]"
```

### Line Ending Normalization

Files moved between Windows and Linux environments often contain carriage return characters (`\r`), appearing as `^M` in some editors. These must be removed to ensure script compatibility.

Perl implementation:

```perl
perl -p -i -e 's/\r\n$/\n/g' FILENAME
```

Shell (tr) implementation:

```bash
tr -d '\r' < FILENAME > FILENAME.tmp && mv FILENAME.tmp FILENAME
```

Shell (awk) implementation:

```bash
awk '{gsub(/\r/, ""); print}' FILENAME
```

Python implementation:

```bash
python3 -c "import sys; [print(line.replace('\r\n', '\n'), end='') for line in sys.stdin]" < FILENAME
```

!!! tip "Summary Checklist"

    - [ ] Identified the appropriate tool based on the task (tr for characters, sed for lines, awk for columns).
    - [ ] Verified the regular expression pattern against a test string.
    - [ ] Used the `-i` flag for in-place edits only after verifying the output.
    - [ ] Handled line ending differences (CRLF vs LF) using `tr` or `sed`.
    - [ ] Applied the correct language identifier to code blocks.

!!! note "Exercise 1: Basic String Replacement"

    **Task**: Create a text file containing the word "ENVIRONMENT=development" on multiple lines. Use `sed` to change all occurrences to "ENVIRONMENT=production".
    **Goal**: Master basic search-and-replace operations.

!!! note "Exercise 2: Column Extraction"

    **Task**: Use `awk` to process the output of the `ls -l` command. Extract only the file size (5th column) and the filename (9th column) for all files in the current directory.
    **Goal**: Practice field-based data extraction.

!!! note "Exercise 3: Multi-file Pattern Update"

    **Task**: Write a Python one-liner that finds all `.txt` files in a directory and replaces every occurrence of the word "TODO" with "COMPLETED".
    **Goal**: Implement a multi-file update logic using Python's `glob` and `os` modules.
