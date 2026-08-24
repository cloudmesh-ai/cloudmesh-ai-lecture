---
title: "Ubuntu Server CLI Cheat Sheet"
---

This cheat sheet provides a quick reference for the most commonly used Command Line Interface (CLI) commands for Ubuntu Server. It is designed to help students and administrators navigate the system, manage services, and configure networking efficiently. The content is taken from <https://assets.ubuntu.com/v1/3bd0daaf-Ubuntu%20Server%20CLI%20cheat%20sheet%202024%20v6.pdf>

## System

### System Information
| Command | Description |
| :--- | :--- |
| `uname -a` | Displays all system information |
| `hostnamectl` | Shows current hostname and related details |
| `lscpu` | Lists CPU architecture information |
| `timedatectl status` | Shows system time |

### System Monitoring & Management
| Command | Description |
| :--- | :--- |
| `top` | Displays real-time system processes |
| `htop` | Interactive process viewer (requires installation) |
| `df -h` | Shows disk usage in human-readable format |
| `free -m` | Displays free and used memory in MB |
| `kill <pid>` | Terminates a process by its ID |

### Running Commands
| Command | Description |
| :--- | :--- |
| `[command] &` | Runs command in the background |
| `jobs` | Displays background commands |
| `fg <number>` | Brings a background command to the foreground |

### Service Management
| Command | Description |
| :--- | :--- |
| `sudo systemctl start <service>` | Starts a service |
| `sudo systemctl stop <service>` | Stops a service |
| `sudo systemctl status <service>` | Checks the status of a service |
| `sudo systemctl reload <service>` | Reloads configuration without interrupting operation |
| `journalctl -f` | Follows the journal, showing logs in real time |
| `journalctl -u <unit>` | Displays logs for a specific systemd unit |

### Cron Jobs & Scheduling
| Command | Description |
| :--- | :--- |
| `crontab -e` | Edits cron jobs for the current user |
| `crontab -l` | Lists cron jobs for the current user |

## Files

### File & Directory Management
| Command | Description |
| :--- | :--- |
| `ls` | Lists files and directories |
| `touch <file>` | Creates an empty file or updates access date |
| `cp <src> <dest>` | Copies files from source to destination |
| `mv <src> <dest>` | Moves or renames files |
| `rm <file>` | Deletes a file |
| `pwd` | Displays the current directory path |
| `cd <dir>` | Changes the current directory |
| `mkdir <dir>` | Creates a new directory |

### Permissions & Ownership
| Command | Description |
| :--- | :--- |
| `chmod [who][+/-][perms] <file>` | Changes file permissions |
| `chmod u+x <file>` | Makes a file executable by its owner |
| `chown [user]:[group] <file>` | Changes file owner and group |

### Searching & Text Processing
| Command | Description |
| :--- | :--- |
| `find [dir] -name <pattern>` | Finds files and directories |
| `grep <pattern> <file>` | Searches for a pattern in files |
| `nano [file]` | Opens a file in the Nano text editor |
| `cat <file>` | Displays contents of a file |
| `less <file>` | Displays paginated content of a file |
| `head <file>` | Shows the first few lines of a file |
| `tail <file>` | Shows the last few lines of a file |
| `awk '{print}' [file]` | Prints every line in a file |

### Archiving & Compression
| Command | Description |
| :--- | :--- |
| `tar -czvf <name.tar.gz> [files]` | Compresses files into a tar.gz archive |
| `tar -xvf <archive> [dest]` | Extracts a compressed tar archive |

## Packages

### Package Management (APT)
| Command | Description |
| :--- | :--- |
| `sudo apt update` | Updates package lists |
| `sudo apt upgrade` | Upgrades all upgradable packages |
| `sudo apt install <pkg>` | Installs a package |
| `sudo apt install -f --reinstall <pkg>` | Reinstalls a broken package |
| `apt search <pkg>` | Searches for APT packages |
| `apt-cache policy <pkg>` | Lists available package versions |
| `sudo apt remove <pkg>` | Removes a package |
| `sudo apt purge <pkg>` | Removes a package and its configuration files |

### Package Management (Snap)
| Command | Description |
| :--- | :--- |
| `snap find <pkg>` | Search for Snap packages |
| `sudo snap install <snap>` | Installs a Snap package |
| `sudo snap remove <snap>` | Removes a Snap package |
| `sudo snap refresh` | Updates all installed Snap packages |
| `snap list` | Lists all installed Snap packages |
| `snap info <snap>` | Displays information about a Snap package |

## Users & Groups

| Command | Description |
| :--- | :--- |
| `w` | Shows which users are logged in |
| `sudo adduser <user>` | Creates a new user |
| `sudo deluser <user>` | Deletes a user |
| `sudo passwd <user>` | Sets or changes the password for a user |
| `su <user>` | Switches user |
| `sudo passwd -l <user>` | Locks a user account |
| `sudo passwd -u <user>` | Unlocks a user password |
| `id [user]` | Displays user and group IDs |
| `groups [user]` | Shows the groups a user belongs to |
| `sudo addgroup <group>` | Creates a new group |
| `sudo delgroup <group>` | Deletes a group |

## Networking

### Network Configuration & Monitoring
| Command | Description |
| :--- | :--- |
| `ip addr show` | Displays network interfaces and IP addresses |
| `ip -s link` | Shows network statistics |
| `ss -l` | Shows listening sockets |
| `ping <host>` | Pings a host and outputs results |

### Netplan (Network Configuration)
| Command | Description |
| :--- | :--- |
| `cat /etc/netplan/*.yaml` | Displays current Netplan configuration |
| `sudo netplan try` | Tests a new configuration for a set period |
| `sudo netplan apply` | Applies the current Netplan configuration |

### Firewall (UFW)
| Command | Description |
| :--- | :--- |
| `sudo ufw status` | Displays the status of the firewall |
| `sudo ufw enable` | Enables the firewall |
| `sudo ufw disable` | Disables the firewall |
| `sudo ufw allow <port/svc>` | Allows traffic on a specific port or service |
| `sudo ufw deny <port/svc>` | Denies traffic on a specific port or service |
| `sudo ufw delete allow/deny <port/svc>` | Deletes an existing rule |

### SSH & Remote Access
| Command | Description |
| :--- | :--- |
| `ssh <user@host>` | Connects to a remote host via SSH |
| `scp <src> <user@host>:<dest>` | Securely copies files between hosts |

## LXD (Containers & VMs)

LXD is a tool for running and managing containers or virtual machines. Visit [canonical.com/lxd](https://canonical.com/lxd) for more information.

| Command | Description |
| :--- | :--- |
| `lxd init` | Initializes LXD before first use |
| `lxc init <image> <name>` | Creates a system container (without starting it) |
| `lxc launch <image> <name>` | Creates and starts a system container |
| `lxc launch <image> <name> --vm` | Creates and starts a virtual machine |
| `lxc list` | Lists instances |
| `lxc info <instance>` | Shows status information about an instance |
| `lxc start <instance>` | Starts an instance |
| `lxc stop <instance> [--force]` | Stops an instance |
| `lxc delete <instance> [--force]` | Deletes an instance |
| `lxc exec <instance> -- <cmd>` | Runs a command inside an instance |
| `lxc exec <instance> -- bash` | Gets shell access to an instance |
| `lxc console <instance>` | Gets console access to an instance |
| `lxc file pull <inst>/<path> <local>` | Pulls a file from an instance |
| `lxc file push <local> <inst>/<path>` | Pushes a file to an instance |

