# Google Cloud Platform (GCP) Account Setup

!!! warning "Draft"
    This guide is to be completed by students of the class who have chosen to use Google Cloud Platform (GCP) for their cloud environment. It has not yet been tested.

To participate in the course exercises using GCP, you will need a Google Cloud account. We recommend using the **GCP Free Trial** and the **Always Free** tier.

## Step-by-Step Setup Process

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

## Focusing on the Free Tier

To ensure you stay within the free limits and avoid charges:
- **Monitor Credits**: Keep an eye on your free trial credits in the **Billing** section of the GCP Console.
- **Set Budget Alerts**: Go to **Billing > Budgets & alerts** and create a budget to receive email notifications when your spending reaches a specific limit.
- **Use "Always Free" Resources**: Select machine types that fall under the "Always Free" tier (e.g., `e2-micro` in specific US regions).
- **Clean Up**: Delete your projects or specific instances when you are finished with an exercise to prevent ongoing costs.

## After Setup

Once your account is active:
1. Log in to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new **Project** for your course work to keep resources isolated.
3. Follow the course modules to configure your network and launch your first VM instance.

---

!!! assignment \"Assignment: Setup GCP Free Trial Account\"

    **Goal**: Successfully create a GCP account and configure a budget alert.

    ### Tasks:

    1. [ ] Create a GCP account using the [Google Cloud Free Trial](https://cloud.google.com/free).
    2. [ ] Complete the identity verification and payment setup.
    3. [ ] Log in to the Google Cloud Console.
    4. [ ] Navigate to **Billing > Budgets & alerts** and create a budget alert for $1.00.
    5. [ ] Create a new project named `course-cloud-setup`.

    ### Validation:

    - The assignment is considered complete when you can log in to the console and provide a screenshot of your budget alert.
    - Verify that you can launch an `e2-micro` instance in a supported free-tier region.
