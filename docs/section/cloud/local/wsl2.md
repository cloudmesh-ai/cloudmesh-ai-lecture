# Virtual Machine Management with WSL2

Windows Subsystem for Linux 2 (WSL 2) allows developers to run a native Linux environment—including most command-line tools, utilities, and applications—directly on Windows, unmodified, alongside traditional Windows desktop and GUI applications.

---

## Prerequisites & System Requirements

Before you begin, verify that your system meets the following requirements:
*   **Operating System:** 
    *   Windows 11 (64-bit: Home, Pro, Enterprise, or Education).
    *   Windows 10 (64-bit: Version 2004 or higher, Build 19041 or higher).
*   **Virtualization:** Hardware virtualization must be enabled in your computer's BIOS/UEFI settings.

---

## Step 1: Install WSL 2

Modern versions of Windows make installing WSL extremely simple with a single command.

1. Open **PowerShell** or **Command Prompt** as an **Administrator** (Right-click $
ightarrow$ *Run as administrator*).
2. Run the installation command:
   ```bash
   wsl --install
   ```
3. **What this command does automatically:**
   * Enables the required optional features (`VirtualMachinePlatform` and `Microsoft-Windows-Subsystem-Linux`).
   * Downloads and installs the latest Linux kernel.
   * Sets WSL 2 as the default architecture.
   * Downloads and installs the default Linux distribution (**Ubuntu**).
4. **Restart your computer** when prompted to complete the installation.

---

## Step 2: Set Up Your Linux User Account

Upon rebooting, a terminal window will automatically open to complete the Linux installation.

1. Wait for the installation process to unpack files.
2. When prompted, **enter a UNIX username** (this does not need to be your Windows username).
3. **Enter a UNIX password** and confirm it. *(Note: Characters will not be visible on screen as you type—this is normal security behavior).*
4. Once completed, you will see a bash prompt (`username@hostname:~$`), indicating your Linux environment is ready.

---

## Step 3: Verify Your WSL Version

To confirm that your distribution is running on WSL 2, open PowerShell or Command Prompt and run:

```bash
wsl -l -v
```

You should see output similar to this:
```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```
*If the version says `1`, you can upgrade your distribution to WSL 2 with the command: `wsl --set-version Ubuntu 2]`*

---

## Step 4: Essential Day-to-Day WSL Commands

Managing your WSL distributions is done through the `wsl` command in PowerShell, Command Prompt, or Windows Terminal.

| Command | Description |
| :--- | :--- |
| `wsl` | Starts your default Linux distribution. |
| `exit` | Closes the current Linux session and returns to Windows. |
| `wsl --list --online` | Lists available Linux distributions that can be installed. |
| `wsl --install -d <Distro>` | Installs a specific distribution (e.g., `wsl --install -d Debian`). |
| `wsl --shutdown` | Immediately terminates all running WSL instances and background VMs. |
| `wsl --export <Distro> <Filename>` | Exports a distribution to a `.tar` file for backup. |

---

## Step 5: Bridging Windows and Linux

WSL 2 offers seamless integration between your Windows host and the Linux guest.

### Accessing Windows Files from Linux

Your Windows drives are automatically mounted under the `/mnt/` directory inside your Linux file system. For example, your `C:` drive is located at `/mnt/c/`:

```bash
cd /mnt/c/Users/YourUsername/Documents
ls
```

### Accessing Linux Files from Windows

You can access your Linux files directly from Windows File Explorer. 
1. Open File Explorer.
2. In the address bar, type:

   ```text
   \wsl$
   ```

3. You will see folders for each installed distribution, allowing you to drag, drop, and edit files using standard Windows editors.

### Launching Windows Apps from Linux

You can launch Windows executables and tools directly from your bash terminal by appending `.exe`:

```bash
notepad.exe myfile.txt # the worst editor 
code .  # Opens Visual Studio Code in the current Linux directory
```

---

## Step 6: Developing with WSL 2 & VS Code

The most powerful way to use WSL 2 is alongside **Visual Studio Code**.

1. Install **VS Code** on your Windows machine.
2. Install the **WSL extension** from the VS Code Marketplace (Extension ID: `ms-vscode-remote.remote-wsl`).
3. Open your WSL terminal and navigate to a project directory:
   ```bash
   cd ~/projects/my-app
   ```
4. Type the following command to open VS Code directly connected to your WSL environment:
   ```bash
   code .
   ```
5. A new VS Code window will open. In the bottom-left corner, you will see a green indicator showing `>< WSL: Ubuntu`, confirming you are editing files directly inside the Linux filesystem with full terminal and debugging integration.

---

## Starting More Than One Instance

By default, running wsl opens your default Linux distribution. However, WSL 2 allows you to run multiple distributions or multiple independent instances of the same distribution simultaneously.

1. Running Different Distributions

   If you have multiple distributions installed (for example, Ubuntu and Debian), you can run them side by side in separate terminal windows:

   ```bash
   wsl -d Ubuntu
   wsl -d Debian
   ```

2. Running Multiple Instances of the Same Distribution

   You can also launch multiple independent terminal sessions of your default or specific distribution simultaneously:

   Open a new PowerShell, Command Prompt, or Windows Terminal tab and type wsl again. Each invocation spins up a separate, concurrent session connected to the same underlying Linux environment.

3. Targeting Specific Users in an Instance

   If you need to log into a specific instance under a different user profile (such as the root user for administrative tasks), use the -u flag:

   ```bash
   wsl -u root
   ```

## Named instances

By default, installing a distribution like Ubuntu only gives you one instance with a generic name. However, you can create multiple, custom-named instances of the exact same Linux distribution (for isolated testing, projects, or different configurations) using the `export` and `import` commands.

1. Export your existing distribution as a template

   First, use an existing installed distribution (like `Ubuntu`) to create a backup file (`.tar`) that will serve as your blueprint:

   ```bash
   wsl --export Ubuntu C:\wslbackup\ubuntu-base.tar

   ```

2. Import it back with a custom name and directory

   Use the `--import` command to unpack that template into a brand-new instance with whatever name you want:

   ```bash
   wsl --import MyCustomDevBox C:\WSL\CustomDevBox C:\wslbackup\ubuntu-base.tar
   ```

   * `MyCustomDevBox` — This is your **custom instance name**.
   * `C:\WSL\CustomDevBox` — This is the folder where your new instance's virtual hard disk (`ext4.vhdx`) will live.
   * `C:\wslbackup\ubuntu-base.tar` — The template backup you created.

3. Run your newly named instance

   You can now launch, target, or manage your newly named environment using the `-d` flag:

   ```bash
   wsl -d MyCustomDevBox
   ```

   To verify all your named instances and see their active versions, run:

   ```bash
   wsl -l -v
   ```

!!! note:
    if you find better ways to create multiple VMs, let us know. I do not own a Windows PC so its difficult for me to find out and try.


#### Alternative: Renaming an Existing Instance

If you want to rename an instance you already have, you can change its name by editing its entry in the Windows Registry (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Lxss`) under the `DistributionName` string value, then restarting WSL with `wsl --shutdown`.

### Program to create a named WSL2 instance

Make sure you have Python installed along with the `click` library:

```bash
pip install click

```

Save the following code as `wsl_manager.py`:

```python
import subprocess
import os
import click

@click.command()
@click.option('--name', 
   required=True, 
   help='The custom name for the WSL instance.')
@click.option('--base', 
   default='Ubuntu', 
   show_default=True, 
   help='The base distribution to copy from if creating a new instance.')
def main(name, base):
    """Manages and launches custom-named WSL 2 instances."""
    
    # 1. Check if the custom WSL instance is already registered
    try:
        result = subprocess.run(['wsl.exe', '-l', '-q'],      
            capture_output=True, 
            text=True, check=True)
        # Clean up carriage returns from Windows output
        existing_distros = [line.strip().replace('\x00', '') for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        click.echo("Error: Failed to query WSL distributions.", err=True)
        return

    if name in existing_distros:
        click.echo(f"Starting existing WSL instance: {name}...")
        subprocess.run(['wsl.exe', '-d', name])
    else:
        click.echo(f"Instance '{name}' not found.")
        if click.confirm(f"Would you like to create it now based on '{base}'?"):
            install_dir = f"C:\\WSL\\{name}"
            temp_tar_linux = "/tmp/wsl-base-temp.tar"
            
            click.echo(f"Exporting base distribution ({base})...")
            # Export base distro to a temp tar file inside WSL path
            subprocess.run(['wsl.exe', '--export', base, temp_tar_linux], check=True)
            
            # Convert Linux path to Windows style using wslpath
            path_result = subprocess.run(['wsl.exe', 
               'wslpath', 
               '-w', temp_tar_linux], 
               capture_output=True, 
               text=True, 
               check=True)
            win_temp_tar = path_result.stdout.strip()
            
            click.echo(f"Importing new instance as '{name}' into {install_dir}...")
            subprocess.run(['wsl.exe', 
               '--import', name, 
               install_dir, 
               win_temp_tar, 
               '--version', 
               '2'], check=True)
            
            # Cleanup temp file inside WSL
            subprocess.run(['wsl.exe', 'rm', '-f', temp_tar_linux])
            
            click.echo(f"Launching new instance: {name}...")
            subprocess.run(['wsl.exe', '-d', name])
        else:
            click.echo("Aborted.")

if __name__ == '__main__':
    main()

```

---

### How to Use It

1. Run the script using Python via your terminal (Git Bash, Command Prompt, or PowerShell):
```bash
python wsl_manager.py --name MyProjectEnv
```


2. You can also override the default base distribution if needed:
```python
python wsl_manager.py --name DebianDev --base Debian
```


3. Run with `--help` to see built-in documentation and options:
```bash
python wsl_manager.py --help
```


---
## Troubleshooting Common Issues

*   **Error: `WslRegisterDistribution failed with error: 0x800701bc`**
    *   *Cause:* The WSL 2 kernel component is missing.
    *   *Fix:* Download and install the latest [WSL2 Linux kernel update package for x64 machines](https://aka.ms/wsl2kernel).
*   **Error: `0x80370102` (Virtualization is disabled)**
    *   *Cause:* Intel VT-x or AMD-V virtualization is disabled in your motherboard's BIOS/UEFI.
    *   *Fix:* Reboot into your BIOS settings, enable **Virtualization Technology (VT-x / AMD-V)**, save, and restart.
*   **Network / DNS Issues inside WSL**
    *   *Fix:* Sometimes Windows VPNs interfere with WSL DNS resolution. You can fix this by creating or editing `/etc/wsl.conf` inside Linux:
        ```ini
        [network]
        generateResolvConf = false
        ```
        And setting custom nameservers in `/etc/resolv.conf` (e.g., `nameserver 8.8.8.8`).
