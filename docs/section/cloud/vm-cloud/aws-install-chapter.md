# AWS CLI Installation and Free-Tier Setup

!!! info "Learning Objectives"
    * Create and configure a free AWS account.
    * Establish an IAM user with programmatic access for CLI operations.
    * Install the AWS CLI using isolated methods to prevent system pollution.
    * Provision essential EC2 resources, including key pairs and security groups.
    * Launch and connect to a free-tier Amazon Linux 2 instance via SSH.
    * Implement a resource cleanup workflow to avoid unexpected charges.

    ## Overview

    This chapter provides a step-by-step guide to deploying a virtual machine on AWS using the Command Line Interface (CLI). It covers the entire lifecycle from account creation to resource termination, emphasizing the use of the AWS Free Tier and isolated tool installations to maintain a clean workstation environment.

    ## Core Sections

    ### Account Setup and IAM Configuration

    To interact with AWS via the CLI, you must first establish an account and a secure identity.

    #### AWS Free Tier Account

    The AWS Free Tier provides a limited set of resources for 12 months. Key offerings include:

    | Resource | Limit | Usage Note |
    |----------|-------|-------------|
    | t2.micro / t3.micro Instance | 750 hours/month | One instance at a time |
    | Amazon S3 | 5 GB Standard storage | Backups and static sites |
    | Amazon RDS | 750 hours of db.t2.micro | Optional database usage |
    | AWS Lambda | 1 M requests | Serverless functions |

    To create an account:
    1. Visit <https://aws.amazon.com/> and select **Create a Free Account**.
    2. Provide an email, password, and account name.
    3. Enter billing information for identity verification (a small temporary authorization may occur).
    4. Select **Basic Support** (Free).
    5. Complete phone verification and sign in as the **root user**.

    #### Programmatic Access via IAM

    Using the root user for daily tasks is a security risk. Instead, create an Identity and Access Management (IAM) user.

    1. Navigate to the **IAM** console: <https://console.aws.amazon.com/iam/>.
    2. Select **Users → Add user**.
    3. Set a user name (e.g., `mycli-user`) and enable **Programmatic access** to generate an Access Key ID and Secret Access Key.
    4. Under **Permissions**, choose **Attach policies directly** and search for **AmazonEC2FullAccess**.
    5. Create the user and download the `.csv` file containing the credentials.

    #### Local Credential Storage

    Configure the CLI to use a specific profile for the free tier:

    ```bash
    aws configure --profile free
    # Enter the following when prompted:
    # AWS Access Key ID      (from CSV)
    # AWS Secret Access Key  (from CSV)
    # Default region name    (e.g., us-east-1)
    # Default output format  json
    ```

    This creates `~/.aws/credentials` with a `[free]` profile. All subsequent commands should include `--profile free`.

    ### AWS CLI Installation

    To avoid conflicting with system Python installations, use one of the following isolated installation methods.

    #### Docker Isolation

    This method ensures the CLI runs in a container, mounting only necessary directories.

    ```bash
    # Pull the official image
    docker pull amazon/aws-cli

    # Create a wrapper script for direct 'aws' command access
    cat <<'EOF' > ~/bin/aws
    #!/usr/bin/env bash
    docker run --rm -it \
      -v "$HOME/.aws:/root/.aws:ro" \
      -v "$HOME/.ssh:/root/.ssh:ro" \
      -v "$(pwd):/aws" \
      amazon/aws-cli "$@"
    EOF
    chmod +x ~/bin/aws
    export PATH=$HOME/bin:$PATH
    ```

    #### Official Bundle Installer

    Use the native binary installer for Linux or macOS.

    ```bash
    # Linux (x86_64)
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install --install-dir /opt/aws-cli --bin-dir /usr/local/bin

    # macOS
    brew install awscli
    ```

    #### pipx Sandbox

    Use `pipx` to install the CLI in an isolated Python environment.

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    pipx install awscli
    ```

    Verify the installation with `aws --version`.

    ### Resource Provisioning

    Launching an instance requires a key pair for authentication and a security group for network access.

    #### Key Pair Generation

    ```bash
    KEY_PATH=~/.ssh/free-key.pem
    aws ec2 create-key-pair \
      --key-name free-key \
      --query "KeyMaterial" \
      --output text \
      --profile free > $KEY_PATH
    chmod 400 $KEY_PATH
    ```

    #### Security Group Configuration

    Configure a group to allow SSH traffic (port 22).

    ```bash
    # Retrieve the default VPC ID
    VPC_ID=$(aws ec2 describe-vpcs \
      --query "Vpcs[0].VpcId" \
      --output text \
      --profile free)

    # Create the security group
    SG_ID=$(aws ec2 create-security-group \
      --group-name free-sg \
      --description "Free-tier SG (SSH)" \
      --vpc-id $VPC_ID \
      --profile free \
      --output text)

    # Open port 22 to all IP addresses
    aws ec2 authorize-security-group-ingress \
      --group-id $SG_ID \
      --protocol tcp \
      --port 22 \
      --cidr 0.0.0.0/0 \
      --profile free
    ```

    #### Launching the Instance

    Deploy a `t2.micro` instance using the latest Amazon Linux 2 AMI.

    ```bash
    # Retrieve the latest Amazon Linux 2 AMI ID
    AMI_ID=$(aws ec2 describe-images \
      --owners amazon \
      --filters "Name=name,Values=amzn2-ami-hvm-2.0.*-x86_64-gp2" "Name=state,Values=available" \
      --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
      --output text \
      --profile free)

    # Run the instance
    INSTANCE_ID=$(aws ec2 run-instances \
      --image-id $AMI_ID \
      --instance-type t2.micro \
      --key-name free-key \
      --security-group-ids $SG_ID \
      --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=free-demo}]' \
      --query "Instances[0].InstanceId" \
      --output text \
      --profile free)

    echo "Instance launched: $INSTANCE_ID"
    ```

    ### Connectivity and Management

    Once launched, the instance must be initialized before connection.

    #### Fetching the Public IP

    ```bash
    aws ec2 wait instance-running \
      --instance-ids $INSTANCE_ID \
      --profile free

    PUBLIC_IP=$(aws ec2 describe-instances \
      --instance-ids $INSTANCE_ID \
      --query "Reservations[0].Instances[0].PublicIpAddress" \
      --output text \
      --profile free)

    echo "Public IP: $PUBLIC_IP"
    ```

    #### SSH Connection

    Connect using the private key created earlier. The default username for Amazon Linux 2 is `ec2-user`.

    ```bash
    ssh -i ~/.ssh/free-key.pem ec2-user@$PUBLIC_IP
    ```

    #### Management Commands

    | Goal | Command |
    |------|---------|
    | List instances | `aws ec2 describe-instances --profile free --output table` |
    | Stop instance | `aws ec2 stop-instances --instance-ids $INSTANCE_ID --profile free` |
    | Start instance | `aws ec2 start-instances --instance-ids $INSTANCE_ID --profile free` |
    | Terminate VM | `aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free` |
    | Check Spend | `aws ce get-cost-and-usage --time-period Start=$(date -d 'first day of month' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics UnblendedCost --profile free` |

    ### Resource Cleanup

    To avoid charges, all provisioned resources must be removed.

    ```bash
    # Terminate the instance
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free
    aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID --profile free

    # Delete the key pair and remove local file
    aws ec2 delete-key-pair --key-name free-key --profile free
    rm -f ~/.ssh/free-key.pem

    # Delete the security group
    aws ec2 delete-security-group --group-id $SG_ID --profile free
    ```

    ### Deployment Cheat Sheet

    This consolidated block provides the entire workflow in one sequence.

    ```bash
    # 1. Install isolated CLI (Docker)
    cat <<'EOF' > ~/bin/aws
    #!/usr/bin/env bash
    docker run --rm -it \
      -v "$HOME/.aws:/root/.aws:ro" \
      -v "$HOME/.ssh:/root/.ssh:ro" \
      -v "$(pwd):/aws" \
      amazon/aws-cli "$@"
    EOF
    chmod +x ~/bin/aws
    export PATH=$HOME/bin:$PATH

    # 2. Configure IAM profile
    aws configure --profile free

    # 3. Create key pair and security group
    KEY=~/.ssh/free-key.pem
    aws ec2 create-key-pair --key-name free-key --query "KeyMaterial" --output text --profile free > $KEY && chmod 400 $KEY

    VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text --profile free)
    SG_ID=$(aws ec2 create-security-group \
      --group-name free-sg \
      --description "Free tier SG" \
      --vpc-id $VPC_ID \
      --profile free \
      --output text)

    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --profile free

    # 4. Launch t2.micro (Amazon Linux 2)
    AMI_ID=$(aws ec2 describe-images \
      --owners amazon \
      --filters "Name=name,Values=amzn2-ami-hvm-2.0.*-x86_64-gp2" "Name=state,Values=available" \
      --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
      --output text \
      --profile free)

    INSTANCE_ID=$(aws ec2 run-instances \
      --image-id $AMI_ID \
      --instance-type t2.micro \
      --key-name free-key \
      --security-group-ids $SG_ID \
      --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=free-demo}]' \
      --query "Instances[0].InstanceId" \
      --output text \
      --profile free)

    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --profile free
    PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
      --query "Reservations[0].Instances[0].PublicIpAddress" --output text --profile free)

    echo "Instance $INSTANCE_ID ready -> $PUBLIC_IP"

    # 5. SSH into the instance
    ssh -i $KEY ec2-user@$PUBLIC_IP

    # 6. Clean up when finished
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free
    aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID --profile free
    aws ec2 delete-security-group --group-id $SG_ID --profile free
    aws ec2 delete-key-pair --key-name free-key --profile free
    rm -f $KEY
    ```

    ## Summary Checklist

    * [ ] AWS account created and verified.
    * [ ] IAM user created with `AmazonEC2FullAccess`.
    * [ ] AWS CLI installed via an isolated method.
    * [ ] AWS CLI configured with a `[free]` profile.
    * [ ] Key pair and security group provisioned.
    * [ ] t2.micro instance launched and reachable via SSH.
    * [ ] All resources terminated and deleted.

    ## Assignments

!!! note "Assignment.1: Full Pipeline Deployment"
    Execute the complete workflow: install the CLI, configure your IAM profile, launch a free-tier instance, and connect via SSH. Verify the instance is running by executing `uname -a` on the remote machine.

??? tip "Solution: Full Pipeline Deployment"
    Follow the "Deployment Cheat Sheet" section. Ensure you use the `--profile free` flag for all CLI commands and use the correct private key for SSH.

!!! note "Assignment.2: Installation Diversification"
    If you used Docker for the CLI installation, repeat the setup using `pipx`. Compare the experience of using a native binary versus a containerized wrapper.

??? tip "Solution: Installation Diversification"
    Run `python3 -m pip install --user pipx` followed by `pipx install awscli`. Test the installation using `aws --version`.

!!! note "Assignment.3: Network Expansion"
    Modify the security group to allow inbound traffic on port 80 (HTTP). Launch a simple web server on your instance (e.g., using `python3 -m http.server 80`) and verify you can reach the instance's public IP in a web browser.

??? tip "Solution: Network Expansion"
    Run `aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --profile free`. Once connected via SSH, start the server with `sudo python3 -m http.server 80`.

    ## References

    * AWS CLI Reference - <https://docs.aws.amazon.com/cli/latest/reference/>
    * AWS Free Tier Details - <https://aws.amazon.com/free/>
    * Amazon Linux 2 User Guide - <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-linux-ami-basics.html>
    * IAM Best Practices - <https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html>
    * EC2 Instance Connect - <https://aws.amazon.com/ec2/instance-connect/>

    ## Self-Evaluation

??? note "Why is it recommended to create an IAM user instead of using the root account for CLI access?"
    The root account has unrestricted access to all AWS resources, including billing. If root credentials are leaked, the entire account is compromised. IAM users allow for the application of the principle of least privilege, granting only the specific permissions (e.g., `AmazonEC2FullAccess`) required for the task.

??? note "What is the benefit of installing the AWS CLI via Docker or pipx?"
    Installing tools globally can lead to dependency conflicts between different Python packages on the host system. Docker provides total isolation by running the CLI in a container, while `pipx` creates a dedicated virtual environment for each application, ensuring that the AWS CLI's dependencies do not interfere with other projects.

??? note "How can you ensure that you do not exceed the AWS Free Tier limits?"
    Regularly monitor the AWS Billing Dashboard and use the `aws ce get-cost-and-usage` command to check the current month's spend. Additionally, always terminate instances and delete unused security groups or elastic IPs immediately after use to prevent accumulating billable hours.
