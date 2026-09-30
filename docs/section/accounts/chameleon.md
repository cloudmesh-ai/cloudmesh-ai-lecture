# Chameleon Cloud Account Setup

This document details the application process for obtaining an account on the Chameleon Cloud testbed for research and education. It provides step-by-step instructions for registration, guidelines for ensuring application approval, and post-approval configuration steps.

!!! info "Learning Objectives"

    By the end of this section, you will be able to:
    - Navigate the Chameleon Cloud registration and application process.
    - Provide the necessary institutional and project-specific information for account approval.
    - Access the Horizon Dashboard and verify project membership.

## Overview

To participate in course Assignments requiring a public cloud environment, you require an account on [Chameleon Cloud](https://chameleoncloud.org). Chameleon Cloud is a specialized testbed designed for cloud computing research and education, providing access to both virtualized and bare metal infrastructure.

## Step-by-Step Application Process

1. **Visit the Website**: Navigate to [chameleoncloud.org](https://chameleoncloud.org).

2. **Create an Account**:
   - Select the **Sign Up** or **Register** button.
   - Create a unique username and password.

3. **Complete the Application**:
   Chameleon Cloud requires an application to verify that resources are used for legitimate research or educational purposes.
   - **Personal Information**: Provide your full name and institutional email address (university email).
   - **Institutional Affiliation**: Enter your university and department.
   - **Project Description**:
     - For students, state that you are enrolled in the "Cloud Computing/DevOps/AI" course.
     - Explain that the account is required for course Assignments and labs focusing on cloud infrastructure, virtualization, and automation.

4. **Submission and Review**:
   - Submit the application for review by Chameleon Cloud administrators.
   - Approval typically takes several business days. You will receive a confirmation email upon activation.

## Guidelines for Approval

To increase the likelihood of prompt approval:

- **Use Institutional Email**: Applications using `.edu` or university-provided email addresses are prioritized. Applications from generic providers (e.g., `@gmail.com`, `@yahoo.com`) are subject to higher scrutiny or rejection.

- **Provide Specificity**: Avoid generic descriptions. Instead of stating "for a class," specify the course name/number, the university, and the technical topics being studied (e.g., "OpenStack," "Bare Metal servers").

## Post-Approval Configuration

Once the account is activated:

1. Log in to the [Chameleon Cloud Portal](https://chameleoncloud.org/login).

2. Use the **Horizon Dashboard** to create virtual instances or request bare metal nodes.

3. Follow subsequent course modules to configure the environment and establish SSH connectivity.

## Summary Checklist

- [ ] Application submitted via institutional email.
- [ ] Project description includes course and university details.
- [ ] Account activation email received.
- [ ] Login to Horizon Dashboard verified.
- [ ] Membership in the `cloudmesh` project confirmed.

## Assignments

!!! note "Assignment.1: Chameleon Cloud Account"

    **Goal**: Successfully apply for a Chameleon Cloud account and request access to the course project.

    **Tasks**:
    1. Navigate to [chameleoncloud.org](https://chameleoncloud.org) and begin the registration process.
    2. Complete the application using an **institutional email address**.
    3. In the project description, clearly state enrollment in the **LUC 2026 Cloud Computing/DevOps/AI** course.
    4. Explicitly request to be added to project `cloudmesh` (ID: `CH-817419`).
    5. Submit the application and retain a record of the submission.

    **Validation**:
    - Receipt of the approval email from Chameleon Cloud.
    - Verification of the `cloudmesh` project within the Horizon Dashboard project list.

    ??? tip "Solution: Chameleon Cloud Account"
        When filling out the project description, be as explicit as possible about the academic nature of the request. Ensure the project ID `CH-817419` is correctly cited to avoid manual routing delays.

## References

- [Chameleon Cloud Homepage](https://chameleoncloud.org)
- [Chameleon Cloud User Guide](https://docs.chameleoncloud.org)
- [OpenStack Horizon Documentation](https://docs.openstack.org/horizon/)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? question "What is Chameleon Cloud and who is it intended for?"
    Chameleon Cloud is a cloud computing testbed specifically intended for research and education, providing infrastructure for legitimate academic and research purposes.

??? question "Why is using an institutional email address critical for the application?"
    Institutional emails (e.g., `.edu`) serve as a primary verification method for academic status, making these applications more likely to be approved than those from generic email providers.

??? question "What specific details should be included in the project description to ensure approval?"
    Students should include the exact course name (e.g., "Cloud Computing/DevOps/AI"), the university name, and the specific technical goals, such as learning cloud infrastructure and automation.
