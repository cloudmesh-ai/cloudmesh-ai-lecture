# Google Cloud Platform (GCP) Account Setup

This section explains how to establish a Google Cloud Platform account using the Free Trial and "Always Free" tier. It outlines the setup process, provides strategies for monitoring credits and setting budget alerts, and emphasizes the use of dedicated projects for resource isolation.

!!! info "Learning Objectives"

    After completing this chapter, you will be able to:
    - Set up a Google Cloud Platform (GCP) account using the Free Trial.
    - Configure budget alerts to prevent unexpected charges.
    - Identify and utilize "Always Free" tier resources.
    - Create a dedicated GCP project to isolate course resources.

## Overview

To participate in the course assignments using Google Cloud Platform (GCP), you will need a Google Cloud account. This guide focuses on leveraging the **GCP Free Trial** and the **Always Free** tier to explore cloud environments without incurring costs.

## Setup Process

1. **Visit GCP**: Go to the [Google Cloud Free Trial page](https://cloud.google.com/free).

2. **Create an Account**:
   - Click **Get started for free**.
   - Sign in with your Google account.

3. **Provide Information**:
   - Agree to the terms of service.
   - Provide your country and account type (Individual).

4. **Payment Information**:
   - **Important**: GCP requires a credit card or bank account for identity verification. Google will not charge you unless you manually upgrade your account to a paid subscription after the trial credits are exhausted.

5. **Verify Identity**:
   - Complete the required identity verification steps.

## Managing the Free Tier

To ensure you stay within the free limits and avoid charges:

- **Monitor Credits**: Keep an eye on your free trial credits in the **Billing** section of the GCP Console.

- **Set Budget Alerts**: Go to **Billing > Budgets & alerts** and create a budget to receive email notifications when your spending reaches a specific limit.

- **Use "Always Free" Resources**: Select machine types that fall under the "Always Free" tier (e.g., `e2-micro` in specific US regions).

- **Clean Up**: Delete your projects or specific instances when you are finished with an assignment to prevent ongoing costs.

## Post-Setup Configuration

Once your account is active:

1. Log in to the [Google Cloud Console](https://console.cloud.google.com/).

2. Create a new **Project** for your course work to keep resources isolated.

3. Follow the course modules to configure your network and launch your first VM instance.

## Summary Checklist

- [ ] GCP account created via the Free Trial page.
- [ ] Identity and payment verification completed.
- [ ] Budget alert configured in the Billing section.
- [ ] Dedicated course project created.
- [ ] Verified access to the Google Cloud Console.

## Assignments

!!! note "Assignment 1: Setup GCP Free Trial Account"

    **Goal**: Successfully create a GCP account and configure a budget alert.

    **Tasks**:
    1. Create a GCP account using the [Google Cloud Free Trial](https://cloud.google.com/free).
    2. Complete the identity verification and payment setup.
    3. Log in to the Google Cloud Console.
    4. Navigate to **Billing > Budgets & alerts** and create a budget alert for $1.00.
    5. Create a new project named `course-cloud-setup`.

    **Validation**:
    - The assignment is considered complete when you can log in to the console and provide a screenshot of your budget alert.
    - Verify that you can launch an `e2-micro` instance in a supported free-tier region.

??? tip "Solution: Budget Alerts"
    When creating the budget alert, set the threshold to a very low amount (e.g., $1.00) and ensure your email notifications are active. This provides an early warning system before any significant credits are consumed.

## References

- [Google Cloud Free Trial](https://cloud.google.com/free)
- [Google Cloud Console](https://console.cloud.google.com/)
- [GCP Free Tier Documentation](https://cloud.google.com/free/docs/free-cloud-features)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? question "Why does GCP require credit card information during the free trial setup?"
    GCP requires payment information for identity verification. Google will not charge the user unless they manually upgrade to a paid subscription after the free trial credits are exhausted.

??? question "How can you ensure you stay within the GCP Free Tier and avoid unexpected charges?"
    You can monitor credits in the Billing section, set budget alerts to receive email notifications, use 'Always Free' resources (like `e2-micro` in specific regions), and delete projects or instances when finished.

??? question "What is the purpose of creating a new project for course work in the GCP Console?"
    Creating a separate project helps keep course resources isolated from other projects, making it easier to manage and clean up resources.
