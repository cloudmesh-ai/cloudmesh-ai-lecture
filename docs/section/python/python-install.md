---
title: "Python Installation"
---

!!! info "Learning Outcomes"
    - Install Python 3.12 using various methods, including official installers, Homebrew, and compiling from source.
    - Set up and manage isolated Python environments using `venv` to prevent system-wide dependency conflicts.
    - Configure environment variables and shell profiles for automatic virtual environment activation.
    - Verify Python and pip installations to ensure version compatibility with AI and cloud frameworks.

!!! info "Version Compatibility"
    Based on the requirements as of 2026, we recommend using **Python 3.12**. This version is fully compatible with the latest stable releases of the core AI frameworks, including **PyTorch**, **TensorFlow**, and **Keras**.
    
    Using Python 3.12 ensures you have access to the latest language features and performance improvements while maintaining stability across the AI ecosystem.

In this section, we explain how to install Python 3.12.x on a computer. Likely, much of the code will work with earlier versions, but we do the development in Python on the newest version of Python available at <https://www.python.org/downloads> .

## Hardware

In general, using Python does not require any special hardware. We have installed Python not only on PCs and laptops but also on Raspberry Pis and Lego Mindstorms.

However, there are some things to consider when developing code. If you use many programs on your desktop and run them all at the same time, you will discover that in an up-to-date operating system, you will quickly run out of memory. This is not really a Python issue, but is caused by other programs you may run on your computer. This is especially true if you use web browsers and editors such as PyCharm, which we highly recommend. Furthermore, as you likely have lots of disk access, make sure to use a fast HDD; we recommend using SSDs or NVMe storage.

A typical modern developer PC or Laptop has *16GB RAM* and an *SSD*. You can certainly do Python on a \$35-\$75 Raspberry PI, but you probably will not be able to run PyCharm. There are many alternative editors with a smaller memory footprint available.

## Python 3.12.9 from Source

To install Python 3.12.9 from source, you can use the following commands. Please note that the parameter behind -j specifies a parallelism for the compile. Please only use the number of processors for your computer.

``` bash
# Prepare the build directory
cd ~
mkdir -p tmp
cd tmp

# Download and extract Python 3.12.9
wget https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz
tar xvf Python-3.12.9.tgz 
cd Python-3.12.9/

# Configure the build
# --enable-optimizations: Runs Profile Guided Optimization (PGO)
# --with-lto: Enables Link Time Optimization for a faster binary
./configure --enable-optimizations --with-lto --enable-loadable-sqlite-extensions

# Compile the source
# -S: Silent mode (optional)
# -j: Parallel jobs (adjust 16 to your CPU core count)
make -j 16

# Install the binary
# Use 'altinstall' to avoid overwriting the system 'python3' binary
sudo make altinstall
```

## Python 3.12

Here we discuss how to install Python 3.12 on your operating system. It is typically advantageous to use a newer version of Python, so you can leverage the latest features. Please be aware that many operating systems come with older versions that may or may not work for you. You can always start with the version that is installed, and if you run into issues, update later.

### Python 3.12 on macOS

[![Video](../../assets/images/video.png) (5:28) Mac Python Installation Video Tutorial](https://youtu.be/TttmzM-EDmk)

First, you want to install a number of useful tools on your macOS. This includes git, make, and a C compiler. All this can be installed with Xcode, which is available from

- <https://apps.apple.com/us/app/xcode/id497799835>

Once you have installed it, you need to install macOS XCode command-line tools:

``` bash
$ xcode-select --install
```

The easiest installation of Python is to use the installation from <https://www.python.org/downloads>. Please, visit the page and follow the instructions to install the Python `.pkg` file. After this install, you have python3 available from the command line.

#### Python 3.12 on macOS via Homebrew

Homebrew provides you with an alternative installation. However, we noticed that Homebrew may not provide you with the newest version, so we recommend using the install from python.org if you can.

To use this installation method, you need to install Homebrew first. Start the process by installing first `homebrew` as documented on their [Web page](https://brew.sh/#install):

``` bash
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Now you can install Python using:

``` bash
$ brew install python@3.12
```

### Python 3.12 on Windows

[![Video](../../assets/images/video.png) (2:16) Windows Python Installation Video Tutorial](https://youtu.be/T6UYyu5XVMc)

Python can be installed on Windows using: <https://www.python.org/downloads>

Follow the instructions provided by the installer. It is critical that you select the checkbox **`[x] Add Python to PATH`** during the installation process. This allows you to run python commands from the terminal/command prompt.

Once installed, open a terminal (cmd or PowerShell) and execute:

``` bash
python --version
```

#### Python in the Linux Subsystem (WSL)

An alternative is to use Python from within the Linux Subsystem (WSL). This is highly recommended for developers on Windows to have a more Unix-like environment.

To activate the Linux Subsystem, please follow the instructions at:
- <https://docs.microsoft.com/en-us/windows/wsl/install-win10>

A suitable distribution would be:
- <https://www.microsoft.com/en-us/p/ubuntu-1804-lts/9n9tngvndl3q?activetab=pivot:overviewtab>

### Python 3.12.9 from Source (Ubuntu 24.04)

[![Video](../../assets/images/video.png) (9:13) Linux Python Installation Video Tutorial](https://youtu.be/4vXyD_hjHNI)

To install Python 3.12.9 from source on Ubuntu 24.04, follow these steps. This process includes installing the required build-essential packages and configuring Python with modern optimizations.

#### 1. Install Build Dependencies

Before compiling, you must install the libraries required for Python’s modules (like SSL, SQLite, and Readline) to work.

``` bash
sudo apt update
sudo apt install -y \
    build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev lib readline-dev libsqlite3-dev \
    libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
    libffi-dev uuid-dev tk-dev wget curl
```

#### 2. Download and Compile

The `-j` parameter passed via the make command specifies the parallelism for the compile. Use the number of logical processors for your computer (e.g., **16**, yours may be different).

``` bash
# Prepare the temporary build directory
cd ~
mkdir -p tmp
cd tmp

# Download and extract Python 3.12.9
wget https://www.python.org/ftp/python/3.12.9/Python-3.12.9.tgz
tar xvf Python-3.12.9.tgz 
cd Python-3.12.9/

# Configure the build
# --enable-optimizations: Enables Profile Guided Optimization (PGO)
# --with-lto: Enables Link Time Optimization for better performance
./configure --enable-optimizations --with-lto --enable-loadable-sqlite-extensions

# Compile the source
# Replace 16 with your actual CPU core count
make -j 16

# Install the binary
# 'altinstall' prevents overwriting the system /usr/bin/python3
sudo make altinstall
```

#### 3. Verify the Installation

``` bash
python3.12 --version
```

## venv

As a developer, you must use a python virtual environment to avoid affecting your system-wide Python installation. Not using a venv could have catastrophic consequences for your operating system tools if they rely on Python.

### Creating a Virtual Environment

We assume that you use the directory `~/ENV3`.

``` bash
$ python3.12 -m venv ~/ENV3
$ source ~/ENV3/bin/activate
```

### Automating Activation

To activate it when you start a new terminal, add the following line to your `.bashrc` (Ubuntu) or `.bash_profile`/`.zprofile` (macOS) file:

``` bash
source ~/ENV3/bin/activate
```

#### Automatic Activation for Git Bash on Windows

On Windows, you can set Git Bash to automatically use this venv:

1. Open `.bashrc` using vi:
   ``` bash
   $ cd ~
   $ vi .bashrc
   ```
2. Add the following line:
   ``` vim
   source ~/ENV3/Scripts/activate
   ```
3. Save and exit (`:wq`).

### Confirm Python is installed

Check if you have the right version of Python installed:

``` bash
$ python --version
```

To make sure you have an up-to-date version of pip, issue the command:

``` bash
$ pip install pip -U
```

## Install Python via Anaconda or Miniconda

We are not recommending the use of conda or Anaconda for this course. However, if you choose to use them, be aware that Anaconda installs additional tools that may be considered bloat.

!!! warning
    When installing Anaconda, do NOT add it to the path or run `conda init`. This modifies your command prompt to register the `(base)` environment by default, which adversely interacts with other Python installations.

#### Configuring `conda` to be on the path (Safe Method)

To prevent polluting the command line path, only expose the `conda` command:

**Windows:**
``` batch
setx PATH <path_to_conda_install>\condabin;%PATH%
```

**Linux / MacOS:**
Add to `.bashrc`, `.bash_profile`, or `.zprofile`:
``` bash
source <path_to_conda_install>/etc/profile.d/conda.sh
```

#### Installing Python via `conda`

``` bash
$ conda create -n ENV3 -c conda-forge python=3.12 pip
```

#### Activating and Deactivating Conda

To activate our `ENV3` environment:
``` bash
conda activate ENV3
```

To deactivate:
``` bash
conda deactivate
```

### Final Version Test

Regardless of the installation method, verify your versions:

``` bash
$ python --version
$ pip --version
```

Expected versions:
- Python 3.12.9 (or similar)
- pip 21.3.1 (or similar)