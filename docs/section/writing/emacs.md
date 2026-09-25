# GNU Emacs: The Extensible Text Editor

!!! info "Learning Objectives"
    - Understand the history, philosophy, and extensibility of the GNU Emacs editor.
    - Use essential key-bindings for navigation, file management, and text manipulation.
    - Implement and utilize recording macros to automate repetitive data-cleaning tasks.
    - Configure and operate within Major Modes, with a focus on Python and LaTeX environments.
    - Integrate Emacs with the system terminal and external toolchains like LatexMk.

Emacs is an extensible, customizable environment that functions as a Lisp interpreter. Originating from the MIT AI Lab's Incompatible Timesharing System (ITS) as a collection of macros for editing, the name Emacs is an abbreviation for Editor MACroS. While the original version was a set of macros, the modern version rewritten in 1984 evolved into a platform that allows users to modify almost every aspect of the editor's behavior while it is running.

The extensibility of Emacs lies in its philosophy. By using Emacs Lisp (Elisp), users can create new commands, automate complex workflows, and integrate disparate tools into a single interface. This makes Emacs suitable for data scientists, researchers, and developers who require control over their text-processing environment.

## Documentation and Learning Resources

Because of its vast feature set, Emacs has a steep learning curve. The following official resources are recommended for structured learning:

- [GNU Emacs Manual](https://www.gnu.org/software/emacs/manual/html_node/emacs/index.html): The guide to all features.
- [An Introduction to Programming in Emacs Lisp](https://www.gnu.org/software/emacs/manual/html_node/eintr/index.html): For those wanting to extend Emacs.
- [Emacs Lisp Reference Manual](https://www.gnu.org/software/emacs/manual/html_node/elisp/index.html): Technical specifications for Elisp.
- [Other Emacs Manuals](https://www.gnu.org/software/emacs/manuals/): Additional specialized guides.
- [Emacs Tour](https://www.gnu.org/software/emacs/tour/): A high-level overview of the editor's capabilities.

For a condensed reference, the official [Emacs Reference Card](https://www.gnu.org/software/emacs/refcards/pdf/refcard.pdf) provides essential commands.

## Essential Key-bindings and Notation

Emacs uses a unique notation for its keyboard shortcuts. Most commands are combinations of modifier keys and characters.

### Notation Guide

| Key | Description |
| :- | :- |
| `C` | Control key |
| `M` | Meta key (usually `Esc` or `Alt`) |

### Emergency and Correction Commands

When navigating a complex editor, it is common to press a prefix key by mistake. Use these commands to recover:

- `C-g` (Cancel): Use this to cancel a command that is prompting for input (e.g., "Find file: ...") or to stop a long-running operation.
- `C-/` (Undo): Reverts the last modification made to the current buffer.

### Core Command Reference

The following table summarizes essential commands for daily usage.

| Category | Key | Description |
| :- | :- | :- |
| **Saving and Exiting** | `C-x C-w` | Write the current buffer to a file |
| | `C-x C-s` | Save the buffer and exit Emacs |
| **Basic Cursor** | `C-f` | Move forward one character |
| | `C-n` | Move to the next line |
| | `C-b` | Move back one character |
| | `C-p` | Move to the previous line |
| **Contextual Move** | `C-a` | Move to the beginning of the line |
| | `C-e` | Move to the end of the line |
| | `M-f` | Move forward one word |
| | `M-b` | Move back one word |
| | `M-v` | Move to the previous screen |
| | `C-v` | Move to the next screen |
| | `M-<` | Jump to the beginning of the buffer |
| | `M->` | Jump to the end of the buffer |
| | `M-a` | Move to the previous sentence |
| | `M-e` | Move to the next sentence |
| **Navigation** | `M-g g` | Jump to a specified line number |
| **Search and Replace** | `C-s` | Incremental search forward |
| | `C-r` | Incremental search backward |
| | `M-%` | Query replace (interactive find and replace) |
| **Text Manipulation** | `C-k` | Kill (cut) the line from the cursor to the end |
| | `C-y` | Yank (paste) the last killed text |

## Automation with Macros

Emacs allows the recording and replaying of a sequence of keystrokes. This is applicable for data science tasks and cleaning datasets where the pattern of editing is repetitive.

### Recording and Playback

Macros capture a series of edits and apply them to multiple lines.

| Key | Description |
| :- | :- |
| `M-x (` | Start recording a macro |
| `M-x )` | Stop recording the macro |
| `M-x e` | Play back the macro once |
| `M-5 C-x e` | Play back the macro 5 times |

### Practical Example: Data Cleaning

Given a list of items in a CSV-like format with unwanted quotes:
`"Item 1", "Item 2", "Item 3"`

To remove quotes:

1. Place the cursor at the first quote.
2. Start recording (`M-x (`).
3. Delete the quote, move to the next quote, delete it, and move to the start of the next line.
4. Stop recording (`M-x )`).
5. Use `M-x e` to clean subsequent lines.

## Major and Minor Modes

Emacs uses "Modes" to customize behavior based on the file type or user needs.

### Major Modes

Every buffer has one associated Major Mode. It determines the syntax highlighting, indentation rules, and key bindings for that specific file type. Major modes are typically activated automatically based on the file extension (e.g., `.py` activates `python-mode`).

| Command | Description |
| :- | :- |
| `M-x python-mode` | Activates the environment for editing Python files |
| `M-x auto-fill-mode` | Automatically wraps lines that exceed 70 characters |
| `M-x flyspell-mode` | Highlights misspelled words in real-time |

### Org Mode

Org Mode transforms the editor into a tool for note-taking, project planning, and TODO list management. Community tutorials are available online.

## Specialized Workflows

### Programming Python with Emacs

Emacs provides built-in syntax highlighting for Python. The following extensions are available:

- **Auto-completion**: The [emacs-jedi](https://github.com/tkf/emacs-jedi) package provides completion and analysis for Python code.
- **Guides**: Refer to [Real Python's Emacs Guide](https://realpython.com/blog/python/emacs-the-best-python-editor/) and the [EmacsWiki Python page](https://www.emacswiki.org/emacs/PythonProgrammingInEmacs).

### Emacs in the Terminal

Emacs can be used in remote environments without a graphical window system.

- **Non-Window Mode**: Run `emacs -nw` to start Emacs directly in the terminal.
- **Bash Integration**: Enable Emacs-style shortcuts in the Bash shell:

```bash
set -o emacs
```

### LaTeX and Emacs Integration

Emacs has native support for LaTeX, which can be enhanced through specialized packages. See the [EmacsWiki LaTeX page](https://www.emacswiki.org/emacs/LaTeX).

- **Spell Checking**: Use `M-x flyspell-mode` for real-time corrections.
- **Predictive Text**: Use [Predictive Mode](https://www.emacswiki.org/emacs/PredictiveMode) to speed up LaTeX command entry.
- **Other Tools**: Tools like `preview-latex` and `whizzy-tex` are available.
- **Compilation Workflow**: Use **LatexMk**.

#### Using LatexMk

LatexMk automatically compiles a document and updates the PDF when the source is changed. See the [EmacsWiki LatexMk page](https://www.emacswiki.org/emacs/LatexMk).

1. Run `latexmk` in one terminal window.
2. Edit the `.tex` file in an Emacs window.
3. View the resulting PDF in a viewer like Skim.

This creates a feedback loop with local control.

!!! info "Summary Checklist"
    - Configured basic navigation using `C` and `M` modifiers.
    - Utilized `C-g` and `C-/` for error recovery and undoing changes.
    - Applied `C-k` and `C-y` for efficient text manipulation.
    - Implemented a recording macro to automate a repetitive data-cleaning task.
    - Activated `python-mode` and `flyspell-mode` for enhanced coding and writing.
    - Integrated Emacs with a remote terminal using the `-nw` flag.
    - Established a LaTeX compilation loop using LatexMk and a PDF viewer.

## Assignments

!!! note "Assignment 1: Basic Navigation"
    Create a text file with 20 lines of random text. Practice moving to the beginning of the buffer, jumping to line 10 using `M-g g`, and moving to the end of the buffer.

!!! note "Assignment 2: Macro Automation"
    Create a file containing a list of 10 names and emails in the format: `Name <email@example.com>`. Use a macro to remove the `<` and `>` characters and the name, leaving only the email addresses.

!!! note "Assignment 3: LaTeX Environment"
    Install `latexmk` on your system. Create a simple LaTeX document in Emacs, launch `latexmk` in a separate terminal, and verify that the PDF updates automatically every time you save the file (`C-x C-s`).

## Self-Evaluation

??? note "Can you navigate a buffer quickly using both character-level and line/word-level movements?"
    Yes, using shortcuts like `C-f`/`C-b` for characters, `C-n`/`C-p` for lines, and `M-f`/`M-b` for words.

??? note "Do you know how to recover from an accidental prefix key press or stop a frozen operation?"
    Yes, by using `C-g` to cancel the current command or stop long-running operations.

??? note "Can you record a macro to automate a repetitive editing task and play it back multiple times?"
    Yes, by using `M-x (` to start recording, `M-x )` to stop, and `M-x e` (or `M-number C-x e`) for playback.

??? note "Do you understand the difference between Major and Minor modes and how to activate them?"
    Yes. Major modes define the primary behavior for a file type (e.g., `python-mode`), while minor modes provide additional optional features (e.g., `flyspell-mode`).

??? note "Are you able to run Emacs in a terminal environment and integrate it with Bash?"
    Yes, by using the `emacs -nw` flag and executing `set -o emacs` in the Bash shell.

??? note "Have you successfully set up a LaTeX compilation loop using LatexMk?"
    Yes, by running `latexmk` in a terminal and editing the source file in Emacs to trigger automatic PDF updates.
