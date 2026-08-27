# Assignments and Project Guidelines

To ensure a high standard of technical rigor and innovation, please adhere to the following requirements for all course assignments and your final project:

- **Timely Completion:** All assignments must be submitted by the specified deadlines to receive full credit. Late submissions will incur a penalty of 10% deduction per week.

## Project Scope and Innovation

- **Project Approval:** Throughout the semester the students will work with the instructor to obtain a project approval.

- **Prohibited Topics:** Projects centered on *recommender system analysis* are strictly disallowed. As these are frequently covered in introductory courses, you are expected to pursue more original and technically challenging research directions. We may add additional topics as they arise, so share your information early.

- **Novelty:** Projects should address a specific, non-trivial problem. This could involve benchmarking a specific AI model across different cloud architectures, implementing a custom distributed system, or optimizing a high-performance computing (HPC) workflow. Simply "deploying a website" is not sufficient. As stated in the University Policies, the same project cannot be submitted in multiple classes. You are, however, required to provide significant extensions.

- **Automation Requirement:** You may utilize any cloud service provider; however, the deployment and management of containers or Virtual Machines (VMs) must be **fully automated**.

- **CLI vs. GUI:** Interactions must be possible via Command Line Interface (CLI) or API. If you believe a Graphical User Interface (GUI) is indispensable for a specific task, you must provide a technical justification within your documentation.

- **Reproducibility:** A project is only as good as its documentation. You must provide a `README.md` and automation scripts (e.g., Terraform, Ansible, or Shell scripts) that allow a grader to recreate your entire environment and results with a single command or a clearly defined sequence of non-interactive steps.

- **Version Control:** You must use Git for every assignment. Commit early and   
  often. This acts as both a backup and a "paper trail" of your progress.

    !!! note "Repository"
        You will be provided an open source git repository set up by the instructor.

## Resource Management and Liability

- **Local Computer:** You are allowed to use your local computer to simulate a cloud.

- **Liability of Use:** Using employer-provided equipment for coursework often violates corporate IT policies and "Acceptable Use" agreements. The university and the instructor are not responsible for any disciplinary actions taken by your employer resulting from the use of company hardware for this course.

- **Hardware Alternatives:** While Raspberry Pis are great for learning, consider "Mini PCs" (used enterprise small-form-factor PCs) for local cloud simulation. They offer significantly more compute power, RAM, and virtualization support (VT-x/AMD-V) for a similar price point. However, they must support virtualization in some form.


- **Cost Responsibility:** Students are solely responsible for any costs incurred
  through the use of remote or cloud resources. 
  
- **Resource Abuse:** If you exhaust the class-assigned resources on access-ci or chameleon cloud and impact other students due to careless resource management, you will receive an "F" (this is standard practice at universities in cloud computing classes). However, this is very unlikely as we explicitly state this policy and we are sure you will avoid this as it is easy to do!  

    !!! note "The incident by an inconsiderate student."

        I previously did not have this policy, but a single student abused the system and used up 20,000 hours of compute time in a couple of days, despite the fact that he was reminded multiple times to shut down his cloud resources. Due to the shared nature of the account with all students, all students in the class lost access to the cloud resources. When confronted on the first day he started the resources, his argument was "No I will not shut down the resources as it took me too much time to start them." Later on I worked with the cloud provider and we looked into his computational load and found out it was 0. He started thousands of VMs and did not even use them.
        Due to this incident and the student's disregard for others in the class, it is best to protect other students with such a policy. 

        Since it has been in place, no other student has ever done this as it is easy to avoid. It remains the sole student. Since I had not established an explicit policy, I also did not give the student an F like he would have with other professors.


- **Understand the cost models:**

As you are in charge of your commercial cloud credits make sure you understand the cost model carefully.

- **Data**: Do not upload data by accident to your repository. Github is extremely limited. This includes containers, and virtual machines. Instead you need to upload the scripts that create and manage them. Make sure to utilize .gitignore


## Security

- **Security Protocols:** It is your responsibility to implement best practices for identity protection (e.g., managing API keys, using IAM roles, and setting up billing alerts) to prevent unauthorized access or unexpected charges. You will get a grade reduction if you store passwords or sensitive credentials in a public online repository such as GitHub and DockerHub.

- **Data Privacy and Ethics:** If your project involves collecting or using datasets, you must ensure they are either public domain or that you have the rights to use them. Do not upload sensitive personal data or proprietary company information to public cloud buckets or repositories.

## Collaboration

You are able to collaborate with others on a project or assignment. The size and complexity should match the group size. At this time the group limit is two.

## Tips

- **Backup:** Back up your computer before the class starts and do it regularly throughout the semester. Evaluate the options you have local SSD/HDD, cloud storage, GitHub. WHich system you use depends on you. Often the free tiers on cloud storage services are enough.

- **Reuse:** You can often use an old computer for other things, I for example used to do a lot on Raspberry Pis, but I think there are better options nowadays. I even used an EV3 Lego robot to interface via Python to and from external resources. However this class will need more then a Lego robot.

- **LLMs as Assistants, Not Authors:** While Large Language Models can be helpful for debugging or clarifying concepts, they frequently hallucinate technical specifications or use outdated API syntax. You are responsible for the correctness of all code and documentation. Using LLM-generated content without verification—especially regarding security configurations—is a high-risk strategy that often leads to system failure or security breaches.

- **Credit Monitoring:** If you use "Free Tiers" from providers (AWS, Azure, GCP), be aware that they often expire or have strict usage limits. Set up **Billing Alarms** on day one. You may have to research this yourself as it may not be covered on day one in class. It could be a valuable contribution to the class to develop a tutorial for others on this.

