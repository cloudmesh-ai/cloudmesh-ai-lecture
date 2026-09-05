# Gitbash

Installing Git Bash on Windows 11 is a straightforward process. Git Bash is packaged automatically with **Git for Windows**, giving you both the version control system and the Bash emulation terminal.

### Download URL

You can download the official installer directly from the Git for Windows project page:

* **Download Link:** [https://gitforwindows.org/](https://gitforwindows.org/) (or the direct project mirror at [https://git-scm.com/download/win](https://git-scm.com/download/win))

---

### Step-by-Step Installation Instructions

1. **Download the Installer:** Web Browser.
Open your web browser, navigate to the Git for Windows website, and click on the **Download** button to save the executable file (`.exe`) to your PC.


2. **Run the Installer:** User Account Control.
Locate the downloaded `.exe` file (usually in your **Downloads** folder) and double-click it to start.

If Windows prompts a User Account Control (UAC) message asking, *"Do you want to allow this app to make changes to your device?"*, click **Yes**.


3. **Step Through Setup Options:** Recommended Defaults.
Review the GNU General Public License, then click **Next**. For most users, accepting the **default settings** across all setup screens is recommended, as they are fully optimized for Windows 11.

*Note: You can safely click **Next** through options like choosing components, selecting the start menu folder, and choosing your default text editor unless you have specific preferences.*


4. **Complete the Installation:** Finalize.
Once you reach the final configuration screen, click **Install**. Wait for the progress bar to finish, leave the option to *Launch Git Bash* checked if you'd like, and click **Finish**.


---

### Verifying Your Installation

To confirm that Git and Git Bash are installed and configured correctly on Windows 11:

1. Press the **Windows Key** on your keyboard and type **Git Bash**.
2. Click on the **Git Bash** app icon to open the terminal.
3. In the terminal window that appears, type the following command and press **Enter**:

    ```bash
    git --version
    ```


4. **Verification Success:** You should see a response showing your installed version (e.g., `git version 2.x.x.windows.1`), confirming the environment is working properly.

---

### Must do First-Time Configuration

Before you start tracking projects, run these two commands in Git Bash to configure your identity for Git commits:

```bash
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"

```

## Appendix - Automated deployments

!!! warning "Untested, i do not have Windows"

Git Bash can be fully automated and installed via configuration management and deployment tools like **Ansible**, **Winget**, or **Chocolatey**.

### Method 1: Using Ansible

Ansible can manage Windows nodes remotely via WinRM. You can use either the `win_chocolatey` module or run `winget` directly through Ansible tasks to automate the installation and configure your git user profile.

Here is an example playbook snippet using Chocolatey:

```yaml
- name: Install Git for Windows (includes Git Bash)
  chocolatey.chocolatey.win_chocolatey:
    name: git
    state: present

- name: Configure global Git user name
  ans.windows.win_command: git config --global user.name "Your Full Name"
  # Or use ansible.windows.win_powershell / win_shell

- name: Configure global Git user email
  ans.windows.win_command: git config --global user.email "your.email@example.com"

```

### Method 2: Using Native Windows Package Managers (Winget / Chocolatey)

If you are bootstrapping machines locally or through scripts without Ansible, you can invoke a package manager directly from PowerShell or Command Prompt.

* **Using Winget (Built into Windows 11):**
```powershell
winget install --id Git.Git -e --source winget

```


* **Using Chocolatey:**
```powershell
choco install git -y

```



Once installed via any of these tools, Git Bash is automatically placed on your system along with the command-line tools, requiring no manual GUI clicking. 


!!! Assignmnet 
    In the last two cases you still have to set the username and email. please work as a team and create a pull request completing the documentation
