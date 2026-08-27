# Linux Shell
---  

!!! info "Learning Outcomes"
    - Be able to know the basic commands to work in a [Linux]{.index} terminal.  
    - Get familiar with Linux commands.  

*The Linux documentation has been improved but nothing has been removed.*

In this chapter we introduce you to a number of useful shell commands. You may ask:

> “Why is he so keen on telling me all about shells when I already have a beautiful GUI?”

You will soon learn that a GUI may not be suitable when you need to manage **10, 100, 1 000, 10 000…** virtual machines. A command‑line interface can be *much* simpler and allows you to script repetitive tasks.

## History
LINUX is a re‑implementation by the community of UNIX, which was developed in 1969 by **Ken Thompson** and **Dennis Ritchie** of Bell Laboratories and originally written in C. An important part of UNIX is the *kernel*, which allows the software to talk to the hardware.

In 1991 **Linus Torvalds** started developing a Linux kernel that was initially targeted for PCs. This made it possible to run Linux on laptops and, over time, it became a full operating‑system replacement for UNIX.

## Shell
One of the most important features for us is the ability to access the computer through a *shell*. The shell is typically run in a **terminal** and allows interaction with the computer via command‑line programs.

There are many good tutorials that explain why one needs a Linux shell and not just a GUI. Randomly we picked the first one that came up with a Google query. This is **not** an endorsement for the material we point to, but it may be a worthwhile read for someone with no experience in shell programming [@www‑learning‑shell]:

<http://linuxcommand.org/lc3_learning_the_shell.php>

You are, of course, welcome to use other resources that suit you best. We will, however, summarize a number of useful commands in table form—some of which you may also find in a **RefCard** [@www‑linux‑cheatsheet]:

<http://www.cheat-sheets.org/#Linux>

## Useful Commands

We provide in the next sections a number of useful commands that you want to explore. For more information simply type `man` and the name of the command. If you find a useful command that is missing, please add it with a Git pull request.

### General and Help

<table style="width:100%; border-collapse:collapse;" border="1">
<thead>
<!-- Table‑wide header (optional) -->
<tr style="background:#e0e0e0;">
    <th style="width:30%; text-align:left;">Command</th>
    <th style="width:70%; text-align:left;">Description</th>
</tr>
</thead>

<tbody>

<!-- ---------- General and Help ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">General and Help</th>
</tr>
<tr><td>`man command`</td><td>manual page for the command</td></tr>
<tr><td>`apropos text`</td><td>list all commands that contain *text*</td></tr>
<tr><td>`history`</td><td>list previously executed commands</td></tr>
<tr><td>`clear`</td><td>clear the terminal screen</td></tr>
<tr><td>`exit`</td><td>exit the current shell</td></tr>

<!-- ---------- File and Directory Management ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">File and Directory Management</th>
</tr>
<tr><td>`ls`</td><td>Directory listing</td></tr>
<tr><td>`ls -lisa`</td><td>list details (long format, inode, size, all)</td></tr>
<tr><td>`tree`</td><td>list the directories in graphical form</td></tr>
<tr><td>`cd *dirname*`</td><td>Change directory to *dirname*</td></tr>
<tr><td>`mkdir *dirname*`</td><td>create the directory</td></tr>
<tr><td>`rmdir *dirname*`</td><td>delete an empty directory</td></tr>
<tr><td>`pwd`</td><td>print working directory</td></tr>
<tr><td>`rm *file*`</td><td>remove the file</td></tr>
<tr><td>`rm -rf *dir*`</td><td>remove directory and its contents recursively</td></tr>
<tr><td>`cp *a* *b*`</td><td>copy file *a* to *b*</td></tr>
<tr><td>`mv *a* *b*`</td><td>move/rename file *a* to *b*</td></tr>
<tr><td>`touch *file*`</td><td>create an empty file or update its timestamp</td></tr>
<tr><td>`find *path* -name *pattern*`</td><td>search for files by name</td></tr>
<tr><td>`mount /dev/cdrom /mnt/cdrom`</td><td>mount a filesystem from a CD‑ROM to <code>/mnt/cdrom</code></td></tr>

<!-- ---------- File Content and Viewing ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">File Content and Viewing</th>
</tr>
<tr><td>`cat *a*`</td><td>print content of file *a*</td></tr>
<tr><td>`cat -n *filename*`</td><td>print content with line numbers</td></tr>
<tr><td>`less *a*`</td><td>paged view of file *a*</td></tr>
<tr><td>`head`</td><td>display the first 10 lines of a file</td></tr>
<tr><td>`head *a*`</td><td>same as above, explicitly naming the file</td></tr>
<tr><td>`head -5 *a*`</td><td>display first 5 lines of file *a*</td></tr>
<tr><td>`tail -5 *a*`</td><td>display last 5 lines of file *a*</td></tr>
<tr><td>`tail *a*`</td><td>display last 10 lines of file *a*</td></tr>
<tr><td>`tail -f *a*`</td><td>follow file *a* in real‑time (useful for logs)</td></tr>
<tr><td>`od -c *a*`</td><td>dump file *a* in octal/char format</td></tr>
<tr><td>`du -hs .`</td><td>show, in human‑readable form, the space used by the current directory</td></tr>
<tr><td>`df -h`</td><td>show details of the disk file system</td></tr>
<tr><td>`wc *filename*`</td><td>counts words, lines and bytes in a file</td></tr>
<tr><td>`sort *filename*`</td><td>sort the file</td></tr>
<tr><td>`uniq *filename*`</td><td>display only unique entries in the file</td></tr>
<tr><td>`find */ \[-name\] file‑name.txt*`</td><td>search the entire drive for a file named <code>file‑name.txt</code></td></tr>
<tr><td>`diff`</td><td>compare files line by line</td></tr>
<tr><td>`awk`</td><td>select particular records and perform operations</td></tr>
<tr><td>`sed`</td><td>stream editor used to perform basic text transformations</td></tr>

<!-- ---------- Text Processing and Search ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Text Processing and Search</th>
</tr>
<tr><td>`grep *pattern* *file*`</td><td>search for *pattern* in *file*</td></tr>
<tr><td>`grep -r *pattern* *dir*`</td><td>recursive search for *pattern* in *dir*</td></tr>
<tr><td>`grep -v *'word'* *filename*`</td><td>find all lines **without** *word*</td></tr>
<tr><td>`grep -R *text* .`</td><td>recursively search for *text* in the current directory tree</td></tr>
<tr><td>`sed *command* *file*`</td><td>filter and transform text</td></tr>
<tr><td>`awk *program* *file*`</td><td>pattern‑scanning and processing language</td></tr>
<tr><td>`sort *file*`</td><td>sort lines of *file*</td></tr>
<tr><td>`uniq *file*`</td><td>report or omit repeated lines</td></tr>
<tr><td>`wc *file*`</td><td>print newline, word, and byte counts</td></tr>
<tr><td>`cut -d *delim* -f *field* *file*`</td><td>extract specific fields from each line</td></tr>
<tr><td>`find . -name *.py`</td><td>find all files ending with <code>.py</code></td></tr>

<!-- ---------- Permissions and Ownership ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Permissions and Ownership</th>
</tr>
<tr><td>`chmod *mode* *file*`</td><td>change file mode bits (permissions)</td></tr>
<tr><td>`chown *user*:*group* *file*`</td><td>change file owner and group</td></tr>
<tr><td>`locate *filename*`</td><td>find the path of a file (uses a pre‑built index)</td></tr>
<tr><td>`chmod ug+rw *filename*`</td><td>give user and group read/write permissions</td></tr>
<tr><td>`chmod go-rwx *file*`</td><td>remove all permissions for group and others</td></tr>
<tr><td>`sudo *command*`</td><td>execute *command* as another user (usually root)</td></tr>
<tr><td>`su *user*`</td><td>switch to another user (default is root)</td></tr>

<!-- ---------- Process and System Monitoring ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Process and System Monitoring</th>
</tr>
<tr><td>`ps`</td><td>display a header line followed by processes that have controlling terminals</td></tr>
<tr><td>`ps aux`</td><td>list all running processes</td></tr>
<tr><td>`top`</td><td>display Linux processes in real‑time</td></tr>
<tr><td>`htop`</td><td>interactive process viewer (more user‑friendly than <code>top</code>)</td></tr>
<tr><td>`kill *pid*`</td><td>send a signal to process *pid* (default SIGTERM)</td></tr>
<tr><td>`kill -9 *pid*`</td><td>force‑kill process *pid* (SIGKILL)</td></tr>
<tr><td>`df -h`</td><td>report file‑system disk space usage in human‑readable format</td></tr>
<tr><td>`du -sh *dir*`</td><td>estimate file‑space usage of *dir*</td></tr>
<tr><td>`free -m`</td><td>display amount of free and used memory in MB</td></tr>
<tr><td>`uptime`</td><td>tell how long the system has been running</td></tr>
<tr><td>`time *command*`</td><td>measure how long *command* takes to run</td></tr>
<tr><td>`at`</td><td>queue commands for later execution (one‑time jobs)</td></tr>
<tr><td>`cron`</td><td>daemon that executes scheduled commands (periodic jobs)</td></tr>
<tr><td>`crontab`</td><td>manage the timetable for <code>cron</code> jobs</td></tr>
<tr><td>`dmesg`</td><td>display the kernel ring buffer (system messages)</td></tr>
<tr><td>`which`</td><td>locate a program file in the user’s PATH</td></tr>
<tr><td>`shutdown -h "shut down"`</td><td>shut down the computer</td></tr>

<!-- ---------- Networking ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Networking</th>
</tr>
<tr><td>`ping *host*`</td><td>send ICMP ECHO_REQUEST to *host*</td></tr>
<tr><td>`ssh *user*@*host*`</td><td>secure shell remote login</td></tr>
<tr><td>`scp *file* *user*@*host*:*path*`</td><td>secure copy (remote file copy)</td></tr>
<tr><td>`curl *url*`</td><td>transfer data from or to a server</td></tr>
<tr><td>`wget *url*`</td><td>non‑interactive network downloader</td></tr>
<tr><td>`ifconfig`</td><td>configure a network interface (deprecated; use <code>ip addr</code>)</td></tr>
<tr><td>`ip addr`</td><td>display/manipulate routing, devices, policy routing</td></tr>
<tr><td>`netstat -tulpn`</td><td>print network connections, listening ports, etc.</td></tr>
<tr><td>`hostname`</td><td>print name of current host system</td></tr>
<tr><td>`traceroute`</td><td>print the route packets take to a network host</td></tr>
<tr><td>`host`</td><td>DNS lookup utility</td></tr>
<tr><td>`whois`</td><td>Internet domain name and network‑number directory service</td></tr>
<tr><td>`dig`</td><td>DNS lookup utility (more powerful than <code>host</code>)</td></tr>

<!-- ---------- Archiving and Compression ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Archiving and Compression</th>
</tr>
<tr><td>`tar -cvf *archive.tar* *files*`</td><td>create a tar archive</td></tr>
<tr><td>`tar -xvf *archive.tar*`</td><td>extract a tar archive</td></tr>
<tr><td>`tar -zcvf *archive.tar.gz* *files*`</td><td>create a compressed tar archive (gzip)</td></tr>
<tr><td>`tar -zxvf *archive.tar.gz*`</td><td>extract a compressed tar archive (gzip)</td></tr>
<tr><td>`gzip *file*`</td><td>compress *file*</td></tr>
<tr><td>`gunzip *file.gz*`</td><td>uncompress *file.gz*</td></tr>
<tr><td>`zip -r *archive.zip* *dir*`</td><td>create a zip archive</td></tr>
<tr><td>`unzip *archive.zip*`</td><td>extract a zip archive</td></tr>
<tr><td>`rsync`</td><td>fast, flexible replacement for <code>rcp</code></td></tr>
<tr><td>`bzip2 *filename*`</td><td>compresses the file with block‑sorting</td></tr>
<tr><td>`bunzip2 *filename*`</td><td>uncompresses the file with block‑sorting</td></tr>

<!-- ---------- Terminal and Shell ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">Terminal and Shell</th>
</tr>
<tr><td>`history`</td><td>built‑in command to list past commands</td></tr>
<tr><td>`clear`</td><td>clears the terminal screen</td></tr>
<tr><td>`echo -n *string*`</td><td>write *string* to standard output without a trailing newline</td></tr>
<tr><td>`sleep`</td><td>suspends execution for a specified number of seconds</td></tr>
<tr><td>`date`</td><td>displays or sets date &amp; time (without arguments shows current date &amp; time)</td></tr>
<tr><td>`logout`</td><td>exit a login session</td></tr>
<tr><td>`exit`</td><td>exit the current shell (terminates any running jobs started from this shell)</td></tr>
<tr><td>`watch *command*`</td><td>run *command* repeatedly, showing updated output</td></tr>
<tr><td>`xargs`</td><td>build and execute command lines from STDIN</td></tr>
<tr><td>`uname`</td><td>print the operating system name</td></tr>
<tr><td>`set -o emacs`</td><td>switch the command‑line editing mode to Emacs‑style key bindings</td></tr>

<!-- ---------- User Management ---------- -->
<tr style="background:#f8f8f8;">
    <th colspan="2" style="text-align:center;">User Management</th>
</tr>
<tr><td>`who`</td><td>display a list of users currently logged on (login name, time, tty, host)</td></tr>
<tr><td>`whoami`</td><td>display the user's effective ID (same as <code>id -un</code>)</td></tr>
<tr><td>`users`</td><td>list the logged‑in users</td></tr>
<tr><td>`last`</td><td>show a reverse‑chronological listing of previous logins</td></tr>

</tbody>
</table>


## The `man` Command
On Linux you find a rich set of manual pages for **the** commands. Try to pick one and execute:

```bash
$ man ls
```

You will see something like this:

````text
LS(1)                     BSD General Commands Manual                    LS(1)

NAME
     ls -- list directory contents

SYNOPSIS
     ls [-ABCFGHLOPRSTUW@abcdefghiklmnopqrstuwx1] [file ...]

DESCRIPTION
     For each operand that names a file of a type other than directory,
     ls displays its name as well as any requested, associated
     information.  For each operand that names a file of type directory,
     ls displays the names of files contained within that directory,
     along with any requested, associated information.

     If no operands are given, the contents of the current directory are
     displayed.  If more than one operand is given, non‑directory operands
     are displayed first; directory and non‑directory operands are sorted
     separately and in lexicographical order.

     The following options are available:
     -@      Display extended attribute keys and sizes in long (-l) output.
     -1      (The numeric digit “one”.) Force output to be one entry per line.
     -A      List all entries except for . and ..  Always set for the super‑user.
     -a      Include directory entries whose names begin with a dot (.).

     ... (additional options omitted for brevity) ...
````

Feel free to explore any other manual page in the same way.

## Multi‑command Execution
You can chain commands in the shell:

* **Sequential execution** – run `command2` after `command1` finishes:

  ```bash
  command1; command2
  ```

* **Conditional execution** – run `command2` *only if* `command1` succeeds (`&&`) or fails (`||`):

  ```bash
  command1 && command2   # run command2 if command1 exits with status 0
  command1 || command2   # run command2 if command1 exits with non‑zero status
  ```

* **Background execution** – start a command and immediately get back the prompt:

  ```bash
  command1 &
  ```

## Keyboard Shortcuts
These shortcuts are handy when working in a Bash (or compatible) terminal. Many overlap with Emacs key bindings.

| Keys                | Description                                                            |
|---------------------|------------------------------------------------------------------------|
| **Up Arrow**        | Show the previous command (history navigation)                         |
| **Ctrl + z**        | Suspend the current foreground job (puts it in the background)        |
| —                   | Resume with `fg` (foreground) or `bg` (background)                    |
| **Ctrl + c**        | Send `SIGINT` – abort the current command                               |
| **Ctrl + l**        | Clear the screen (same as the `clear` command)                         |
| **Ctrl + a**        | Move cursor to the beginning of the line                                 |
| **Ctrl + e**        | Move cursor to the end of the line                                       |
| **Ctrl + k**        | Cut everything after the cursor (stores in the “kill ring”)            |
| **Ctrl + y**        | Paste the most recent kill‑ring entry (undo a cut)                      |
| **Ctrl + d**        | Log out of the current session (same effect as `exit` when at a prompt) |

## `.bashrc`, `.bash_profile` or `.zprofile`
The `man` command is your friend for learning the usage and options of any command.  
To avoid accidental deletions, you can make the `rm` and `mv` commands interactive by adding the following aliases to the appropriate startup file:

- **Bash (Linux/macOS):** `~/.bashrc` or `~/.bash_profile`  
- **Zsh (macOS, some Linux distros):** `~/.zprofile`

```bash
alias rm='rm -i'     # Prompt before removing files
alias mv='mv -i'     # Prompt before overwriting files
alias h='history'    # Shortcut for viewing command history
```

## Makefile
Makefiles allow developers to coordinate the execution of compilation, testing, packaging, or any other reproducible workflow. They are not limited to C/C++ projects; you can also use them for LaTeX builds, Docker image creation, cloud‑service deployment, etc.

*Example: a very simple Makefile for Docker*

```make
build:
    docker build -t myimage .
```

*Example: a LaTeX Makefile*

```make
PDF = document.pdf
SRC = document.tex

$(PDF): $(SRC)
    pdflatex $(SRC)

clean:
    rm -f *.aux *.log *.out $(PDF)
```

Key points:

* **Tabs, not spaces:** The command lines after a target must start with a **single TAB** character.  
* **Dependencies:** Targets can depend on other targets—`hallo: hello` runs `hello` first, then the commands of `hallo`.  
* **Variables:** Use `$(VAR)` syntax; they are defined with `VAR = value`.

For more examples see:

- Docker Makefiles: <http://jmkhael.io/makefiles-for-your-dockerfiles/>  
- LaTeX Makefiles: <https://github.com/cloudmesh/book/blob/master/Makefile>  
- Unix reference card (PDF): <http://www.cs.jhu.edu/~joanne/unixRC.pdf>

## `chmod` – Changing File Modes
The `chmod` command **changes the access permissions** for files and directories.

```bash
chmod [options] mode[,mode] file1 [file2 …]
```

### Options
| Option                | Description                                                            |
|-----------------------|------------------------------------------------------------------------|
| `-f`, `--silent`, `--quiet` | Suppress most error messages.                                    |
| `-v`, `--verbose`     | Explain each change as it is made.                                     |
| `-c`, `--changes`     | Report only when a file’s mode actually changes.                       |
| `--reference=RFILE`   | Apply the mode of *RFILE* to the target files.                         |
| `-R`, `--recursive`   | Apply changes recursively to all files/sub‑directories.                |
| `--help`              | Show a help message and exit.                                           |
| `--version`           | Show version information and exit.                                      |

### Understanding Modes
Permissions are expressed for three classes of users:

| Class   | Symbol | Meaning                              |
|---------|--------|--------------------------------------|
| Owner   | `u`    | The user that owns the file          |
| Group   | `g`    | Users that belong to the file’s group|
| Others  | `o`    | Everyone else                        |
| All     | `a`    | Shortcut for `u,g,o`                 |

For each class you can **add** (`+`), **remove** (`-`), or **set exactly** (`=`) one or more of the following permissions:

| Permission | Symbol | Meaning                                          |
|------------|--------|--------------------------------------------------|
| Read       | `r`    | Allows reading the file or listing a directory   |
| Write      | `w`    | Allows modifying the file or creating/deleting entries in a directory |
| Execute    | `x`    | Allows executing a file or entering a directory   |
| Execute only if directory | `X` | Execute permission is set only on directories (or on files that already have at least one execute bit) |
| Set‑UID/GID| `s`    | Set user ID or group ID on execution (requires `x` to be set as well) |
| Sticky bit | `t`    | Restricts deletion/renaming of files in a directory (e.g., `/tmp`) |
| **Special**| `u`/`g`/`o` | Use the existing permissions of user/group/others as a source for the new mode |

#### Examples
```bash
# Give user and group read/write permissions:
chmod ug+rw file.txt

# Remove execute permission for all, then add read for others:
chmod a-x,o+r file.txt

# Verbosely set the sticky bit on a directory:
chmod -v +t /shared
```

## `chown` – Changing Ownership
`chown` changes the **owner** and optionally the **group** of a file or directory.

```bash
chown [options] [owner][:[group]] file…
```

### Options
| Option               | Description                                          |
|----------------------|------------------------------------------------------|
| `-c`, `--changes`    | Report only when a change is made.                   |
| `-f`, `--silent`     | Suppress most error messages.                        |
| `-v`, `--verbose`    | Explain each change as it is made.                   |
| `-R`, `--recursive`  | Operate on files and directories recursively.        |
| `--help`             | Show help and exit.                                  |

### Examples
```bash
# Change only the user (owner) to alice:
chown alice file.txt

# Change user to bob and group to developers:
chown bob:developers file.txt

# Recursively change ownership of a directory tree:
chown -R root:wheel /opt/myapp
```

## `su` and `sudo` – Privilege Escalation
Both commands allow you to execute commands with **elevated privileges**, but they work in different ways.

| Command | What it does | Typical use‑case |
|---------|--------------|------------------|
| `su`    | Starts a new shell as another user (default is `root`). You are prompted for the target user’s password. | When you need an interactive root shell or to become another user for a longer session. |
| `sudo`  | Executes a single command as another user (default is `root`). You are prompted for **your** password (unless configured otherwise). | When you want to run a privileged command without opening a full root shell. |
| `sudo -i` | Starts an interactive login shell as root (similar to `su -`). | Convenient shortcut to get a root environment while keeping your own password. |

### Configuring `sudo`
The file `/etc/sudoers` (edited with `visudo`) defines who may run which commands. A typical entry:

```text
alice ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart apache2
```

This allows user **alice** to restart Apache without a password prompt.

## Scheduling with `cron`, `at`, and `crontab`
Linux provides two main utilities for running commands automatically at a later time or on a regular schedule.

| Utility | Description | Typical scenario |
|---------|-------------|------------------|
| `cron`  | Daemon that runs **periodic** jobs defined in *crontab* files. | Back‑up databases every night, rotate logs daily. |
| `crontab` | Command‑line tool to edit a user’s cron table. | `crontab -e` opens the editor to add scheduled entries. |
| `at`    | Schedules a **one‑time** job to run at a specific time/date. | Run a script at 02:30 AM tomorrow. |

### Crontab Syntax
A crontab line has six fields:

```
* * * * * command
| | | | |
| | | | +----- day of week (0‑7, 0 or 7 = Sunday)
| | | +------- month (1‑12)
| | +--------- day of month (1‑31)
| +----------- hour (0‑23)
+------------- minute (0‑59)
```

**Example:** Run a backup script at 3 AM every day:

```cron
0 3 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

### `at` Example
```bash
echo "/usr/local/bin/cleanup.sh" | at 02:30
```

This schedules `cleanup.sh` to run once at 02:30 AM today (or tomorrow if the time has already passed).

## Exercises
!!! assignment "Exercise E.Linux.1"
    Familiarize yourself with the commands.

!!! assignment "Exercise E.Linux.2"
    Find more commands that you find useful and add them to this page.

!!! assignment "Exercise E.Linux.3"
    Use the `sort` command to sort all lines of a file while removing duplicates.

!!! assignment "Exercise E.Linux.4"
    Should there be other commands listed in the table with the Linux commands? If so which? Create a pull request for them.

!!! assignment "Exercise E.Linux.5"
    Write a section explaining `chmod`. Use letters not numbers.

!!! assignment "Exercise E.Linux.6"
    Write a section explaining `chown`. Use letters not numbers.

!!! assignment "Exercise E.Linux.7"
    Write a section explaining `su` and `sudo`.

!!! assignment "Exercise E.Linux.8"
    Write a section explaining `cron`, `at`, and `crontab`.