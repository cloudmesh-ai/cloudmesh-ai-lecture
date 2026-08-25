# AWS Account Setup

!!! warning "Draft"
    This guide is to be completed by students of the class who have chosen to use Amazon Web Services (AWS) for their cloud environment. It has not yet been tested.

To participate in the course exercises using AWS, you will need an AWS account. We recommend using the **AWS Free Tier** to avoid costs.

## Step-by-Step Setup Process

1. **Visit AWS**: Go to the [AWS Free Tier page](https://aws.amazon.com/free/).
2. **Create an Account**:
   - Click **Create a Free Account**.
   - Enter your email address and an account name.
   - Verify your email address with the code sent to you.
   - Set a strong root password.
3. **Provide Contact Information**:
   - Select **Personal** for the account type.
   - Enter your contact details.
4. **Payment Information**:
   - **Important**: AWS requires a credit or debit card for identity verification and to cover any charges if you exceed the Free Tier limits. You will not be charged unless you go beyond the free limits.
5. **Identity Verification**:
   - AWS will verify your identity via a phone call or SMS.
6. **Choose a Support Plan**:
   - Select the **Basic Support - Free** plan.

## Focusing on the Free Tier

To ensure you stay within the Free Tier and avoid unexpected charges:

- **Monitor Usage**: Use the [AWS Billing Dashboard](https://console.aws.amazon.com/billing/home) to track your usage.
- **Set Billing Alarms**: Create a billing alarm in AWS Budgets to notify you via email when your spending exceeds a small threshold (e.g., $1).
- **Stick to Free Eligible Resources**: When launching instances, always look for the **"Free tier eligible"** label (e.g., `t2.micro` or `t3.micro` depending on the region).
- **Clean Up**: Always terminate instances, delete volumes, and remove elastic IPs when you are finished with an exercise.

## After Setup

Once your account is active:

1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Create an **IAM User** with administrative permissions instead of using the Root account for daily tasks (Best Practice).
3. Follow the course modules to configure your VPC and launch your first instance.

---

!!! assignment "Assignment: Setup AWS Free Tier Account"

    **Goal**: Successfully create an AWS account and configure a billing alarm to protect against charges.

    **Tasks:**

    1. [ ] Create an AWS account using the [AWS Free Tier](https://aws.amazon.com/free/).
    2. [ ] Complete the identity verification and payment setup.
    3. [ ] Log in to the AWS Management Console.
    4. [ ] Navigate to **AWS Budgets** and create a budget alert for $1.00.
    5. [ ] Create an **IAM User** with `AdministratorAccess` for your course work.

    **Validation:**

    - The assignment is considered complete when you can log in to the console and provide a screenshot of your $1.00 budget alarm.
    - Verify that you can launch a `t2.micro` (or equivalent free-tier) instance.
