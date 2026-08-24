---
title: "Text Processing One-liners"
---

!!! info "Learning Outcomes"
    - Understand the role of Perl, Python, and Shell in system administration and text processing.
    - Apply one-liners from different languages to perform common file manipulation tasks.
    - Compare and utilize regular expressions and stream editors to efficiently edit files from the command line.

# Text Processing One-liners

Text processing is a core skill for system administrators. While Perl was historically the gold standard for this, modern environments often provide Python or powerful shell utilities like `sed` and `awk` to achieve similar results.

Here are some useful one-liner commands for common tasks.

## Strip trailing whitespace from a file

**Perl:**
```perl
perl -lpe 's/\s*$//' FILENAME
```

**Python:**
```bash
python3 -c "import sys; [print(line.rstrip()) for line in sys.stdin]" < FILENAME
```

**Shell (sed):**
```bash
sed -i 's/[[:space:]]*$//' FILENAME
```

**Shell (awk):**
```bash
awk '{sub(/[[:space:]]*$/, ""); print}' FILENAME
```

## Replace a string (e.g., wrong quotes)

**Perl:**
```perl
perl -i -p -e "s/'/'/g;" *.md
```

**Shell (sed):**
```bash
sed -i "s/'/'/g" *.md
```

**Shell (awk):**
```bash
awk '{gsub(/\'/\', \"'\"); print}' *.md
```

**Python:**
```bash
python3 -c "import glob, os; [open(f, 'w').write(open(f).read().replace(\"'\", \"'\")) for f in glob.glob('*.md')]"
```


## Remove `^M` (carriage returns) from file

**Perl:**
```perl
perl -p -i -e 's/\r\n$/\n/g' FILENAME
```
**Shell (tr):**
```bash
tr -d '\r' < FILENAME > FILENAME.tmp && mv FILENAME.tmp FILENAME
```

**Shell (awk):**
```bash
awk '{gsub(/\r/, ""); print}' FILENAME
```

**Python:**
```bash
python3 -c "import sys; [print(line.replace('\r\n', '\n'), end='') for line in sys.stdin]" < FILENAME
```
