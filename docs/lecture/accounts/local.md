# Runing VMs locally 

!!! warning 
    you will need some additional material to decide which vm framework to use.For the impatient, one of the easiest to use is multipass which works on Linux, MacOS, Windows. However, it uses ubuntu images.

!!! info "Learning Outcomes"
    - Master local-first development practices to test code safely and avoid unexpected cloud costs.
    - Set up research and academic testbed accounts (Chameleon Cloud and Access-CI) for infrastructure experimentation.
    - Configure commercial cloud provider accounts (AWS, Azure, and GCP) to explore industry-standard free tiers and student credits.

# Setting Up Your Accounts

To participate in the hands-on portions of this course, you will need accounts for several cloud and infrastructure services. Please set these up as early as possible to avoid delays in your projects.

## 1. Local Development First

!!! important 
    Before deploying any resources to the cloud, it is strongly recommended that you develop and test your scripts, containers, and configurations on your own local computer.

Cloud resources, even within "free tiers," can incur costs if misconfigured or if you exceed the free limits. Testing locally (using tools like Docker or local virtual machines) ensures that your code is working correctly before you move it to a production or cloud environment where costs might be associated.

---

## Assignments

!!! assignment "Account: Local Virtual machines"
    1. Install a virtualization tool 
       1.1 decide which to use multipass, VirtualBox, VMware, other.
    2. Run a simple "Hello World" VM to ensure it is working.
    3. Verify that you have administrative rights to manage these resources.

!!! assignment "Account: Local Containers"
    1. Install Docker on your local machine.
    2. Run a simple "Hello World" container to ensure it is working.
    3. Verify that you have administrative rights to manage these resources.
