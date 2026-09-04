# Assignments

!!! warning "All assignments are due on *Thursdays 9am*. This is 9am in the morning so i can attempt to review your assignments before class"

!!! warning "Do not start VMs or containers or use other resources from access-ci jetstream or chameleon cloud yet."

!!! info "Temawork is allowed on any assignment."

    You are allowed to work in a team. This may be done either remotely or via in-person meetings. When working in teams, you need to provide documentation of who did what. Teams can be different for different assignments. Some homework may foster ad-hoc teams that utilize the same platform or operating system. Just make sure you do not just blindly replicate somone elses work. If you work on a team, please put that in your assignment solution and describe who did what.


## Week 3:  Due Sep 17, 2026, 9am

??? note "Click here to see a draft version of the Assignments Week 3, Sept 17, 2026 (not yet due)"
    !!! note "Assignment W3.1 VM on Chameleon Cloud"

        Although you may wish to use other clouds for your project, we want you to start up a single VM on Chameleon Cloud for a very brief time.

        Document your activity with screenshots.

        Tip: 
        
        1. Set your preferred time zone in Chameleon settings.
        2. Make sure you have a key in your .ssh dir on your laptop. Upload the public key to Chameleon.
        3. Before doing anything, explore the portal and browse around so you develop a plan for what you have to do.
        4. Only after you have developed a plan. Do the reservation first. Make sure the reservation does not exceed 1 hour.
        5. Start up a VM using a Chameleon Cloud image for Ubuntu 24.04. Make sure to use the smallest image size possible for it (what size is that? It is part of your plan).

    !!! note "Assignment W3.2 VM on Jetstream"

        Start a vm on jetstream and follow the tutorial provided. If you see issues. Improve the tutorial while createing pull requests in the Lecture notes.

    !!! note "Assignment W3.3: OPTIONAL: VM on public cloud"

        Create a VM on a cloud of your choice, such as AWS, Azure, or Google. Use the free tier.
        Document with screenshots how you created your account. Make sure you blur out sensitive information in the screenshot, including your name, credit card numbers and key, and other security details.

    !!! note "Assignment W3.4: Compare"

        Compare your experience between starting a VM on your local machine vs using Chameleon Cloud.

        2. Put the results of your assignments in a structured fashion into the repository. While creating filenames and directories

        Example: assignments/week1/w3.3-compare

        (All filenames and dir names for assignments must be lower case.)
    

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
    chameloncloud id: azweistein@luc.edu
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

    1. **`assignment/week1/local-vm.md`** – the complete, up‑to‑date tutorial,   
    2. **Screenshot** (`assignment/week1/vm-login.png`) showing a successful login inside the VM (≤ 800 × 600 px).  
    3. (Optional) A pull request against the lecture‑notes repository if you corrected an existing guide. (Gets extra points)

    **Grading Checklist**

    - [ ] Correct installation of Git Bash (Windows).  
    - [ ] Appropriate hypervisor selected and installed.  
    - [ ] VM created, started, and logged into successfully.  
    - [ ] Screenshot meets size & content requirements.  
    - [ ] `local‑vm.md` is clear, accurate, and includes any system‑specific notes.  
    - [ ] Proper commit/push of the markdown file and screenshot.  
    - [ ] If relevant, a well‑formatted PR to the lecture notes.

    **Tips:

    - **CLI vs. GUI** – include the command‑line version of the VM creation steps (e.g., `VBoxManage …`) even if you used the GUI; it’s useful for automation.  
    - **Version info** – note the version numbers of the hypervisor and OS you used; future students can compare.  



!!! note "Assignment W2.4: Project proposal"

    Start working towards a project proposal. Work on it every week. A possible template for a proposal is at 
    
    * <https://github.com/cloudmesh-ai-luc/example/blob/main/project.md>

    Note that you can deviate form the format. The proposal for example aught to have an architectural diagram, Also the description is not yet fully developed (It is just a sample template ;-) ) It is not expected that you have it worked out by next week, but that you have created some text nd at least though t about the title and filled out the administartive fields.



## Week 1 (Past Due) Thursday, August, 2026, 9am {#assignment-week1}

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
    chameloncloud id: *this is an e-mail*
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
    chameloncloud id: azweistein@luc.edu
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
