# Virtual Machine Management with Multipass

!!! note "Learning Outcome"
    By the end of this section, you will be able to:

    * Install, configure, and troubleshoot Multipass across Linux, macOS, and Windows environments.
    * Manage the complete lifecycle of Ubuntu virtual instances, including hardware driver selection and hypervisor optimization.
    * Leverage advanced `cloud-init` configurations to automate multi-service provisioning, SSH key injection, and security hardening.
   
Multipass is a lightweight command-line tool used to manage Ubuntu virtual machines on local developer workstations. By abstracting hypervisor complexities, it provides an instantaneous bridge between local experimentation and cloud-scale deployment, enabling a true infrastructure-as-code workflow.

For comprehensive architectural documentation, visit the [official Multipass website](https://multipass.run/).

---

## 1. Prerequisites

To run Multipass successfully, your environment must meet specific hardware virtualization, memory, and privilege requirements based on your operating system.

### 1.1 Linux (Ubuntu / Debian-based)

- **Hardware Virtualization**: Hardware-assisted virtualization (Intel VT-x or AMD-V) must be enabled in your system's UEFI/BIOS settings. You can verify support via `lscpu | grep Virtualization`.
- **Memory**: Minimum 2GB RAM per concurrent instance (4GB+ recommended for container workloads like Kubernetes or Docker). Ensure your host has sufficient unallocated RAM.
- **Privileges**: Membership in the `sudoers` list or root access to manage the `snapd` daemon and network bridges.

### 1.2 macOS

- **Hardware Virtualization**: Apple Silicon relies on the native Apple Virtualization Framework. On Intel Macs, Intel VT-x must be enabled in the BIOS/EFI.
- **Memory**: Minimum 2GB RAM per concurrent instance. On Apple Silicon unified memory architectures, ensure sufficient headroom is reserved for the host macOS kernel.
- **Privileges**: An administrator user account capable of installing Homebrew packages or running the `.pkg` installer and modifying system virtualization parameters via `sudo`.

### 1.3 Windows 11

- **Hardware Virtualization**: Hardware virtualization (Intel VT-x or AMD-V) and nested virtualization support must be enabled in your UEFI/BIOS settings.
- **Memory**: Minimum 2GB RAM per instance. When running Hyper-V alongside WSL2 or Docker Desktop, dynamic memory allocation can cause contention; ensure adequate physical RAM is installed (8GB absolute minimum; 16GB+ recommended).
- **Privileges**: Administrative privileges in an elevated PowerShell or Command Prompt to enable Hyper-V features and control the Multipass Windows service.

---

## 2. Installation & Environment Configuration

For up-to-date core binaries, refer to the [official documentation](https://multipass.run/docs). 

### 2.1 Linux (Ubuntu / Debian-based)

On Ubuntu, Multipass is packaged as a strict-confinement [snap](https://snapcraft.io/):

```bash
sudo snap install multipass --classic
```

*Troubleshooting Note*: If you encounter permission errors with the snap socket, verify that the `snapd` service is running and restart your shell session:

```bash
sudo systemctl enable --now snapd.socket
```

### 2.2 macOS

The standard method is via the official installer package, or via Homebrew cask:

```bash
brew install --cask multipass
```

*Driver Note*: macOS supports the Apple Virtualization Framework (default on Apple Silicon) and legacy backends like Hyperkit or VirtualBox. Switch drivers via:

```bash
sudo multipass set local.driver=virtualization
```

### 2.3 Windows 11 (Hyper-V & WSL2 Coexistence)

This may not work on Windows Home. However, we had students in the past that reported they got it to work on Windows EDU.

!!! warning 
    If you are on Windows Home, Hyper-V is unavailable. Install **Oracle VirtualBox** instead, and configure Multipass to use it once multipass is installed:

    ```powershell
    multipass set local.driver=virtualbox
    ```

On Windows Pro or Enterprise, Hyper-V is the native backend driver. You also need the Windows Hypervisor Platform and Virtual Machine Platform enabled so WSL2 and Hyper-V can share the hypervisor layer harmoniously.

* Open an **elevated PowerShell prompt** (Run as Administrator) and execute:
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

* If you plan to use WSL2 concurrently, ensure the Virtual Machine Platform is also enabled:

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
* **Restart your computer** to apply the changes.

* Download and install Multipass. There are different ways on how to install it. the easisets way may be to install winget or chocolatey. As you are Windows users it will be easy for you to find out. We also have an install instruction for chocolatey, ask and I can release it without warrenty obviously.

Once you install chocolatey you can install it with 

```bash
choco install multipass
```

If you install it with winget use

```bash
winget install -e --id Canonical.Multipass
```

* **Configure Multipass to Use Hyper-V**

  Once rebooted, verify that Multipass is communicating with the Hyper-V backend.

  * Set Hyper-V as the default driver (if it isn't already):
  ```powershell
  multipass set local.driver=hyperv
  ```



### 3. Managing Resource Contention (Hyper-V & WSL2)

When running Docker Desktop (which relies on WSL2) and Multipass simultaneously under Hyper-V, they compete for RAM and CPU cores.

* **Dynamic Memory:** Hyper-V can dynamically allocate RAM, but sudden spikes from Docker containers or Multipass instances can cause host stuttering.
* **Best Practice:** Explicitly define CPU and RAM limits when launching instances to reserve headroom for your host OS:
```powershell
multipass launch --cpus 2 --memory 4G --disk 20G --name dev-instance

```


* **WSL2 Resource Limits:** Create a `.wslconfig` file in your Windows user profile directory (`C:\Users\<YourUsername>\.wslconfig`) to cap WSL2's memory usage so it doesn't starve Multipass:
```ini
[wsl2]
memory=4GB
processors=4

```

### 4. Troubleshooting Common Coexistence Issues

* **"Hyper-V is not installed or enabled":** Ensure virtualization is enabled in your computer's BIOS/UEFI settings (Intel VT-x or AMD-V).
* **Port Conflicts:** If services inside your Multipass instance aren't reachable from the host, check your Hyper-V Virtual Switch settings. Multipass creates an external or default switch; ensure your firewall isn't blocking the virtual network adapter.


## 3. The Cloud-Native Mindset: Disposable Infrastructure

Unlike traditional servers that are maintained and run indefinitely, modern cloud development uses disposable, automated instances that can be easily replaced whenever needed. 

Multipass makes this easy by letting you isolate completely different environment requirements on the same computer. For example, if your chemistry professor requires a specific software stack that conflicts with the tools requested by your computer science or physics professors, you can instantly spin up a dedicated, independent virtual machine for each class without any software interference or dependency conflicts. 

## 3.1 Example motivation: Solving the Conda trap

Often professors using conda may run into such issues. Conda is a powerful package and environment manager, but professors across different disciplines often run into severe conflicts when using it for a few core reasons:

* Global Environment Pollution & Dependency Lock-in: By default, Conda installs packages into a shared directory structure. If a chemistry professor's simulation tool requires an older version of a core library (like a specific BLAS implementation or Python version) and your physics or computer science coursework demands a newer release, Conda's global resolver can easily break or deadlock trying to reconcile competing version constraints in a single environment.

* Non-Python Binary Incompatibilities: Conda manages non-Python binaries (such as C/C++ compilers, CUDA toolkits, OpenMPI, or specialized scientific libraries like HDF5 and BLAS). Different academic fields pin these to drastically different, deeply incompatible release cycles. Mixing scientific computing stacks (common in chemistry/physics) with modern AI or systems programming stacks (common in CS) often leads to low-level segmentation faults or silent math calculation errors.

* System-Level Driver & CUDA Mismatches: Chemistry and physics applications frequently compile custom code against specific hardware drivers or local CUDA versions. If two different course environments require different versions of GPU toolkits, Conda environments alone may not isolate low-level driver hooks properly without a full virtual machine layer beneath them.

If possible avoid Conda.

## 4. Core Lifecycle Commands

* **Launch**: `multipass launch --name ubuntu-lts`
* **Execute**: `multipass exec ubuntu-lts -- lsb_release -a`
* **List (JSON formatting for scripts)**: `multipass list --format json`
* **Stop / Start**: `multipass stop ubuntu-lts` followed by `multipass start ubuntu-lts`
* **Teardown**: `multipass delete --all && multipass purge`

---

## 5. Instance Information and Resource Monitoring (`info`)

To inspect detailed operational metrics, network configurations, and resource consumption of a specific virtual instance, use `multipass info`.

* **Viewing Instance Details:**
```bash
multipass info ubuntu-lts
```


*Output details include:* State, IP addresses, release version, CPU load average, disk usage, and allocated memory.
* **Checking All Instances:**
```bash
multipass info --all
```

---

## 6. Interactive Shell Access (`shell`)

When you need an interactive terminal session inside a running instance rather than executing a single isolated command, use `multipass shell`. This command automatically handles SSH key exchange and logs you into the default user account (`ubuntu`) inside the virtual machine.

* **Opening an Interactive Shell:**

```bash
multipass shell ubuntu-lts
```


* **Connecting to the Default "Primary" Instance:**
If an instance is named `primary` (or if it is the only active instance), you can drop into a shell instantly without specifying a name:

```bash
multipass shell
```


* **Exiting the Shell:**
To leave the virtual machine and return to your host terminal, simply type `exit` or press `Ctrl + D`.

---

## 7. Data Transfer and Directory Mounting (`transfer` & `mount`)

Moving code, configuration files, or datasets between your host machine and isolated virtual environments is vital for day-to-day development and testing.

* **File Transfer:** Use `multipass transfer` to securely copy individual scripts or configuration files directly into a running instance:

```bash
multipass transfer local_script.py ubuntu-lts:/home/ubuntu/
```


* **Directory Mounting:** For active development where you want live file syncing without manual copying, use `multipass mount` (which leverages SSHFS or native hypervisor tools under the hood):
```bash
multipass mount /host/workspace ubuntu-lts:/home/ubuntu/workspace

```


*Unmounting:* To cleanly unmount a shared directory:

```bash
multipass umount ubuntu-lts
```

---

## 8. State Management: Snapshots and Recovery (`snapshot`)

Mirroring the immutable infrastructure and checkpointing workflows used in enterprise cloud platforms, snapshots let you freeze a virtual machine's exact disk, memory, and configuration state at a specific moment.

* **Creating a Snapshot:**

```bash
multipass snapshot ubuntu-lts --name clean-base-state
```


* **Listing Snapshots:** View all available checkpoints for a given instance:

```bash
multipass info ubuntu-lts
```


* **Restoring State:** Roll back a misconfigured or broken instance instantly to a known good snapshot:

```bash
multipass restore ubuntu-lts.clean-base-state
```



---

## 9. Custom Networking and Bridged Interfaces (`networks`)

By default, Multipass instances sit behind an internal NAT (Network Address Translation) bridge, which isolates them from your local physical network. For multi-node cluster orchestration or service discovery testing, you can bridge instances directly to your physical network interface.

* **Inspecting Available Networks:** List the physical and virtual interfaces available on your host machine:

```bash
multipass networks
```


* **Launching with a Custom Bridge:** Attach an instance directly to a specific host network bridge (e.g., Wi-Fi or Ethernet adapter) so it acquires an IP address from your local router:

```bash
multipass launch --name worker-node --network bridge0
```

---

## 10. Advanced Automation with Cloud-Init

`cloud-init` standardizes bootstrap configuration. BeloNext we show a production-grade `cloud-config.yaml` that configures a non-root user, injects an SSH public key, updates packages, hardens basic firewall rules via `ufw`, and deploys an Apache service.

```yaml
#cloud-config
users:
  - name: clouduser
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ... user@host

package_update: true
packages:
  - apache2
  - ufw

runcmd:
  - [ ufw, allow, "Apache" ]
  - [ systemctl, enable, apache2 ]
  - [ systemctl, start, apache2 ]
  - [ sh, -c, "echo 'Provisioned via Cloud-Init' > /var/www/html/index.html" ]
```

Launch using this custom configuration:

```bash
multipass launch --name secured-web --cloud-init cloud-config.yaml
```

*Verification*: You can parse `/var/log/cloud-init-output.log` inside the instance to ensure execution completed without error.

---

## 11. Troubleshooting & FAQ

| Symptom / Error | Root Cause | Resolution |
| --- | --- | --- |
| `[FATAL] virtualization not supported` | Hardware-assisted virtualization disabled in BIOS. | Reboot into UEFI/BIOS and enable Intel VT-x or AMD-V. |
| `connection refused / daemon socket error` | Snap daemon or Windows service not running. | Restart service via `sudo systemctl restart snapd` or Windows Services manager. |
| Out of memory errors on launch | Insufficient host RAM allocated to hypervisor pool. | Adjust default instance memory allocations using `multipass set local.memory=2G`. |

---

## Exercises

!!! assignment "Exercise 1: Installation & Verification"
Install Multipass on your primary development operating system and verify functionality:

```bash
multipass version
```

!!! assignment "Exercise 1a: Documentation Improvement"
Document any specific local firewall, proxy, or corporate VPN constraints encountered during your installation and how you routed around them.

!!! assignment "Exercise 2: Multipass Concepts & 'Primary' Instance"
Research and explain the purpose and automatic creation behavior of the default "Primary" instance managed by Multipass.

!!! assignment "Exercise 3: Snapcraft & Packaging"
Explain what Snapcraft is, sandboxing limitations, and why snaps are chosen for Linux distribution of tools like Multipass.

!!! assignment "Exercise 4: Bibliography & Citations"
Generate BibTeX entries for all URLs referenced in this guide and append them to the project bibliography file: `multipass.bib`. Example entry format:

```bibtex
@misc{www-multipass, 
  author = {Canonical}, 
  title = {Multipass: Ubuntu VMs for any workstation}, 
  howpublished = {Online},
  url={https://multipass.run/}, 
  year = {2026}, 
  note = {Accessed: 2026-08-23} 
}
```

!!! assignment "Exercise 5: Image Discovery"
Run `multipass find` and output the supported images in a structured Markdown table including columns for `Image Alias`, `Release Version`, and `Supported Architectures`.

!!! assignment "Exercise 6: Advanced Cloud-Init"
Write a complete `cloud-config` file that automatically provisions an environment capable of launching local lightweight workloads (e.g., pulling an Ollama model container on first boot).

!!! assignment "Exercise 7: Kubernetes with MikroK8s"
Provision a MikroK8s node inside a Multipass instance and write a 3-step verification guide confirming cluster health via `microk8s status`.

!!! assignment "Exercise 8: Performance Benchmarking via Pytest"
Using the [cloudmesh-multipass](https://www.google.com/search?q=https://github.com/cloudmesh-community/cloudmesh-multipass) repository, write a `pytest` suite that measures image fetch and launch times under cold versus warm cache states. Output the results as a Markdown table containing: `Image`, `Hypervisor`, `Cache State`, `Fetch Time (s)`, `Launch Time (s)`, and `Execution Time (s)`, ensuring instances are purged between test cycles.

!!! assignment "Exercise 9a: Understanding k3s"
Investigate [k3s.io](https://k3s.io/) and the Rancher documentation to summarize the architectural differences between standard Kubernetes and k3s for edge/local deployments.

!!! assignment "Exercise 9b: Multi-Node k3s Cluster Deployment"
Implement a Cloudmesh command generator (`cloudmesh sys command generate k3s`) supporting options `--hypervisor` and `--names node[0-3]` to deploy, start, stop, purge, and delete a multi-node k3s cluster over Multipass nodes.

!!! assignment "Exercise 10: ComputeNodeABC Provider Implementation"
Extend the Multipass provider by inheriting from the `ComputeNodeABC` abstract class in [cloudmesh-cloud](https://www.google.com/search?q=https://github.com/cloudmesh/cloudmesh-cloud). Implement core lifecycle methods (`create`, `destroy`, `stop`, `start`, `info`), parse responses via JSON, and submit your implementation via a Pull Request.

```

```