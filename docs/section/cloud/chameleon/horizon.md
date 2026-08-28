# Chameleon Cloud – Horizon Quick‑Start Guide

---

## Prerequisites
- A **Chameleon Cloud** account with an active project.  
- A **public SSH key** uploaded to the portal (Settings → Key Pairs).  
- Sufficient credit / quota for at least one small instance.  
- Your local machine’s **time zone** correctly set (the portal uses UTC).  

---

## System Use & Policy
!!! warning "System Use & Policy"
    * **Scheduled maintenance** – Check the *Maintenance* banner in the portal; plan your work around it.  
    * **Support** – I am not a Chameleon Cloud administrator. If you need assistance, use the integrated **Help** form.  
    * **Course usage** – Do not use this resource for other classes. Your other professor can create a dedicated project and add you as a member. It is common  that you may belong to multiple projects. In that case make sure you associate the resources with the correct project.

---

## Getting Started – Step‑by‑Step

### 1. Create a reservation
1. In the Horizon sidebar, go to **Project → Compute → Reservations**.  
2. Click **Create Reservation**.  
3. Fill the form as follows:  

   | Field            | Recommended value                                                                  |
   |------------------|------------------------------------------------------------------------------------|
   | **Name**         | `demo‑reservation‑<your-luc-email-id-before-at>`                                                  |
   | **Start time**   | *Current time + 1 min* (the portal will auto‑populate)                             |
   | **End time**     | `0` (means “no explicit end”)                                                      |
   | **Duration**     | `1 h` (maximum for small experiments)                                              |
   | **Time zone**    | Select your local time zone                                                         |
   | **Image**        | Choose an image with the **CC‑** prefix, e.g. **CC‑ubuntu‑24.04**                  |
   | **Network**      | **shared** (default)                                                               |
   | **Flavor**       | `a2.tiny` (or any small flavor)                                                   |

!!! info "Tip"
    Keep the reservation ≤ 1 hour to avoid quota conflicts.  

!!! info 
    For The official documentation on reservation please look at:

    * [Overview](https://chameleoncloud.readthedocs.io/en/latest/technical/reservations)
    * GUI: [link](https://chameleoncloud.readthedocs.io/en/latest/technical/reservations/gui_reservations.html)
    * Commandline: [link](https://chameleoncloud.readthedocs.io/en/latest/technical/reservations/cli_reservations.html)

### 2. Navigate to Instances
1. Verify the correct **project** is selected in the top‑left dropdown.  
2. Open the left‑hand menu → **Compute → Instances**.  
3. Click the **Launch Instance** button (top‑right).  

### 3. Configure the Launch Instance wizard
#### Details tab
- **Instance Name** – e.g., `my‑test‑vm`.  
- **Flavor** – choose a small flavor (e.g., `a2.tiny`).  

#### Source tab
- **Select Boot Source** → **Image**.  
- Locate the image you chose in the reservation (e.g., **CC‑ubuntu‑24.04**) and click the **`+`** button to move it to *Allocated*.

#### Networking tab
- Locate the **shared** network (or a private network you own).  
- Click the **`+`** button to allocate it.

#### Security Groups tab
- Choose a group that permits **SSH (port 22)** inbound traffic.  
- Click **`+`** to allocate it.

#### Key Pair tab
- Select the SSH key you uploaded earlier.  
- If none appears, click the **`+`** next to the dropdown to **Create / Import** a new key pair directly from this wizard.

### 4. Launch the instance
1. Review every tab to confirm the settings are correct.  
2. Press **Launch Instance** (bottom‑right).

> **Result** – The instance will appear in the Instances list with status **BUILD** → **ACTIVE** in a few moments.

---

## Assign a floating IP (optional)
A floating (public) IP lets you reach the VM from outside the private cloud network, which is required for SSH or any web service you want to expose to the internet.  

1. In **Instances**, click the dropdown next to your VM → **Associate Floating IP**.  
2. Choose an available floating IP or click **Allocate New Floating IP**.  
3. Confirm. You can now SSH to the VM using the floating IP address.

---

## Cleanup (avoid lingering charges)

| Action                | How to perform |
|-----------------------|----------------|
| **Terminate VM**      | Instances → select the VM → **Delete Instance** |
| **Release reservation** | Reservations → select the reservation → **Delete** |
| **Remove key pair** (if no longer needed) | Access & Security → Key Pairs → delete the entry |

---

## Troubleshooting

| Symptom                     | Likely cause                              | Fix |
|-----------------------------|-------------------------------------------|-----|
| *VM stuck in BUILD*         | Reservation not active or quota exceeded  | Verify the reservation window, increase quota, or delete other running VMs. |
| *SSH “Connection refused”* | No floating IP attached or security group missing port 22 | Attach a floating IP and ensure the security group allows inbound TCP 22. |
| *Image not listed*          | Wrong image prefix or wrong project       | Use a **CC‑**‑prefixed image and confirm the project selection. |
| *Time‑zone mismatch*        | Portal using UTC while you entered local time | Double‑check the **time zone** field in the reservation form. |

---

## Further reading
- [Chameleon Cloud Documentation – Horizon UI](https://chameleoncloud.org/docs/horizon/)  
- [OpenStack Horizon User Guide](https://docs.openstack.org/horizon/latest/)  
- [Chameleon Cloud Help Form](https://chameleoncloud.org/help/)
