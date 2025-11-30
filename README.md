# ⚡ GridWatch: Real-Time Energy Grid Visualization

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

GridWatch is a cloud-native, three-tier web app that visualizes real-time energy generation data from the US power grid (PJM Interconnection). It demonstrates a secure, production-ready DevOps architecture on Microsoft Azure, built entirely with Infrastructure as Code (IaC).

## Architecture

This project implements a **Hub-and-Spoke** style architecture within a secure Virtual Network (VNet). It utilizes **Azure Container Apps** for compute and **Azure Database for PostgreSQL** for persistence.

```mermaid
graph TD
    subgraph Azure_Cloud [Microsoft Azure Region]
        subgraph VNet [Virtual Network (10.0.0.0/16)]

            subgraph App_Subnet [App Subnet (10.0.2.0/23)]
                ACA_Env[Container App Environment]

                subgraph Web_Tier [Frontend]
                    Nginx[Nginx Container]
                end

                subgraph App_Tier [Backend]
                    FastAPI[Python FastAPI Container]
                end
            end

            subgraph Data_Subnet [Data Subnet (10.0.4.0/24)]
                Postgres[(Azure PostgreSQL)]
            end
        end

        KV[Azure Key Vault]
        ACR[Azure Container Registry]
    end

    User((User/Browser)) -- HTTPS --> Nginx
    Nginx -- Internal HTTP --> FastAPI
    FastAPI -- VNet Integration --> Postgres
    FastAPI -- Private Link --> KV
    FastAPI -- HTTPS (Ingress) --> EIA_API[EIA Public API]

    style VNet fill:#e1f5fe,stroke:#01579b
    style App_Subnet fill:#e0f2f1,stroke:#00695c,stroke-dasharray: 5 5
    style Data_Subnet fill:#fff3e0,stroke:#e65100,stroke-dasharray: 5 5
