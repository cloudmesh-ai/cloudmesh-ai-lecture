# Azure Account Setup

This guide provides a detailed walkthrough for setting up a Microsoft Azure account, focusing on the Azure Free Account and Azure for Students offers. It covers the registration process, cost management through budget alerts, and the organization of cloud resources using Resource Groups.

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    - Create and verify a Microsoft Azure account.
    - Configure budget alerts to manage costs.
    - Organize cloud resources using Resource Groups.

## Overview

To participate in the course assignments using Azure, you will need an Azure account. This guide focuses on leveraging the **Azure Free Account** and the **Azure for Students** offer to obtain a cloud environment at no cost.

## Step-by-Step Setup Process

1. **Visit Azure**: Go to the [Azure Free Account page](https://azure.microsoft.com/free/).

2. **Create an Account**:
    - If you have a university email, try the [Azure for Students](https://azure.microsoft.com/free/students/) offer, which often provides free credits without requiring a credit card.
    - Otherwise, click **Start free** and sign in with a Microsoft account.

3. **Provide Information**:
    - Enter your identity and contact details.

4. **Payment Verification**:
    - For the standard free account, Azure requires a credit card for identity verification. You will not be charged until your free credits are exhausted or you upgrade to a paid plan.

5. **Verify Identity**:
    - Complete the phone or email verification process.

## Cost Management and the Free Tier

To avoid unexpected charges:

- **Use the Cost Management + Billing Tool**: Monitor your spending and remaining credits via the [Azure Portal](https://portal.azure.com/).

- **Set Budget Alerts**: Create a budget in the **Cost Management** section to receive notifications when your spending reaches a certain percentage of your budget.

- **Select Free Services**: Choose services labeled as **"Free for 12 months"** or **"Always free"** when creating resources.

- **Clean Up**: Delete resource groups when you are finished with an assignment to ensure all associated resources are removed.

## Post-Setup Actions

Once your account is active:

1. Log in to the [Azure Portal](https://portal.azure.com/).

2. Explore the **Resource Groups** concept to organize your course work.

3. Follow the course modules to create your first Virtual Machine.

## Summary Checklist

- [ ] Azure account created or Azure for Students activated.
- [ ] Identity verification completed.
- [ ] Budget alert configured in Cost Management + Billing.
- [ ] Resource Group `course-cloud-setup` created.

## Assignments

!!! note "Assignment 1: Setup Azure Free Account"
    **Goal**: Successfully create an Azure account (or activate Azure for Students) and configure a budget alert.

    **Tasks**:
    1. Create an Azure account using the [Azure Free Account](https://azure.microsoft.com/free/) or [Azure for Students](https://azure.microsoft.com/free/students/).
    2. Complete the identity verification process.
    3. Log in to the Azure Portal.
    4. Navigate to **Cost Management + Billing** and set up a budget alert.
    5. Create a new **Resource Group** named `course-cloud-setup`.

    **Validation**:
    - The assignment is considered complete when you can log in to the portal and provide a screenshot of your budget alert.
    - Verify that you can create a small Virtual Machine (e.g., B1s) within your resource group.

??? tip "Solution: Setup Azure Free Account"
    Verify your account status in the Azure Portal under "Subscriptions". Ensure your budget alert is set to a low threshold (e.g., $1.00) to receive immediate notification of any charges.

## References

- [Azure Free Account Documentation](https://azure.microsoft.com/free/)
- [Azure for Students](https://azure.microsoft.com/free/students/)
- [Azure Portal](https://portal.azure.com/)

## Self-Evaluation

??? note "What is the 'Azure for Students' offer and how does it differ from the standard free account?"
    The Azure for Students offer often provides free credits without requiring a credit card, whereas the standard free account requires a credit card for identity verification.

??? note "How can you avoid unexpected charges in Microsoft Azure?"
    Users should use the Cost Management + Billing tool to monitor spending, set budget alerts, select services labeled as "Free for 12 months" or "Always free", and delete resource groups when finished.

??? note "What is the purpose of using Resource Groups in Azure?"
    Resource Groups are used to organize and manage related resources for a specific project or environment, making it easier to deploy and delete them as a single unit.

