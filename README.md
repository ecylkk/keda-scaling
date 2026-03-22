# Event-Driven Pod Autoscaler (KEDA & Redis)

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)
![KEDA](https://img.shields.io/badge/KEDA-event--driven-orange.svg)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)

An enterprise demonstration of **FinOps and Cost Optimization** utilizing [KEDA (Kubernetes Event-driven Autoscaling)](https://keda.sh/) to dynamically scale worker pods based on the length of a Redis task queue.

Unlike standard HPA (Horizontal Pod Autoscaler) which reacts slowly to CPU/Memory thresholds, this architecture scales proactively based on actual business queue depth, and crucially, **scales to zero (`minReplicaCount: 0`)** when idle to eliminate unnecessary cloud compute costs.

---

## 🏗️ Architecture

```mermaid
graph LR
    A[Producer Pod] -->|LPUSH jobs| B[(Redis Queue)]
    B -->|Triggers| C[KEDA ScaledObject]
    C -->|Scales up/down (0-10)| D[Worker Pods]
    D -->|BRPOP jobs| B
```

## 🚀 Features

*   **Scale-to-Zero:** Workers are completely removed when the queue is empty.
*   **Queue-Length Targeting:** Configured via `ScaledObject` to maintain a ratio of 1 worker pod per 5 queued items.
*   **Traffic Spike Simulation:** Includes a stochastic producer script to generate realistic, bursty workloads.
*   **Visual Monitor:** Includes a CLI monitoring tool (`watch.py`) to visualize queue length vs. pod count in real-time.

## 🛠️ Deployment Guide

### Prerequisites
*   A running Kubernetes cluster (e.g., Minikube, kind, or EKS/GKE).
*   `kubectl` configured.

### 1. Install KEDA
If KEDA is not already installed on your cluster:
```bash
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.16.1/keda-2.16.1.yaml
```

### 2. Deploy the Infrastructure & Application
This will deploy Redis, the Producer, the Worker Deployment (initially 0 replicas), and the KEDA `ScaledObject`.
```bash
kubectl apply -f k8s/
```

### 3. Monitor Autoscaling in Action
Run the included python monitor script to watch the queue fill up and the pods automatically scale to meet the demand:
```bash
python watch.py
```

## ⚙️ Configuration Tuning
Scaling behavior can be finely tuned in `k8s/scaledobject.yaml`:
*   `minReplicaCount`: Minimum pods (set to 0 for maximum cost saving).
*   `maxReplicaCount`: Maximum pods to prevent runaway scaling costs.
*   `listLength`: The target value (queue length per pod). 

## 📄 License
MIT License
