# Tutorial 1: Using Lima on MacOS

Lima is a lightweight tool that launches Linux virtual machines with automatic file sharing and port forwarding, making it ideal for command-line workflows and container runtimes.

## Step 1: Install Lima and QEMU

Using Homebrew, install Lima and its virtualization backend:

```bash
brew install lima qemu

```

## Step 2: Create and Start a Linux Instance

Lima uses YAML configuration files. You can start a default Ubuntu virtual machine with a single command:

```bash
limactl start default

```

*During startup, it will ask you to choose a template. Select the default Ubuntu template, or let it spin up the default instance.*

## Step 3: Open the Linux Shell

Once the instance is running, connect to it via SSH:

```bash
limactl shell default

```

*You are now inside an Ubuntu Linux environment running on your Mac.*

## Step 4: Install Apptainer inside the Lima VM

Inside your Lima shell, follow the standard Ubuntu installation steps outlined earlier to install Apptainer, Go, and build your containers.
