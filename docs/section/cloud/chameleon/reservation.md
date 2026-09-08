
**Short answer:**  
Yes – the “reservation” capability that you see on the Chameleon Cloud is provided by **Blazar**, the official OpenStack *Reservation Service*. It is a fully‑supported, upstream OpenStack project, but it is an **optional add‑on** (not part of the core services such as Nova, Neutron, Cinder, etc.).  

Below is a quick rundown of what Blazar is, its OpenStack‑project status, and how Chameleon uses it.

---

## 1️⃣ What is the OpenStack “Reservation” service?

| Name (code name) | Official project name | Primary purpose |
|------------------|----------------------|-----------------|
| **Blazar** | **OpenStack Blazar – Reservation Service** | Allows users (or administrators) to **reserve compute, block‑storage, and network resources for a future time window**. |
| **Key features** | • Create *leases* → a lease is a time‑bounded reservation <br>• Reserve specific **flavors**, **hosts**, **networks**, **volumes**, etc. <br>• Enforce quotas and avoid over‑commit during the lease window <br>• REST API (and Horizon panels) for users to manage leases |

*Why it exists:* OpenStack’s core services allocate resources **immediately** when a server/volume/network is created. In research and education clouds (e.g., Chameleon, Jetstream, NSF clouds) users often need to **book resources ahead of a scheduled experiment or class**, and Blazar supplies that capability.

---

## 2️⃣ OpenStack project status

| Milestone | Status in OpenStack |
|-----------|--------------------|
| **Incubator** | Introduced in the *2016* *OpenStack Kilo* cycle as an incubated project. |
| **Integrated** | Graduated to **“Integrated”** status in the *OpenStack Pike* release (2017). |
| **Supported** | Since then it has been **maintained and released** in every subsequent release (Queens → Yoga → Z → 2025‑Q1). |
| **Core vs. Optional** | It ships as a **stand‑alone service** (its own API endpoint, database, and service processes). Clouds can enable it or leave it out – it is **not a mandatory component** of a vanilla OpenStack deployment. |
| **Documentation** | Official docs: <https://docs.openstack.org/blazar/latest/> |
| **Code repo** | <https://opendev.org/openstack/blazar> (GPL‑2.0) |

Thus, while Blazar is an official, upstream OpenStack project with a stable API, its **adoption is optional** and depends on whether a cloud operator wants to expose reservation capabilities.

---

## 3️⃣ How Chameleon Cloud uses Blazor (Blazar)

| Aspect | Details |
|--------|---------|
| **Service name in the UI** | “Reservations” or “Leases” (visible in the Horizon dashboard under *Project → Reservations*). |
| **What can be reserved** | • Compute nodes (specific flavors or even particular hosts) <br>• Block‑storage volumes <br>• Network ports / sub‑nets (rarely exposed) |
| **Typical workflow** | 1. **Create a lease** → specify start time, end time, and resource requirements. <br>2. Once the lease becomes active, the reserved resources behave like normal Nova/Neutron/Cinder resources. <br>3. After the lease expires, the resources are automatically released back to the pool. |
| **Why Chameleon needs it** | Researchers schedule experiments weeks in advance; the reservation system guarantees that the required number of CPUs, RAM, and GPUs will be available at the exact time the experiment starts. |
| **Quota integration** | Blazar enforces the user’s OpenStack quota **at lease‑creation time**, preventing users from over‑booking the cloud. |
| **Implementation** | Chameleon runs a Blazar API service, a Scheduler service, and a database (usually MySQL). The Horizon UI ships the “Reservation” panel, and the CLI commands are under `openstack reservation …` (e.g., `openstack reservation lease create …`). |

---

## 4️⃣ Is it “fully supported” by OpenStack?

* **Upstream support:** Yes. The OpenStack PTL (Project Technical Lead) for Blazar actively maintains the code, publishes release notes, and fixes bugs in each cycle. It receives the same testing, CI, and cross‑project integration as the core services.
* **Compatibility:** It works with Nova, Cinder, Neutron, and Placement. When a lease is created, Blazar talks to the Placement service to **allocate inventory** for the requested time window, and then it issues the actual Nova/Neutron calls when the lease becomes active.
* **Community backing:** Blazar has a dedicated mailing list, weekly IRC/Matrix meetings, and is represented at the OpenStack Summit. Many large academic clouds (Chameleon, Jetstream, XSEDE, GARR Cloud, etc.) run it in production.
* **Limitations:** Because it is optional, not every OpenStack deployment includes it. Also, certain advanced features (e.g., reservations of IPv6 prefixes, per‑host affinity) are still evolving, so the documentation occasionally warns about “feature in progress”.

---

## 5️⃣ Quick cheat‑sheet for a Chameleon user

```bash
# List your current leases
openstack reservation lease list

# Create a simple compute lease (example: 2 m1.medium VMs for 4 hours starting tomorrow)
openstack reservation lease create \
  --name my‑experiment \
  --resource-type compute \
  --resource-quantity 2 \
  --resource-flavor m1.medium \
  --start-date "$(date -d '+1 day' --utc +%Y-%m-%dT%H:%M:%SZ)" \
  --end-date "$(date -d '+1 day +4 hour' --utc +%Y-%m-%dT%H:%M:%SZ)"

# Show details of a lease
openstack reservation lease show <LEASE_ID>

# Delete a lease (if you no longer need it)
openstack reservation lease delete <LEASE_ID>
```

---

## 6️⃣ TL;DR

* **Blazar** is the official OpenStack **Reservation Service**.
* It is **maintained upstream**, releases with every OpenStack version, and is considered a **supported** OpenStack project.
* It is **optional** – clouds decide whether to deploy it. Chameleon Cloud **does** deploy it, exposing “Reservations/Leases” to its users.
* The service lets you **book compute, storage, or network resources ahead of time**, integrating with the core services and respecting quotas.

If you need to verify whether a specific OpenStack deployment (e.g., a private cloud you manage) includes reservations, look for a service named **blazar** in the service catalog:

```bash
openstack service list | grep blazar
```

Presence of an entry indicates that the reservation capability is installed and ready to use.


!!! Learning Objectives  

1. Define the role of the OpenStack Reservation Service (Blazar) and its integration points with Nova, Placement, and other core services.  
2. Locate the Blazar endpoint in an OpenStack service catalog (`openstack service list`).  
3. Create, query, and delete a lease using the OpenStack CLI (`openstack reservation lease …`).  
4. Explain how a lease is transformed into regular Nova/Neutron resources when it becomes active.  
5. Verify Placement quota limits before creating a lease to avoid over‑booking.  
6. Choose appropriate flavors for a reservation based on CPU, RAM, and disk requirements (using a flavor‑listing helper).  
7. Perform a clean‑up that restores quota after lease deletion.

---  

!!! Assignments  

| # | Task | Success criteria (pass) | Points |
|---|------|--------------------------|--------|
| 1 | Verify Blazar is running (`openstack service list`). | Service named **blazar** (or **reservation**) appears and is `enabled`. | 5 |
| 2 | Generate a markdown table of available flavors (use a helper script). | Table with columns **Name**, **RAM (GB)**, **VCPU**, **Disk (GB)** printed to stdout. | 10 |
| 3 | Create a lease for **2 × m1.medium** VMs, 3 h duration, starting 1 h from now. | Lease command returns an ID; `openstack reservation lease show <ID>` shows `status = PENDING`. | 15 |
| 4 | Start the lease immediately (set start = now) and confirm two VMs are created and tagged with the lease ID. | `openstack server list` shows two new servers; their description contains the lease ID. | 15 |
| 5 | Deploy a simple workload (e.g., Docker + nginx) on one of the leased VMs and verify via HTTP. | `curl http://<floating‑IP>` returns the nginx welcome page. | 15 |
| 6 | Delete the lease before it expires and verify the VMs disappear and the flavor quota is restored. | `openstack reservation lease delete <ID>` succeeds; no servers from that lease remain; flavor usage returns to pre‑lease level. | 10 |
| 7 | Write a ~200‑word reflection on why reservations are critical for research clouds and how quota enforcement works across Nova + Placement + Blazar. | Paragraph submitted with required length and content. | 10 |
| **Total** | | | **80** |

