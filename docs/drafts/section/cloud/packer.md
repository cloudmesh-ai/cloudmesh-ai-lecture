# Image Orchestration with Packer {#sec:packer}

Packer is an open-source tool for creating identical machine images for multiple platforms from a single source configuration. Instead of manually installing software on a VM and then taking a snapshot, Packer allows you to codify the build process. This ensures that your development, staging, and production environments are identical.

Packer runs on every major operating system and can create images for various platforms in parallel based on a single configuration specification.

**Key Resources:**
*   [Packer Introduction](https://www.packer.io/intro)
*   [Official Documentation](https://developer.hashicorp.com/packer/docs)
*   [Common Use Cases](https://developer.hashicorp.com/packer/docs/concepts)

## Installation

Installation instructions for all platforms are available at the [official getting started guide](https://developer.hashicorp.com/packer/installs).

## How Packer Works

In previous sections, we used tools like Vagrant to launch a VM and then manually installed software (e.g., upgrading Python, installing `pip`). While this works for a single machine, it is inefficient for teams or large-scale deployments.

Imagine you have a "golden image" of Ubuntu 22.04 with all your project dependencies pre-installed. With Packer, you can define this state in a configuration file and tell Packer to:
1.  Launch a temporary VM on a provider (e.g., AWS, GCP, or VirtualBox).
2.  Run a series of "provisioners" (like shell scripts) to install software.
3.  Stop the VM and save it as a reusable machine image (e.g., an Amazon AMI or a GCP Image).
4.  Destroy the temporary VM.

## Example Implementation (HCL2)

Modern Packer uses **HCL (HashiCorp Configuration Language)** instead of JSON for better readability. Below is an example of a Packer template (`ubuntu_dev.pkr.hcl`) that creates a development image on Google Compute Engine.

### 1. Configuration File (`ubuntu_dev.pkr.hcl`)

```hcl
# Define variables for flexibility
variable "project_id" {
  type    = string
  default = "your-project-id"
}

# Source block: Define where the image comes from and where it goes
source "googlecompute" "ubuntu-dev" {
  project_id   = var.project_id
  source_image = "ubuntu-2204-lts"
  ssh_username = "packer"
  zone         = "us-central1-a"
  image_name   = "ubuntu-2204-dev-image"
}

# Build block: Define the provisioning steps
build {
  sources = ["source.googlecompute.ubuntu-dev"]

  # Shell provisioner to install dependencies
  provisioner "shell" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y python3-pip python3-dev build-essential",
      "echo \"alias python='python3'\" >> ~/.bashrc"
    ]
  }
}
```

### 2. Running the Build

To build the image, run the following command in your terminal:

```bash
packer build -var "project_id=my-cloud-project" ubuntu_dev.pkr.hcl
```

Packer will automatically handle the creation of the temporary instance, run the shell commands, create the image, and clean up the resources.

## Multi-Platform Builds

One of Packer's greatest strengths is the ability to target multiple clouds simultaneously. By adding another `source` block (e.g., for `amazon-ebs`), you can create an AWS AMI and a GCP Image from the same provisioning script.

### Example AWS Source Block

```hcl
source "amazon-ebs" "ubuntu-dev-aws" {
  ami_name      = "ubuntu-2204-dev-ami"
  instance_type = "t2.micro"
  region        = "us-west-2"
  source_ami    = "ami-xxxxxxxxxxxxxxxxx" # Replace with current Ubuntu 22.04 AMI ID
  ssh_username  = "ubuntu"
}
```

By adding this to the `sources` list in the `build` block, Packer will launch instances in both GCP and AWS and provision them identically.

## Exercises

!!! assignment "Exercise 1: Packer Installation"
    Install Packer on your local machine and verify the installation by running `packer version`.

!!! assignment "Exercise 2: Image Creation"
    Using a provider of your choice (VirtualBox, AWS, or GCP), create a Packer template that builds an Ubuntu 22.04 image with the following installed:
    1. `git`
    2. `curl`
    3. `python3-pip`

!!! assignment "Exercise 3: Multi-Cloud Strategy"
    Research how to use **Ansible** as a Packer provisioner instead of simple shell scripts. Write a short paragraph explaining the advantages of using a configuration management tool over shell scripts for image building.

!!! assignment "Exercise 4: Image Validation"
    After building your image, launch a VM from that image and verify that all the software specified in your Packer template is present and correctly configured.