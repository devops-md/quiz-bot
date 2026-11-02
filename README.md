# DevOps Moldova Quiz Bot

Automated Telegram Quiz Bot that dynamically generates and publishes daily technical quizzes to the DevOps Moldova community channel. Powered by a local **Ollama LLM** running alongside the bot in **Docker** on a local **Proxmox** server.

---

## Key Features

- 🧠 **Autonomous Dynamic Generation**: Uses a local Ollama LLM (`llama3.2:3b` or `qwen2.5:3b`/`7b`) to generate realistic scenario-based questions daily.
- 🎯 **12 DevOps Domains**: Comprehensive taxonomy covering Kubernetes, GitOps, IaC, Cloud, SRE/Observability, Linux, Networking, DevSecOps, AI/MLOps, Databases, History of IT, and IT Memes & Culture.
- 🛡️ **Strict Telegram Validation**: Automatically verifies and formats questions to meet Telegram Bot API limits (4 options, question $\le 300$ chars, options $\le 100$ chars, explanation $\le 200$ chars).
- 🔀 **Option Shuffling & Deduplication**: Randomizes correct answer positions to eliminate LLM placement bias and tracks question history to avoid repeats.
- 🛟 **Emergency Fallback Pool**: Local verified question pool guarantees a quiz is always published even if Ollama is restarting or temporarily offline.
- 🐳 **Self-Contained Docker Deployment**: Orchestrated via Docker Compose for easy deployment on Proxmox VE (LXC or VM).
- 🚀 **Automated Multi-Arch CI/CD**: Builds and pushes `linux/amd64` and `linux/arm64` images to Docker Hub (`aprescornic/telegram_quizz`) on push to `main`.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│ Proxmox VE Host (Local Server)                         │
│                                                        │
│  ┌─────────────────────── Docker Network ────────────┐ │
│  │                                                   │ │
│  │  ┌──────────────────┐       ┌──────────────────┐  │ │
│  │  │   ollama         │◄──────│   quiz-bot       │  │ │
│  │  │ (llama3.2:3b)    │ HTTP  │  (Python 3.12)   │  │ │
│  │  │ Port 11434       │       │                  │  │ │
│  │  └────────┬─────────┘       └─────────┬────────┘  │ │
│  │           │                           │           │ │
│  │     Ollama Models                quiz_data        │ │
│  │     Docker Volume              History Volume     │ │
│  └───────────────────────────────────────┼───────────┘ │
└──────────────────────────────────────────┼─────────────┘
                                           │ HTTPS
                                           ▼
                               ┌───────────────────────┐
                               │ Telegram Bot API      │
                               │ (Channel / Topic)     │
                               └───────────────────────┘
```

---

## Taxonomy & Difficulty Levels

### Difficulty Levels
Questions are rotated across four calibrated difficulty levels:
- **`beginner`**: Primitives, core definitions, and basic commands.
- **`intermediate`**: Day-to-day production operations, configuration flags, and debugging.
- **`advanced`**: Deep internals, kernel mechanisms, race conditions, and performance tuning.
- **`architect`**: System design trade-offs, high-availability topologies, DR/RTO/RPO strategies, FinOps unit economics, and platform scaling.

### Domains
Questions are rotated dynamically across 16 domains specified in `questions_domains.json`:
1. **Containers & Orchestration** (Docker, Kubernetes Control Plane, CNI, CSI, RBAC, Autoscaling/Karpenter, Gateway API, vCluster, Helm, Istio/Cilium)
2. **CI/CD & GitOps** (ArgoCD, Flux v2, GitLab CI, GitHub Actions, Jenkins, Progressive Rollouts, Harbor, Pipeline Security, Tekton)
3. **Infrastructure as Code** (Terraform, OpenTofu, Terragrunt, Ansible, Pulumi, Crossplane, Atlantis, Packer, Drift & DR)
4. **Cloud Platforms** (AWS, GCP, Azure, Serverless, Cloud Identity & Federation, Hybrid Connectivity, Cloud Governance)
5. **Platform Engineering** (Internal Developer Platforms, Backstage, Port, Golden Paths, Platform APIs, DevEx, DevContainers)
6. **Observability & SRE** (Prometheus, PromQL, Grafana, OpenTelemetry, Loki, Continuous Profiling, SLOs, Incident Response)
7. **Linux & System Engineering** (Kernel, cgroups v2, Systemd, Bash, Performance diagnostics, strace/perf, eBPF, Memory/OOM, SELinux)
8. **Networking & Protocols** (TCP/IP, DNS, TLS/mTLS, Nginx, Envoy, HTTP/2 & HTTP/3, BGP Routing, WireGuard, CDNs, DDoS/WAF)
9. **DevSecOps** (Trivy, Vault, SBOM, Sigstore, OPA/Kyverno, Distroless Hardening, Falco Runtime Security, CSPM, Zero Trust)
10. **FinOps & Cloud Economics** (Cost Allocation & Tagging, Savings Plans/CUDs, Spot Orchestration, Kubecost/OpenCost, Unit Economics)
11. **Chaos & Reliability Engineering** (Chaos Mesh, Blast Radius, GameDays, Circuit Breakers, Bulkheads, Jitter, Active-Active DR)
12. **Distributed Systems Architecture** (Consensus Raft/Paxos, CAP/PACELC, Sagas, Kafka/RabbitMQ/NATS, Idempotency, Caching, Gateways)
13. **AI for DevOps & MLOps** (Local LLMs, Model Context Protocol, GPU Scheduling, Vector DBs, RAG Ops, Kubeflow, AI SRE Agents)
14. **Databases & Storage for DevOps** (PostgreSQL HA Patroni, pgBackRest, Redis/Valkey, Kafka, MinIO/Ceph, Zero-Downtime Migrations)
15. **History of IT** (UNIX & BSD origins, early computing pioneers, ARPANET, famous historical outages, virtualization history, VCS evolution)
16. **IT Memes & Culture** (DNS jokes, Friday deploys, editor wars, joke RFCs, on-call humor, programming roast culture, meetup lore)

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | **Yes** | — | Telegram Bot token from @BotFather |
| `CHANNEL_ID` | **Yes** | — | Target channel username or ID (e.g. `@devopsmoldova` or `-100...`) |
| `THREAD_ID` | No | `None` | Telegram Topic / Forum Thread ID |
| `PUBLISH_TIME` | No | `"08:50"` | Daily publish schedule (`HH:MM`) |
| `TZ` | No | `"Europe/Chisinau"` | Timezone for the scheduler |
| `DEBUG_MODE` | No | `"false"` | If `true`, fires an immediate quiz and publishes every 2 mins |
| `DEBUG_INTERVAL_MINUTES` | No | `2` | Interval in minutes when `DEBUG_MODE=true` |
| `OLLAMA_BASE_URL` | No | `"http://ollama:11434"` | Internal or external Ollama API URL |
| `OLLAMA_MODEL` | No | `"llama3.2:3b"` | Ollama model tag |
| `OLLAMA_TIMEOUT` | No | `60.0` | Timeout in seconds for LLM generation |
| `OLLAMA_TEMPERATURE` | No | `0.7` | Temperature for question diversity |
| `OLLAMA_MAX_RETRIES` | No | `3` | Retries on failed generation/validation |

---

## Proxmox VE Deployment Guide (Dedicated Multi-CT Architecture)

To keep services cleanly separated and allow your **Ollama instance to serve multiple applications** (Quiz Bot, Home Assistant, Open WebUI, dev agents, etc.), the recommended Proxmox setup uses **two separate LXC Containers**:

```
┌────────────────────────────────────────────────────────┐
│ Proxmox VE Local Server                                │
│                                                        │
│  ┌─────────────────────────┐  ┌─────────────────────┐  │
│  │ CT 101: Dedicated Ollama│  │ CT 102: Quiz Bot    │  │
│  │ (e.g. 192.168.1.50)     │  │ (e.g. 192.168.1.51) │  │
│  │                         │  │                     │  │
│  │  ┌───────────────────┐  │  │  ┌───────────────┐  │  │
│  │  │  Ollama Service   │◄─┼──┼──┤   Quiz Bot    │  │  │
│  │  │  Port 11434       │  │  │  │ (Docker)      │  │  │
│  │  │  (0.0.0.0:11434)  │  │HTTP│  └───────────────┘  │  │
│  │  └────────┬──────────┘  │  │          │          │  │
│  │           │             │  │          ▼          │  │
│  │     Ollama Models       │  │      History Data   │  │
│  └─────────────────────────┘  └──────────┬──────────┘  │
└──────────────────────────────────────────┼─────────────┘
                                           │ HTTPS
                                           ▼
                               ┌───────────────────────┐
                               │ Telegram Bot API      │
                               │ (Channel / Topic)     │
                               └───────────────────────┘
```

---

### Step 1: Set Up CT 101 — Dedicated Ollama AI Server

This container will serve as your centralized LLM inference engine for the Quiz Bot and any future projects.

1. **Create the LXC Container**:
   - In Proxmox Web UI, click **Create CT**.
   - **Template**: Debian 12 or Ubuntu 24.04.
   - **Resources**: 
     - **CPU**: 4 vCPUs (or more, depending on your Proxmox CPU).
     - **RAM**: 4096–8192 MB (allows comfortable running of 3B to 7B models).
     - **Disk**: 30–50 GB (models are ~2–5 GB each).
   - **Network**: Static IP or DHCP reservation (e.g., `192.168.1.50`).

2. **Install Ollama Natively**:
   Enter the CT 101 console:
   ```bash
   apt-get update && apt-get install -y curl jq
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   *Installing natively inside the LXC container gives the best performance with zero Docker overhead and automatic systemd service management.*

3. **Configure Ollama to Listen on the Network (`0.0.0.0:11434`)**:
   By default, Ollama only listens on `127.0.0.1`. Configure systemd so other containers can access it:
   ```bash
   # Create systemd override directory
   mkdir -p /etc/systemd/system/ollama.service.d/

   # Set OLLAMA_HOST to listen on all interfaces
   cat << 'EOF' > /etc/systemd/system/ollama.service.d/override.conf
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0:11434"
   Environment="OLLAMA_ORIGINS=*"
   EOF

   # Reload systemd and restart Ollama
   systemctl daemon-reload
   systemctl restart ollama
   ```

4. **Pull the Models**:
   ```bash
   # Pull the fast 3B model for daily quiz generation
   ollama pull llama3.2:3b

   # (Optional) Pull additional models for other purposes
   ollama pull qwen2.5:3b
   ollama pull qwen2.5:7b

   # Verify downloaded models
   ollama list
   ```

5. **Verify Network Accessibility**:
   From your PC or any other machine on your local network:
   ```bash
   curl http://192.168.1.50:11434/api/tags
   ```

---

### Step 2: Set Up CT 102 — Dedicated Quiz Bot Container

This container runs the Quiz Bot application via Docker.

1. **Create the LXC Container**:
   - In Proxmox Web UI, click **Create CT**.
   - **Template**: Debian 12 or Ubuntu 24.04.
   - **Resources**: 1–2 vCPUs, 1024–2048 MB RAM, 10 GB disk.
   - **Crucial**: Enable Docker Nesting & keyctl support:
     - In Proxmox Web UI: **CT 102 -> Options -> Features -> Edit**.
     - Check **Nesting** (`nesting=1`) and **keyctl** (`keyctl=1`).
     - *Or from Proxmox host shell:*
       ```bash
       pct set 102 -features nesting=1,keyctl=1
       ```

2. **Install Docker in CT 102**:
   ```bash
   apt-get update && apt-get install -y curl git jq
   curl -fsSL https://get.docker.com | sh
   systemctl enable --now docker
   ```

3. **Deploy the Quiz Bot**:
   ```bash
   git clone https://github.com/aprescornic/telegram_quizz.git /opt/telegram_quizz
   cd /opt/telegram_quizz

   cp .env.example .env
   nano .env
   ```

4. **Configure `.env`**:
   Point `OLLAMA_BASE_URL` to your CT 101 IP address:
   ```env
   # Telegram Bot Credentials
   BOT_TOKEN=123456789:ABCDefGhIjKlMnOpQrStUvWxYz
   CHANNEL_ID=@devopsmoldova
   THREAD_ID=

   # Scheduling
   PUBLISH_TIME=08:50
   TZ=Europe/Chisinau
   DEBUG_MODE=false

   # Point to your dedicated Ollama CT IP
   OLLAMA_BASE_URL=http://192.168.1.50:11434
   OLLAMA_MODEL=llama3.2:3b
   ```

5. **Start the Quiz Bot**:
   ```bash
   docker compose up -d
   ```

---

### Step 3: Test & Verify

1. **Test Immediate Quiz Dispatch**:
   Temporarily enable debug mode to verify that CT 102 reaches CT 101 and publishes to Telegram immediately:
   ```bash
   sed -i 's/DEBUG_MODE=false/DEBUG_MODE=true/' .env
   docker compose up -d
   docker compose logs -f quiz-bot
   ```

   You should see in logs:
   - Ollama healthcheck succeeded on `http://192.168.1.50:11434`
   - Target domain and subdomain selected
   - Generated quiz received and validated
   - Quiz successfully published to Telegram

2. **Switch to Production Schedule**:
   ```bash
   sed -i 's/DEBUG_MODE=true/DEBUG_MODE=false/' .env
   docker compose up -d
   ```

3. **Enable Auto-Start on Proxmox Boot**:
   In the Proxmox Web UI, enable **Start at boot** for both **CT 101** and **CT 102**.
   Set **Start order** on CT 101 to `order=1` and CT 102 to `order=2` so Ollama boots first.
   ```bash
   docker compose up -d
   ```

---

### Step 4: Download the Ollama Model

Once the containers are running, trigger the initial model download into the persistent Docker volume:

```bash
# Pull the recommended 3B model (approx. 2 GB download)
docker compose exec ollama ollama pull llama3.2:3b

# Verify the model is available
docker compose exec ollama ollama list
```

> **Alternative Models**:
> - `qwen2.5:3b`: Extremely fast, high instruction-following precision.
> - `qwen2.5:7b`: Stronger technical depth for complex scenarios (requires ~6 GB RAM).

---

### Step 5: Test & Verify

1. **Verify Ollama is responding**:
   ```bash
   curl -s http://localhost:11434/api/tags | jq .
   ```

2. **Trigger an immediate test quiz**:
   To test generation and Telegram delivery right away without waiting for the daily cron:
   ```bash
   # Temporarily enable debug mode
   sed -i 's/DEBUG_MODE=false/DEBUG_MODE=true/' .env
   docker compose up -d

   # Watch logs to see the test quiz generated and sent
   docker compose logs -f quiz-bot
   ```
   After confirming the quiz appeared in Telegram, switch back to production mode:
   ```bash
   sed -i 's/DEBUG_MODE=true/DEBUG_MODE=false/' .env
   docker compose up -d
   ```

3. **Enable Proxmox Auto-Start**:
   - In Proxmox VE Web UI, go to your CT/VM -> **Options** -> **Start at boot** -> set to **Yes**.
   - Because `restart: unless-stopped` is configured in `docker-compose.yaml`, the bot will automatically resume after host reboots.

---

### Proxmox Useful Commands & Maintenance

```bash
# View live application logs
docker compose logs -f quiz-bot

# View Ollama inference logs
docker compose logs -f ollama

# Inspect published question history
docker compose exec quiz-bot cat data/history.json | jq .

# Restart the bot
docker compose restart quiz-bot

# Update to latest bot image from Docker Hub
docker compose pull quiz-bot && docker compose up -d
```

---

## Local Development & Testing

### Setup Virtual Environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
```

### Run Test Suite
```bash
pytest -v
```

---

## CI/CD Pipeline

On every push to `main`, GitHub Actions (`.github/workflows/docker-build.yml`):
1. Builds multi-architecture images (`linux/amd64`, `linux/arm64`) using QEMU and Docker Buildx.
2. Checks Docker Hub (`aprescornic/telegram_quizz`) tags and automatically bumps the semantic patch version.
3. Pushes tagged and `latest` images to Docker Hub.
4. Generates a new GitHub Release with release notes.
