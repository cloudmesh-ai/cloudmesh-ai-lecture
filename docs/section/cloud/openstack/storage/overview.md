---
title: "OpenStack Storage Overview: Cinder, Swift, and Glance"
---

# OpenStack Storage Overview: Cinder, Swift, and Glance

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this section, you will be able to:
    - Distinguish between block, object, and image storage within the OpenStack ecosystem.
    - Compare the architectural goals and access patterns of Cinder, Swift, and Glance.
    - Apply a decision framework to select the appropriate storage service based on a set of technical requirements.
    - Understand the interdependencies between Glance and the underlying storage backends.
    - Identify how these services are implemented and utilized on the Chameleon and Jetstream platforms.

## Overview

OpenStack does not provide a single "storage service." Instead, it implements a diverse storage ecosystem designed to handle fundamentally different data access patterns. While Cinder, Swift, and Glance all store bytes on disk, they differ in how that data is organized, how it is accessed, and the specific problem they solve.

At a high level:
- **Cinder** provides virtual hard disks for virtual machines.
- **Swift** provides a scalable, distributed key-value store for unstructured data.
- **Glance** provides a catalog of virtual machine blueprints (images).

## Understanding Storage Types: Block vs. Object

Before exploring the specific OpenStack services, it is essential to understand the two primary paradigms of data storage: **Block** and **Object**.

### What is Block Storage?
Block storage breaks data into fixed-size chunks called "blocks." Each block has its own unique address, and the operating system manages these blocks as a single contiguous disk.

- **How it works**: The storage is presented to the host as a raw, unformatted device. The user must choose a filesystem (like ext4 or XFS) to organize the blocks into files and folders.
- **Key Advantage**: **Performance.** Because it provides low-level access to the disk, it is incredibly fast for random read/write operations.
- **Key Trade-off**: **Coupling.** Block storage must be "attached" or "mounted" to a specific server to be usable.
- **Real-world Example**: A physical hard drive, an SSD, or an AWS EBS volume.

### What is Object Storage?
Object storage treats data as discrete "objects." Each object contains the data itself, a variable amount of metadata (labels describing the data), and a unique identifier. All objects are stored in a flat namespace (no folders, only "containers").

- **How it works**: Data is accessed via a REST API over HTTP. You don't "mount" object storage; you simply request an object by its URL (e.g., `GET /container/my-photo.jpg`).
- **Key Advantage**: **Scalability.** Because it doesn't rely on a complex filesystem hierarchy, it can scale horizontally across thousands of servers to hold petabytes of data.
- **Key Trade-off**: **Latency.** It is slower than block storage for small, frequent updates because every access requires an HTTP request.
- **Real-world Example**: Amazon S3, Google Cloud Storage, or Dropbox.

### Block vs. Object Comparison

| Feature | Block Storage | Object Storage |
| :--- | :--- | :--- |
| **Data Organization** | Fixed-size blocks | Discrete objects + Metadata |
| **Access Method** | OS-level (Filesystem mount) | API-level (HTTP/REST) |
| **Structure** | Hierarchical (Folders/Files) | Flat (Containers/Objects) |
| **Performance** | High IOPS, Low Latency | High Throughput, Higher Latency |
| **Scalability** | Limited by volume size | Virtually unlimited (Horizontal) |

## Core Storage Services

### Cinder: Block Storage
Cinder is the OpenStack implementation of **Block Storage**. It provides virtual hard disks (volumes) that behave exactly like physical disks.

- **Analogy**: Like an external USB hard drive or a SAN LUN.
- **Access Pattern**: The VM's operating system sees a SCSI or VirtIO device. The user formats it with a filesystem (e.g., ext4, XFS) and mounts it.
- **Key Characteristics**: 
    - Low latency and high IOPS.
    - Strong consistency.
    - Tight coupling with the compute instance (must be attached to be accessed).
- **Primary Use Cases**: Database data files, application logs, and persistent OS boot disks.

### Swift: Object Storage
Swift is the OpenStack implementation of **Object Storage**. It provides a distributed, highly durable store for unstructured data.

- **Analogy**: Like AWS S3, Google Cloud Storage, or Dropbox.
- **Access Pattern**: Accessed via HTTP requests (GET, PUT, DELETE) using a URL. It is not "attached" to a VM; any client with the correct credentials can access the data over the network.
- **Key Characteristics**:
    - Massive horizontal scalability (petabytes of data).
    - Eventual consistency.
    - High durability through replication across multiple nodes and zones.
- **Primary Use Cases**: Static website assets (images, videos), large-scale backups, and unstructured data lakes.

### Glance: Image Service
Glance is the **Image Service**. While it is not "block" or "object" storage in the traditional sense, it is a specialized catalog that manages VM templates. Under the hood, Glance typically uses either Swift or Cinder to store the actual image bytes.

- **Analogy**: A library of ISO images or VM templates.
- **Access Pattern**: The Nova compute service requests an image from Glance, which streams it to the compute node to create a new disk.
- **Key Characteristics**:
    - Optimized for read-heavy workloads.
    - Supports various image formats (qcow2, raw, vmdk).
    - Decouples the image definition from the actual storage implementation.
- **Primary Use Cases**: Storing a pre-configured Ubuntu or Windows image that will be used as the base for hundreds of instances.

## Comparative Analysis

The following table summarizes the fundamental differences between the three services.

| Feature | Cinder (Block) | Swift (Object) | Glance (Image) |
| :--- | :--- | :--- | :--- |
| **Unit of Storage** | Volume | Object (Blob) | Image |
| **Access Method** | Attached Block Device | REST API (HTTP) | REST API / Internal |
| **Interface** | Filesystem (mount) | Key-Value / URL | Image Catalog |
| **Performance** | High (Low Latency) | Moderate (High Throughput) | Low (Sequential Read) |
| **Consistency** | Strong | Eventual | Strong (for metadata) |
| **Scalability** | Vertical / Backend | Massive Horizontal | Moderate |
| **VM Relationship** | Attached to 1 or more VMs | Independent of VMs | Base for new VMs |

### Platform Implementation: Chameleon & Jetstream

While the OpenStack specifications are standard, the way these services are exposed and billed varies by platform. The table below maps these storage services to the specific environments used in this course.

| Service | Storage Type | Jetstream 2 | Chameleon | Primary Role / Platform Note |
| :--- | :--- | :--- | :--- | :--- |
| **Glance** | Image | Yes (Public/Private) | Yes (`CC-` images) | Manages boot images. Chameleon uses the `CC-` prefix for official images. |
| **Cinder** | Block | Yes (Billable) | Yes | Persistent disks. Jetstream explicitly bills for Cinder volumes and snapshots. |
| **Swift** | Object | Yes | Yes | Distributed storage for unstructured data and large-scale backups. |

## Decision Guide: Which Storage to Use?

Choosing the right storage service depends on how the data will be accessed and the required performance characteristics.

### Use Cinder When...
- You need a disk for a **database** (e.g., MySQL, PostgreSQL) where low latency is critical.
- You need **persistent storage** that survives the deletion of the VM it is attached to.
- You need to perform **high-speed random I/O**.
- You require a filesystem that can be mounted and managed by the OS.

### Use Swift When...
- You are storing **unstructured data** (e.g., user profile pictures, log archives).
- You need to store **massive amounts of data** (TBs to PBs) across many servers.
- The data needs to be **accessed via the web** without mounting a disk.
- You prioritize **durability and availability** over raw latency.

### Use Glance When...
- You need to store a **template** for a virtual machine.
- You are managing **OS images** that will be used to boot new instances.
- You need a centralized repository for **disk images** of different versions (e.g., Ubuntu 20.04 vs 22.04).

### Decision Matrix Summary

| Requirement | Recommended Service | Why? |
| :--- | :--- | :--- |
| "I need a disk for my DB" | **Cinder** | Low latency, strong consistency, block access. |
| "I need to store 1M photos" | **Swift** | Scalability, HTTP access, object storage. |
| "I need a base OS image" | **Glance** | Specialized for VM templates and spawning. |
| "I need a backup repo" | **Swift** | Durability, massive scale, easy API access. |
| "I need a shared volume" | **Cinder** | Block storage with multi-attach (backend dependent). |

## Summary Checklist

- [ ] Differentiate between Block, Object, and Image storage.
- [ ] Map Cinder, Swift, and Glance to their respective storage types.
- [ ] Identify the primary access method for each service (Mount vs API).
- [ ] Match a specific use case (e.g., "Database") to the correct service.
- [ ] Explain the relationship between Glance and its backends (Swift/Cinder).
- [ ] Identify how Glance and Cinder are utilized on Chameleon and Jetstream.

## Assignments

!!! note "Assignment.1: Scenario Analysis"
    For each of the following requirements, identify which OpenStack storage service is most appropriate and justify your answer:
    1. A company needs to store 50TB of historical logs for compliance.
    2. A developer needs a high-performance disk for a Redis cache.
    3. An administrator needs to provide a standard "Company Gold Image" for all new developer VMs.
    4. A web application needs to store user-uploaded PDF resumes.

??? tip "Solution: Scenario Analysis"
    1. **Swift**: Historical logs are unstructured, massive in scale, and don't require low-latency block access.
    2. **Cinder**: Redis requires high-performance, low-latency block storage.
    3. **Glance**: Gold images are the primary purpose of the Image service.
    4. **Swift**: PDF uploads are objects that are best served via API/HTTP.

!!! note "Assignment.2: Architecture Design"
    Design the storage layer for a typical three-tier web application consisting of:
    - A set of stateless Web Servers.
    - An Application Server.
    - A relational Database (PostgreSQL).
    - A repository for static images and CSS.

??? tip "Solution: Architecture Design"
    - **Web/App Servers**: Use **Glance** for the base OS image to ensure all servers are identical.
    - **Database**: Use **Cinder** for the data volume to ensure high IOPS and persistence.
    - **Static Assets**: Use **Swift** for the images and CSS to allow global access and easy scaling.

## References

- [OpenStack Storage Documentation](https://docs.openstack.org/storage/)
- [Cinder Project Page](https://docs.openstack.org/cinder/latest/)
- [Swift Project Page](https://docs.openstack.org/swift/latest/)
- [Glance Project Page](https://docs.openstack.org/glance/latest/)

## Self-Evaluation

??? note "What is the fundamental difference between Block Storage (Cinder) and Object Storage (Swift)?"
    Block storage presents data as raw volumes that must be formatted with a filesystem and attached to a VM, providing low-latency access. Object storage stores data as discrete objects with metadata in a flat namespace, accessed via a REST API over HTTP, providing massive scalability and durability.

??? note "Can Glance exist without Cinder or Swift?"
    While Glance manages the image metadata and catalog, it requires a storage backend to hold the actual image bytes. In most deployments, Glance uses either Swift (for distributed storage) or Cinder (for block-based storage) as its backend.

??? note "Why would you use Swift for backups instead of Cinder snapshots?"
    Cinder snapshots are typically used for point-in-time recovery of a specific volume and are often stored on the same backend. Swift is designed for long-term, highly durable, and geographically distributed storage, making it superior for off-site backups and archival.
