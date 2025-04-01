
# ⚡ Kafka-Live-Orchestrator for Smart Energy Grids

This repository contains a real-time, modular, Kafka-based orchestrator designed to manage smart energy grid pipelines using AI microservices.

> 🔥 Built by [Vaibhav Rana](https://github.com/VaibhavTechie) under the **AI4EU-Graphene** initiative.

---

## 🚀 Project Vision

The energy sector is undergoing rapid transformation, and intelligent orchestration of live data is the backbone of tomorrow’s smart grids.

This project is built with the vision of:
- Replacing traditional, sequential orchestrators with lightweight, event-driven Kafka pipelines
- Providing **real-time energy demand forecasting, anomaly detection**, and **smart grid rebalancing**
- Ensuring each microservice is **modular, reusable, and domain-aware**, designed to plug into real-world deployments

---

## 🧠 System Overview

Each node in this system is an intelligent microservice responsible for a specific function in the energy pipeline. Kafka topics connect these nodes like neural links, allowing flexible, scalable execution.

### ✅ Completed Nodes So Far:
| Node Name                | Role Description |
|-------------------------|------------------|
| `smart-data-ingestor`   | Fetches real-time energy data from EirGrid and publishes it to Kafka (`raw_data`) |
| `smart-data-preprocessor` | Preprocesses raw data (pivot, clean) and publishes to `pivoted_data` |

> ⚙️ More nodes (ML Forecaster, Anomaly Detector, Grid Rebalancer, etc.) will follow.

---

## 🧱 Folder Structure

```
kafka-live-orchestrator/
├── smart-data-ingestor/
│   ├── smartgrid_fetcher.py
│   ├── smart_ingestor_service.py
│   └── requirements.txt
├── smart-data-preprocessor/
│   ├── preprocessor_service.py
│   └── requirements.txt
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🧪 Running Locally (Dev Setup)

> 🐳 Make sure you have Docker and Docker Compose installed.

```bash
# Clone the repo
git clone git@github.com:AI4EU-Graphene/kafka-live-orchestrator.git
cd kafka-live-orchestrator

# Start the system
docker compose up --build

# Test the ingestor
curl http://localhost:5104/fetch-and-publish

# Monitor Kafka messages (consumer)
docker exec -it kafka-live-orchestrator-kafka-1 \
  kafka-console-consumer --bootstrap-server kafka:9092 \
  --topic pivoted_data --from-beginning --timeout-ms 5000
```

---

## 📡 Technologies Used

- **Apache Kafka** – Real-time event streaming
- **Flask** – Microservice APIs
- **Kafka Python** – Kafka producer/consumer integration
- **Pandas / JSON / Aiohttp** – Data processing, async I/O
- **Docker Compose** – Service orchestration

---

## 🧭 What's Next?

- ✅ ML Preprocessing Node (scaling, feature engineering)
- ✅ ML Forecaster Node (regression-based predictions)
- ✅ Anomaly Detection Node (detect spikes/drops)
- ✅ Smart Rebalancer & Storage Optimizer Nodes

> The end goal: a modular, AI-powered grid orchestration system deployable in **real-world energy infrastructure**.

---

## 🙌 Contributing

This is an open vision project. If you're passionate about energy, AI, or distributed systems, feel free to fork or raise an issue/discussion.

---

## 📬 Contact

Created by **Vaibhav Rana**  
📫 [vaibhav.s.rana@outlook.com](mailto:vaibhav.s.rana@outlook.com)  
🔗 [https://github.com/VaibhavTechie](https://github.com/VaibhavTechie)

---

> ⚡ *"This isn't just code—this is infrastructure thinking."*
