# Horizon

To create a virtual machine using the **OpenStack Horizon dashboard** with a specific network, security group, and SSH key, follow these steps through the web user interface:

## 1. Navigate to Instances

1. Log in to your Horizon dashboard and make sure you have selected the correct project from the dropdown menu at the top left.
2. In the left-hand sidebar, expand **Compute** and click on **Instances**.
3. Click the **Launch Instance** button in the upper-right corner.

---

## 2. Configure the Launch Instance Tabs

A multi-step wizard will appear. Fill out the required tabs:

* **Details Tab**
* **Instance Name**: Enter a name for your virtual machine.
* **Flavor**: Select the virtual hardware size (vCPUs, RAM, disk).


* **Source Tab**
* **Select Boot Source**: Choose **Image**.
* Locate your desired boot image (e.g., Ubuntu) in the *Available* table and click the **`+`** icon to move it to *Allocated*.


* **Networking Tab**
* Find your target private or shared network in the *Available* table and click the **`+`** icon to add it to *Allocated*.


* **Security Groups Tab**
* Select the security group containing your inbound rules (such as SSH port 22 access) and click the **`+`** icon to move it to *Allocated*.


* **Key Pair Tab**
* Select your pre-registered SSH key pair and click the **`+`** icon to allocate it. *(If you haven't created one yet, you can click the `+` button next to the dropdown to create or import a new key pair right inside the wizard).*



---

## 3. Launch the Instance

1. Review your configurations across the tabs.
2. Click the **Launch Instance** button in the lower-right corner.

Horizon will queue the request, and within a few moments, the instance status will change to **Active**. You can then assign a floating IP via the actions dropdown menu if you need external public internet access.