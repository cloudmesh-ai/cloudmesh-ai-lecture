# Assignments

!!! warning "All assignments are due on *Thursdays 9am*. This is 9am in the morning so I can attempt to review your assignments before class"

!!! warning "Do not start VMs or containers or use other resources from access-ci jetstream or chameleon cloud yet."

!!! info "Teamwork is allowed on any assignment."

    You are allowed to work in a team. This may be done either remotely or via in-person meetings. When working in teams, you need to provide documentation of who did what. Teams can be different for different assignments. Some homework may foster ad-hoc teams that utilize the same platform or operating system. Just make sure you do not just blindly replicate someone else's work. If you work on a team, please put that in your assignment solution and describe who did what.

!!! Assignments "Assignments: Every week"

    1. Review lecture material
    2. Improve with pull requests if you see issues
    3. Help each other
    4. Update the `README.md` with the list of assignments that are posted each week.
    5. You can add a subbullet with - [ ] Other and check what other things you did. If there are relevant links in GitHub, make sure to post them here.


## Week 5:  Due Oct 1, 2026, 9am

??? note "Click here to see a draft version of the Assignments Week 5, Oct 1 , 2026 (not yet due)"

    !!! Warning 
        The list of assignments is not finalized. The assignments   listed here are just some ideas. I am sure they will change. However you can start working ahed if you wish, but do not be angry, or disapointed if the assignments change.
    
        !!! note note "Assignment W5.1 VMs via python (libcloud)"

            In <https://github.com/cloudmesh-ai/cloudmesh-ai-vm> 
            we are providing the template to a multicloud management tool. This tool has not been tested and only provides the framework. Some function such as starting vms on multipass should work.
            
            Your task is it to engage with the entire class to learn ho wto use github with a larger group as part of devops development activities, but also to improve the code so you can integrate it in your devops projects.

            1. decide which clouds you like to implement the command for or improve. This can be multiple.

            2. Understand the structure of the code, which included
                * a configuration file for all clouds
                * the commandline based on click
                * the various Cloud provider interfaces
                
              Typically you only have to improve the implamentation and the configuration file. Please note that in case of openstack you also deal with another file in ~/.config/openstack/clouds.yml
              which is different from ~/.config/cloudmesh/clouds.yml
            
                ```
                username: gregor
                couter: 0
                clouds:
                jetstream:
                    flavour: ...
                    image: ...
                    security group:
                        ...
                    auth: path to the credentials
                    keys:
                        ...
                        ...
                ...
                ```
            YOu will be responsible for implementing all commands as much as possible and showcase that they work with a simple shell script. Demonstrating wich command succeeds and which failes. The hope is that all will succeed.

            If tike allows also update the markdown documentation with examples for the clouds you have picked.

            You can get the manual page with 

            ```bash
            cmc man vm 
            ```

            Example comamnds include 

            * cmc vm set multipass # wsl2, VBox, ... to set the default cloud
            * cmc vm start [--name=NAME]# starts a vm and names the vm <username><counter+1> or the one defined by name
            if no name is provided the counter in the yaml file is incremented.
            * cmc vm --name=the name # overwrites the naming and does not increment counter
            cmc stop [--name=NAME] # stops the last started vm or the one with the name
            * cmc vm login [--name=NAME]# logs into the last started vm
            * cmc vm suspend ...
            * cmc vm retart ...
            * cmc vm delete ...
            * cmc vm list [--jason|--yaml|--csv|--table]

            !!! note
                you will need to create a fork and clone it into your own directory.

                Readup in google how to work on a forked repo with a colleague.
            
            !!! tip 

                Pair programming could help if needed

                Ask on piazza and communicate with each other.
            

## Week 4:  Due Sep 24, 2026, 9am

!!! note note "Assignment W4.1 VM on local machine via Makefile"

    1. Pick a local VM framework. Make sure it is installed.
    2. Write a Makefile with all the targets that you need (which are they?) to manage a single VM
    3. Can you manage multiple machines? How.
    4. How do you organize different Makefiles for different local and cloud environments (tip directories) there re other ways to do this, but directories are easy

!!! note note "Assignment W4.2 VM on Jetstream 2"

    1. Pick a local VM framework. Make sure it is installed.
    2. Write a Makefile with all the targets that you need (which are they?) to manage a single VM
    3. Can you manage multiple machines? How.

!!! note note "Assignment W4.3 VM on Chameleon Cloud"

    1. Pick a local VM framework. Make sure it is installed.
    2. Write a Makefile with all the targets that you need (which are they?) to manage a single VM

!!! note note "Assignment W4.4 Review Python"

    In preparation for the upcoming weeks, please review your python knowledge. You can any resource you like, but we have provided a large amount of information about python (which you do not need all of it.) Therefore we recommend to strategically review sections that will be instrumental to Clouds, DevOps, and AI.
    If there are any issues, please use Piazza to ask and we can narrow it down. This is a relatively simple activity and it should not take long. If it takes more than 3 hours  please use Piazza to find out where you may need some more help.

    Please review:
        
    1. Setting up  python virtual environment. 
        * You can use the one you use usually use such as venv or pyenv.
        * Typically we discourage using conda and miniconda due to the potential that 
            hundreds of unneeded libraries may be downloaded or a low level conflict may arise. For your project you will be asked not to use conda to keep the vms and containers clean. Use of conda has to be justified in a detailed justification and outline why other python virtualization technologies can not be used. 
        * please not that the openstack commandline tool must be installed with pipx 
    
        See: [link](/section/python/python-install.md/#venv)
    2. Using 
        
        * pip install
        * pipx install

        See: [link](/section/python/python-pipx.md)

    3. Review how to use import statements such as `os.system`
        Write a program that uses os.sytem("ls") (windows users must be in gitbash to make that work or in a vm using Linux.

    4. Review how to create a __main__ 

    5. Review how to write a function

    5. Review how to pass arguments to the python program from commandline.

    !!! tip 
        I recommend click instead of argparse as there is a direct correlation between function name and parameters. click provides ease augmentations befor the function to transform it for you to a commanline interface. In other frameworks you have to do much more.
            
        See: [link](/section/python/python-click.md)

    6. Review how to run shell commands from within python 

        See: [link](/Users/grey/work/cloudmesh-ai-lecture/docs/section/python/python-subprocess.md)

        Focus on `os.system()` and `supbrocess.run()`
    


## Week 3:  Due Sep 17, 2026, 9am


!!! tip "Keep this assignment simple" 

    Create the proper file specified under:

    * `<repo>/assignments/week3/`

    But make sure you do also the `README.md` update


!!! note "Assignment W3.1 VM on Jetstream Horizon"

    Start a vm on jetstream and follow the tutorial provided. If you see issues, improve the tutorial while creating pull requests in the Lecture notes.

    Document your activity with a screenshot of the terminal (800x600).

    Put the solution in file vms.md
    ```
    # Jestream VM

    ![Jetstream](jetstream.png)
    ```


!!! note "Assignment W3.2 VM on Chameleon Cloud Horizon"

    Although you may wish to use other clouds for your project, we want you to start up a single VM on Chameleon Cloud for a very brief time.

    Document your activity with a screenshot of the terminal (800x600).

    Tip: 
    
    1. Set your preferred time zone in Chameleon settings.
    2. Make sure you have a key in your .ssh dir on your laptop. Upload the public key to Chameleon.
    3. Before doing anything, explore the portal and browse around so you develop a plan for what you have to do.
    4. Only after you have developed a plan, do the reservation first. Make sure the reservation does not exceed 1 hour.
    5. Start up a VM using a Chameleon Cloud image for Ubuntu 24.04. Make sure to use the smallest image size possible for it (what size is that? It is part of your plan).

    Put the solution in file vms.md
    ```
    # Chamelon Cloud VM

    ![Chameleon](chameleon.png)
    ```


!!! note "Assignment W3.3: OPTIONAL: VM on public cloud"

    Create a VM on a cloud of your choice, such as AWS, Azure, or Google. Use the free tier.
    Document with screenshots how you created your account. Make sure you blur out sensitive information in the screenshot, including your name, credit card numbers and key, and other security details.

    Put the solution in file vms.md
    ```
    # XYZ VM

    ![XYZ](xyz.png)
    ```

!!! note "Assignment W3.4: Compare"

    Compare your experience between starting a VM on your local machine vs using Chameleon Cloud and Jetstream 2. If you did others also add them. 

    Put the solution in file vms.md
    ```
    # Comparing VM Creation

    write a nice comparision, do not use I
    ```


!!! note "Assignment W3.5: `README.md`"


    1. Please update the Readme using the following template

        * <https://github.com/cloudmesh-ai-luc/example/blob/main/README.md>

    2. Fill out the checkboxes. only fill them out when they are done. The have the purpose to selfevaluate and document the progress. you make.

    3. This is kept up to date by you every week from assignments posted in the Lecture notes. It is part of each weeks assignment. It is your responsibility. I will only review assignments that are linked to this document. So make sure the URLs are also included.
    
!!! note "Assignment W3.6 git from commandline"

    We created a project.md use th git command lines to sharpen your skills to do all git interactions from commandline. This is important as on cloud services we do not have GUIs and we need to use git form multiple services. Use:

    * Work with a fork (GUI)

    All these from commandline:
    
    * git clone
    * git commit -a
    * git commit -m "msg" file
    * git push
    * git pull

    * Create a pull request (GUI)
    * Accept a pull request (you can do that via GUI)

    !!! tip "set up your username email on any machine where you do git push. Also set up the editor.

~
## Week 2:  Due Sep 10, 2026, 9am

!!! note "Assignment W2.1: Google Account, Piazza Account post cleanup"

    1. Locate your Account post in Piazza
    2. Add your google account too your original post
    3. Correct your chameleon id which is for us the e-mail you registered with
    4. Fix your subject line to `Firstname Lastname (lucid@luc.edu)`

    **Solution Example**

    This is the subject line in the post:

    ```
    Albert Zweistein (azweistein@luc.edu)
    ```
    This is the message boddy in the post.

    ```
    class: 488
    Firstname: Albert
    Lastname: Zweistein
    LUC e-mail: azweistein@luc.edu
    chameleoncloud id: azweistein@luc.edu
    access id: azweistein
    github id: zweistein
    google email: zweistein-fake@gmail.com
    ```

    The post must be submitted to the accounts category.


!!! note "Assignment W2.2: GitHub Repository"

    1. You will be given a GitHub repository by the instructor. It is located at
       
        - <https://github.com/orgs/cloudmesh-ai-luc/repositories>
    
    2. Verify that you can write into a file in the directory. I suggest to put something useful into the README such as your first and lastname. 
    3. Upload your public key 

!!! note "Assignment W2.3: Backup Your Computer"

    Computers store the work, photos, and projects you’ve spent time creating including that of your classes. If a virus, hardware failure, or accidental delete occurs, those files can disappear forever. A regular backup gives you a safe copy that you can restore instantly, protecting both your effort and your grades. Think of a backup as a “reset button” that saves you from losing everything.
   
    1. Write a one‑paragraph explanation (4‑6 sentences) of why backing up of your own up a computer is important, using the ideas discussed earlier.

    2. List three real‑world consequences that apply to you of not having a backup (e.g., lost homework, corrupted projects, costly data recovery).

    3. Choose one backup method (external drive, cloud service, or built‑in OS tool) and outline very briefly the steps you would follow to set it up on your own computer.

    4. Create a weekly backup schedule (day, time, and what to back up). 

    5. Research an example from cloud Computing where a missing backup strategy lead to issues. (Example: Loss of data by NPR dur to Vendor shutting down [[1]](https://www.stlpr.org/news-briefs/2026-08-20/nine-pbs-70-years-programming-history)) 
    Are there other examples? Write a short incidence case and how it could have been avoided.
    
    **Submission:**  
    
    * <repo>/assignments/week2/backup.md

        1. Why is backing up important?
        2. Real world consequences applying to you.
        3. Which backup plan will you use?
        4. My plan to establish a backup schedule.
        5. Real world consequences applying to others.

    !!! warning 
        Backing up your computer could cost significant time. In the instructors case it took almost 2 days. So plan ahead and use days where you do not need your computer, or break the backup in smaller chinks. In some cases restrict the backup. If you use a physical backup drive, do not move your computer or drive during the backup.
        

!!! note "Assignment W.2.4: Local VM"

    **Goal:**  Set up a local virtual machine (VM) on your own computer, prove that you can log in, and produce a short, up‑to‑date tutorial that anyone else can follow.

    **Steps:**

    | # | Action | Details |
    |---|--------|---------|
    | **1** | **Install a terminal on Windows** | • Download & install **Git Bash** (or enable WSL). <br>• macOS and Linux already have a usable shell. |
    | **2** | **Pick a VM framework** | Choose a hypervisor that runs on your hardware and that you like. Typical options are: <br>• *VirtualBox* (free, cross‑platform) <br>• *VMware Workstation/Player* <br>• *Microsoft Hyper‑V* (Windows Pro) <br>• *Multipass* (lightweight CLI) <br>Make sure the download size fits on your drive. |
    | **3** | **Create and start a VM** | • Follow the hypervisor’s wizard or CLI to create a minimal VM (e.g., Ubuntu 22.04). <br>• Boot the VM, log in at least once, and verify that the terminal works. |
    | **4** | **Capture proof of login** | Take a screenshot of the VM’s terminal **≤ 800 × 600 px**. The image must show:<br>• Your prompt (username/hostname) <br>• At least one command you ran (e.g., `uname -a` or `ls -la`). |
    | **5** | **Write / update the tutorial** | • In your repository, create (or edit) a file named **`local-vm.md`**. <br>• The file should contain a concise, step‑by‑step guide that includes:<br>   1. Prerequisites (Git Bash, chosen hypervisor, etc.)<br>   2. Installation of the hypervisor<br>   3. VM creation commands (or GUI instructions) and how to log in<br>   4. The screenshot (embed it or link to `vm-login.png`)<br>   5. Any system‑specific quirks you encountered<br>   6. A “Contributing” section that tells others how to submit a PR if the official lecture notes need fixing. <br> **Note**: Do not waste your time to duplicate a tutorial if it is already in the Lecture Notes, create a pull request if you see something is wrong.|
    | **6** | **Submit** | • Add the screenshot (e.g., `vm-login.png`). <br>• Commit **`local-vm.md`** and the screenshot to your repository. <br>• If the lecture notes already contain a tutorial, verify it works on your machine. <br>   – If you found errors, open a pull request to correct them. <br>   – If it works, simply note any differences in your `local‑vm.md`. <br>• If no tutorial exists, your `local‑vm.md` becomes the canonical guide. |

    **Deliverables**

    Files are to be submitted into your repository.

    1. **`assignments/week1/local-vm.md`** – the complete, up‑to‑date tutorial,   
    2. **Screenshot** (`assignments/week1/vm-login.png`) showing a successful login inside the VM (≤ 800 × 600 px).  
    3. (Optional) A pull request against the lecture‑notes repository if you corrected an existing guide. (Gets extra points)

    **Grading Checklist**

    - [ ] Correct installation of Git Bash (Windows).  
    - [ ] Appropriate hypervisor selected and installed.  
    - [ ] VM created, started, and logged into successfully.  
    - [ ] Screenshot meets size & content requirements.  
    - [ ] `local‑vm.md` is clear, accurate, and includes any system‑specific notes.  
    - [ ] Proper commit/push of the markdown file and screenshot.  
    - [ ] If relevant, a well‑formatted PR to the lecture notes.

    **Tips**:

    - **CLI vs. GUI** – include the command‑line version of the VM creation steps (e.g., `VBoxManage …`) even if you used the GUI; it’s useful for automation.  
    - **Version info** – note the version numbers of the hypervisor and OS you used; future students can compare.  



!!! note "Assignment W2.4: Project proposal"

    Start working towards a project proposal. Work on it every week. A possible template for a proposal is at 
    
    * <https://github.com/cloudmesh-ai-luc/example/blob/main/project.md>

    Note that you can deviate from the format. The proposal, for example, ought to have an architectural diagram. Also, the description is not yet fully developed (it is just a sample template ;-) ). It is not expected that you have it worked out by next week, but that you have created some text and at least thought about the title and filled out the administrative fields.



## Week 1 (Past Due) Thursday, August, 2026, 9am

!!! note "Assignment W1.1. What hardware do you have?"

    Fill out the [LUC Hardware Questionnaire](https://docs.google.com/forms/d/e/1FAIpQLSdxxTnj8JFrrbREcM0wQ7B9nGmqpYfBPRddhKnGE7e7Dui_lA/viewform?usp=sharing&ouid=114251938823529916329)

!!! note "Assignment W1.2. Lecture review"

    Review all sections under LECTURES -> INTRODUCTIONS. 
    In case of questions, post them on Piazza.

!!! note "Assignment W1.3. Look over the assignment sections"

    Review all sections under ASSIGNMENTS, this includes the Overview section and the weekly section.

!!! note "Assignment W1.3. Create class accounts"

    a. Create an account on access-ci.org. 
    b. Create an account on chameleoncloud.org
    c.  Set up a GitHub account
    d. Make sure your Piazza account works by posting the account information to Piazza.


    Completion of the Account assignments

    Send a message to the account folder in "Piazza" with the following information. Please use the name registered with LUC. Please use the following format. 

    When submitting this post, make sure to select lecture/accounts. Make sure you use it as the subject. 

    ```
    Firstname Lastname (email@luc.edu)
    ```

    Once submitted, the results are in:
    [this link](https://piazza.com/class/mt5rkdsycb31c3#folder=logistics%E2%88%95accounts)
    ```
    class: 388 or 488 (use only one number)
    Firstname:
    Lastname:
    LUC e-mail/id: *this is an e-mail*
    chameleoncloud id: *this is an e-mail*
    access id: *this is not an e-mail*
    github id: *this is not an e-mail*
    google email: *this is an e-mail*
    ```

    To make it clear by example:

    ```
    Albert Zweistein (azweistein@luc.edu)
    ```
    
    ```
    class: 488
    Firstname: Albert
    Lastname: Zweistein
    LUC e-mail: azweistein@luc.edu
    chameleoncloud id: azweistein@luc.edu
    access id: azweistein
    github id: zweistein
    google email: zweistein-fake@gmail.com
    ```

    !!! info 
        The IDs on access, GitHub, and Chameleon may be different.



!!! note "Assignment W1.4. Work ahead: Refresh knowledge about Python and Linux"

    We will do some minimal Linux and Python in this class; if you want to work ahead, review some of the optional material in the class documentation. 

!!! note "Assignment W1.5. Improve the Web Site."

    During the entire semester: If you find errors, update them or let us know.
