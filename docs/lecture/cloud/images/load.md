
```mermaid
graph LR
    %% Styles
    classDef internet fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b,font-weight:bold;
    classDef lb fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17,font-weight:bold;
    classDef asg fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20,font-weight:bold;
    classDef vm fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c,font-weight:bold;

    %% Nodes
    User(("🌐 - Internet <br> (Client Traffic)")):::internet
    LB["⚖️ - Load Balancer <br> (Distributes Traffic)"]:::lb
    ASG{{"🔄 - Auto-Scaling Group <br> (Policy & Scaling Engine)"}}:::asg
    
    subgraph VM Cluster [Virtual Machines Pool]
        direction TB
        VM1["🖥️  - VM Instance 1"]:::vm
        VM2["🖥️  - VM Instance 2"]:::vm
        VMi["🖥️  - ................"]:::vm
        VM3["🖥️  - VM Instance N"]:::vm
    end

    %% Flow Connections
    User -->|HTTPS Request| LB
    LB -->|Routes Traffic| ASG
    ASG --> VM1
    ASG --> VM2
    ASG --> VMi
    ASG --> VM3
 ```
