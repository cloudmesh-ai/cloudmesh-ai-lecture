# AWS Account Setup

This section provides a comprehensive guide to setting up an AWS account using the Free Tier to minimize costs. It includes instructions for creating a billing alarm, configuring an administrative IAM user, and managing resources to stay within free limits.

!!! info "Learning Objectives"
    By the end of this section, you will be able to:
    - Create and verify an AWS account using the Free Tier.
    - Configure billing alarms to prevent unexpected costs.
    - Establish a secure administrative IAM user for daily operations.

## Overview

To participate in the course Assignments using Amazon Web Services (AWS), you require an AWS account. This guide outlines the process for setting up an account utilizing the AWS Free Tier to minimize or eliminate costs during your studies.

## Step-by-Step Setup Process

1. **Visit AWS**: Navigate to the [AWS Free Tier page](https://aws.amazon.com/free/).

2. **Create an Account**:
   - Click **Create a Free Account**.
   - Enter your email address and an account name.
   - Verify your email address using the code sent to you.
   - Set a strong root password.

3. **Provide Contact Information**:
   - Select **Personal** for the account type.
   - Enter your contact details.

4. **Payment Information**:
   - AWS requires a credit or debit card for identity verification and to cover charges if Free Tier limits are exceeded. You will not be charged unless usage exceeds these limits.

5. **Identity Verification**:
   - AWS verifies identity via a phone call or SMS.

6. **Choose a Support Plan**:
   - Select the **Basic Support - Free** plan.

## Managing the Free Tier

To maintain Free Tier status and avoid unexpected charges:

- **Monitor Usage**: Use the [AWS Billing Dashboard](https://console.aws.amazon.com/billing/home) to track resource consumption.

- **Set Billing Alarms**: Create a billing alarm in AWS Budgets to trigger an email notification when spending exceeds a low threshold (e.g., $1).

- **Utilize Free Eligible Resources**: When launching instances, select resources marked as **"Free tier eligible"** (e.g., `t2.micro` or `t3.micro` depending on the region).

- **Resource Cleanup**: Terminate instances, delete volumes, and remove elastic IPs immediately upon completing an Assignment.

## Initial Configuration

Once the account is active:

1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).

2. Create an **IAM User** with administrative permissions for daily tasks to avoid using the Root account.

3. Follow the course modules to configure your Virtual Private Cloud (VPC) and launch your first instance.

## Summary Checklist

- [ ] AWS Account created and verified.
- [ ] Basic Support plan selected.
- [ ] Billing alarm configured for $1.00.
- [ ] Administrative IAM User created.
- [ ] Root account access secured (MFA recommended).

## Assignments

!!! note "Assignment.1: Setup AWS Free Tier Account"
    **Goal**: Successfully create an AWS account and configure a billing alarm to protect against charges.

    **Tasks**:
    1. Create an AWS account using the [AWS Free Tier](https://aws.amazon.com/free/).
    2. Complete identity verification and payment setup.
    3. Log in to the AWS Management Console.
    4. Navigate to **AWS Budgets** and create a budget alert for $1.00.
    5. Create an **IAM User** with `AdministratorAccess` for course work.

    **Validation**:
    - Submission of a screenshot showing the $1.00 budget alarm.
    - Successful launch of a `t2.micro` (or equivalent free-tier) instance.

    ??? tip "Solution: Setup AWS Free Tier Account"
        Ensure you use a personal email for the account. When creating the budget, choose "Cost budget" and set the amount to 1.00 USD. For the IAM user, attach the `AdministratorAccess` managed policy directly to the user or a group they belong to.

## References

- [AWS Free Tier Documentation](https://aws.amazon.com/free/)
- [AWS Billing and Cost Management](https://aws.amazon.com/aws-cost-management/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## Self-Evaluation

??? note "What is the recommended way to avoid costs when using AWS for course Assignments?"
    Utilize the AWS Free Tier and select resources explicitly marked as "Free tier eligible" (e.g., `t2.micro` or `t3.micro`).

??? note "Why is creating an IAM User preferred over using the Root account for daily tasks?"
    IAM users provide granular access control and reduce the risk of accidental, critical changes to the account, enhancing overall security.

??? note "What steps prevent unexpected charges in AWS?"
    Monitoring usage via the Billing Dashboard, configuring AWS Budgets alarms (e.g., $1 threshold), and terminating all resources (instances, volumes, elastic IPs) after use.
