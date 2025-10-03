Roadmap for SME LLM Fine‑Tuning and RAG Framework

The roadmap outlines a phased approach starting in October 2025. Actual dates may shift based on resource availability and discoveries during implementation. The plan assumes a small engineering/data‑science team and external support where required.

Phase 0 – Research & Planning (Oct 2025)
Tasks:

Finalize requirements and FSD: 
    - Review the functional specification with stakeholders; refine user roles, data sources and domain priorities
      - Owner: REH
      - Approver: team

Evaluation of open‑source LLMs:
    - **COMPLETE**: Benchmarking LLMs for general SME domain usage
    - **COMPLETE**: assess licensing, performance and compute requirements	
    - **COMPLETE**: Selection report and recommended base models

Define SME Agents (top 3 for initial development and testing): 
    - Process Control and Automation Supervisor SME Agent
      - To supervise layer 2 and 3 process control infrastructure
    - Database Interaction SME Agent
      - for non-technical interactions with WMS database
    - ML and Data Engineering Manager SME Agent
      - Responsible for the curation of datasets and conversion to Model ingestion formats
      - Access to core WHK DB infrastructure


Define Evaluation metrics:
    - Select domain‑specific question sets and general metrics (accuracy, latency) for model and agent evaluation	Data Science Expert	Evaluation plan

Plan infrastructure:
    - Inventory existing hardware (M3 Ultra, AMD 9995WR) and decide if additional GPUs or servers are required;
    - Owner: Director of Technology with IT/OT Network Engineer	
    - Approval: Team

Phase 1 – Infrastructure and Security Setup:
    Tasks:
        - Deploy development environment	
        - Set up container cluster or VM infrastructure on WHK’s internal network; install container runtime, orchestrator and storage
        - Install Neo4j Dev cluster 
          - Test high availability
          - enable full‑text and vector indexes

    Configure storage & model registry:
      - Set up object storage - NAS partition? for extended dataset storage and model checkpoints. 
      - Deploy model registry (LLM Studio - for Dev)
      - 
    Implement SSO integration & RBAC:
        - Integrate Microsoft SSO with identity provider
          - define initial RBAC policies and group mappings
          - Authentication/authorization working in development

    Develop dev‑ops pipelines:
        - Create GitHub CI/CD pipelines and workflows for building, testing and deploying services (ingestion, training, inference)
        - Set up git integrations - codeRabbit, Graphite, Linear... 

Phase 2 – Data Ingestion & Curation:
    Tasks:
        Build connectors:
        	- Implement data connectors for documents, SCADA logs, PLC tag data, ERP/MES, and other systems. 
            	- handle streaming MQTT and batch ingestion
          	- Testing Connectors with unit tests

        Implement data_curation_manager:
            - Develop the service to clean, filter, deduplicate, redact PII and package datasets into JSON/Parquet
              - incorporate pipelines as needed
              - Formating and filtering requirements

        Create Data Governance Expert with curation services:
            - Establish schema governance
              - Define metadata fields (source, timestamp, tags, access level, ownership)
              - implement schema in curated datasets
              - develop metadata schema frameworks and validation scripts
            - Populate initial graph for first agent training
              - Run curation on a limited subset (e.g., distillation manuals, process logs)
                - To generate graph documents import into Neo4j using LLMGraphTransformer

Phase 3 – Embedding & Vector Infrastructure:
    Tasks:
        Choose VDB:
            Postgres: Review as Prod VectorDB
                - Pros:
                - Cons:
            Neo4J:Review as Prod VectorDB (vector embedding functionality may require paid version?) 
                - Pros:
                - Cons:

            Choose embedding models to create vector representations:
                - Start with SME Agent specific Data injestion to graphDB
                  - node and relationships text, datasets, definative authoratative sources, and unstructured documents.
                - Post Ingestion from Neo4j to 
                  - Neo4J vector index or 
                  - dedicated vector DB

	        ML Engineer	Embedding generation scripts: Once vDB is setup
                Set up vector database or Neo4J vector index model
                    - DEV - Evaluate need for external vector store (e.g., FAISS, Qdrant)
                      - if beneficial, deploy and integrate
                    - maintain references to Neo4j nodes
                    - Vector DB deployed and documented
                Develop retrieval API
                    - Build API endpoint to perform hybrid search (keyword + vector)
                    - Setup return top‑k results along with graph context
                    - optimize for speed
                Retrieval microservice:
                    - Conduct retrieval performance tests
                    - Benchmark retrieval latency and accuracy
                    - optimize index configuration (dimensions, distance metrics)
                    - Retrieval benchmark report / documentation

Phase 4 – Model Fine‑Tuning Pipeline:
    Tasks:
        Prepare training datasets:
            - Use curated datasets to generate instruction‑response pairs; ensure data labeling consistency and remove residual PII	Data
            - Curation Expert:	Training datasets (JSON / JSONL)
            - Develop training scripts
              - Create scripts using PyTorch/Deepspeed
            - Support full fine‑tuning and PEFT
              - include logging, checkpointing and hyperparameter configuration
            - Develop ML Research Expert:
              - Training pipeline code
              - Begin train pilot models (7 B–13 B)
              - Fine‑tune selected base models on domain data
              - evaluate using evaluation metrics
              - iterate hyperparameters
        Fine‑tuned SME models evaluation reporting / documentation
            - Assess hardware scaling
            - Measure training throughput on existing hardware
            - Determine hardware requirements:  MAC Studio VS AMD9995WR with 2 RTX6000 (48Gb VRAM each)
              - decide whether to procure additional GPUs or use multi‑node training for larger models
              - document \
        Scaling assessment:
            - Plan 70 B training: 
              - Assess distributed training strategy for 70 B models
              - consider PEFT to reduce hardware requirements
    	ML Research Expert	70 B training plan:

Phase 5 – RAG Integration:  
    Tasks:
        Build RAG layer	Implement retrieval orchestrator:
            - Framework combines keyword search, vector search and graph traversal
            - design algorithms to assemble context for LLM input
            - RAG service development
        Integrate with models:
            - Development of modified inference orchestrators to accept retrieved context and generate responses
              - support graph‑enhanced generation
              - Develop ML Engineer	Inference service with RAG
                - Evaluate RAG quality	
        Research:
          - Perform experiments comparing vector‑only retrieval with hybrid and graph‑based retrieval
            - record accuracy improvements and latency
            - Create RAG evaluation report
        Determine need for Enhanced graph construction:
            - Iterate on entity extraction and relation detection
            - build out by incorporating additional domain knowledge
            - refine LLMGraphTransformer prompts
        Data Curation Expert:
            - Eval to improve graph construction pipeline

Phase 6 – Agent Orchestration & Real‑Time Integration:
    Tasks: 
        Develop agent framework
        Build orchestration layer -Agent orchestrator 
            - to manages multiple SME agents
            - handles user queries
            - selects appropriate retrieval pathways and models
            - composes responses
        Implement real‑time streaming
            - Integrate PLC tag streams
              - process data into the retrieval pipeline
            - Use windowing and summarization to capture trends
        Develop Real‑time ingestion module
        Design user interfaces
        Create API endpoints
        CLI tools or chat interfaces for operators, engineers and management to interact with agents
            - API bridge CLI to UI/API prototypes
        Deploy agents for one domain (e.g., controls & automation)
        Develop SME feedback pipelines for CI model RL
            - track performance and adoption
            - create Pilot report and improvement plan

Phase 7 – Security, RBAC & Governance: 
    Tasks:
        Finalize RBAC rules:
            - Define fine‑grained access rules for data categories, models and agents
            - Implement checks in APIs
              - integrate with SSO
              - RBAC configuration deployment
        As clould based resources are required: 
            - Conduct security audits to ensure no sensitive information is exposed
            - test RBAC enforcement	
        Add to External security consultant workload? 
            - Compliance review	Review
            - data handling and privacy controls against relevant regulations (GDPR, ISA‑95) and corporate policies
            - Data Governance Compliance assessment

Phase 8 – Testing & Optimization: 
    Tasks:
        System integration testing:
            - Test end‑to‑end workflows (ingestion → graph → retrieval → model → agent) under realistic workloads
              - fix issues	
              - QA Engineer	Test report
              - Performance & scalability testing
                - Stress test retrieval and inference services
                  - identify bottlenecks; optimize caching, batching and concurrency
              - Performance tuning plan documented
            - User acceptance testing: Involve SMEs from each domain
              - gather feedback on agent accuracy, usability and trust
              - document and incorporate suggestion
                - UAT results and issue backlog

Phase 9 – Production Deployment & Maintenance:
    Tasks: 
        Production testing / rollout - after unannounced prod testing
            - Gradually roll out SME agents across domains
            - monitor usage and performance
            - scale infrastructure as needed
        Full Production deployment:
            Continuous improvement
                - Set up feedback loops to capture user corrections and new data
                - retrain models periodically using SME feedback RL expand graph coverage	Data Science Team	Continuous improvement pipeline
Maintenance & support	Maintain infrastructure, update dependencies, patch security vulnerabilities; provide user support and documentation	IT/OT Network Engineer & Software Engineers	Maintenance playbook
Future expansion	Explore adding additional domains or cross‑domain reasoning; integrate with other WHK initiatives (e.g., predictive analytics)	Engineering Leadership	Roadmap updates
