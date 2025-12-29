# Architecture Diagrams

Visual representations of the OpenAI Agents SDK Travel Planning System architecture.

---

## System Architecture Diagram

```mermaid
graph TB
    User[User Interface<br/>Terminal/API/Web] --> API[FastAPI Layer]
    API --> Orchestrator[Travel Agent<br/>Orchestrator]
    
    Orchestrator --> Planner[Planner Agent<br/>Itinerary]
    Orchestrator --> Budget[Budget Agent<br/>Cost Estimation]
    Orchestrator --> Guide[Local Guide Agent<br/>Tips & Dining]
    
    Planner --> WebSearch[WebSearchTool]
    Guide --> WebSearch
    
    Orchestrator --> Guardrails[Input Guardrails<br/>Budget Validator]
    
    Planner --> OpenAI[OpenAI API<br/>GPT-4/GPT-5]
    Budget --> OpenAI
    Guide --> OpenAI
    Orchestrator --> OpenAI
    Guardrails --> OpenAI
    
    Orchestrator --> Session[SQLite Sessions<br/>Context Memory]
    
    Session --> DB[(Database<br/>Session Storage)]
    
    style User fill:#e1f5ff
    style Orchestrator fill:#fff4e1
    style Planner fill:#e8f5e9
    style Budget fill:#e8f5e9
    style Guide fill:#e8f5e9
    style Guardrails fill:#ffebee
    style OpenAI fill:#f3e5f5
    style Session fill:#e0f2f1
```

---

## Data Flow - Lesson 1 (Basic Agent)

```mermaid
sequenceDiagram
    participant User
    participant Agent as agent.py
    participant API as OpenAI API
    participant Output as print_fields()
    
    User->>Agent: User prompt
    Agent->>API: chat.completions.create()
    API->>API: Process with GPT
    API-->>Agent: JSON response
    Agent->>Output: Parse & validate
    Output-->>User: Display formatted output
```

---

## Data Flow - Lesson 3 (Multi-Agent Orchestration)

```mermaid
sequenceDiagram
    participant User
    participant Orch as Orchestrator
    participant Planner as Planner Agent
    participant Budget as Budget Agent
    participant Guide as Guide Agent
    participant API as OpenAI API
    
    User->>Orch: "Plan trip to Delhi"
    Orch->>API: Analyze request
    API-->>Orch: Call planner_agent
    
    Orch->>Planner: Create itinerary
    Planner->>API: Build day-by-day plan
    API-->>Planner: Itinerary JSON
    Planner-->>Orch: Return itinerary
    
    Orch->>Budget: Estimate costs
    Budget->>API: Calculate budget
    API-->>Budget: Cost JSON
    Budget-->>Orch: Return costs
    
    Orch->>Guide: Get local tips
    Guide->>API: Find restaurants
    API-->>Guide: Tips JSON
    Guide-->>Orch: Return tips
    
    Orch->>Orch: Aggregate results
    Orch-->>User: Complete travel plan
```

---

## Guardrail Flow - Lesson 4

```mermaid
flowchart TD
    Start[User Input] --> Guardrail{Input Guardrail<br/>Budget Check}
    Guardrail -->|Valid| Process[Travel Agent<br/>Processes Request]
    Guardrail -->|Invalid| Block[Raise Exception<br/>Block Request]
    
    Process --> Result[Return Travel Plan]
    Block --> Error[Error Message<br/>to User]
    
    style Guardrail fill:#ffebee
    style Block fill:#ff5252,color:#fff
    style Process fill:#e8f5e9
    style Result fill:#81c784,color:#fff
```

---

## Session Lifecycle - Lesson 5

```mermaid
stateDiagram-v2
    [*] --> Created: SQLiteSession("user_123")
    Created --> Turn1: Runner.run(agent, prompt1)
    Turn1 --> Persisted: Save to DB
    Persisted --> Turn2: Runner.run(agent, prompt2)
    Turn2 --> Persisted: Update DB
    Persisted --> Turn3: Runner.run(agent, prompt3)
    Turn3 --> Persisted: Update DB
    Persisted --> [*]: Session ends
    
    note right of Turn1
        Context: Fresh start
        No prior messages
    end note
    
    note right of Turn2
        Context: Remembers Turn 1
        Has message history
    end note
```

---

## Production Architecture

```mermaid
graph TB
    subgraph "Load Balancing"
        LB[Load Balancer<br/>AWS ALB]
        Nginx[Nginx<br/>Reverse Proxy]
    end
    
    subgraph "Application Layer"
        API1[FastAPI<br/>Instance 1]
        API2[FastAPI<br/>Instance 2]
        API3[FastAPI<br/>Instance 3]
    end
    
    subgraph "Business Logic"
        AgentService[Agent Service<br/>Orchestration]
        SessionService[Session Service<br/>State Management]
    end
    
    subgraph "Data Layer"
        Redis[(Redis<br/>Cache)]
        PostgreSQL[(PostgreSQL<br/>Sessions)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-4/5]
        Search[Web Search<br/>DuckDuckGo]
    end
    
    subgraph "Monitoring"
        Prometheus[Prometheus<br/>Metrics]
        Jaeger[Jaeger<br/>Tracing]
        Grafana[Grafana<br/>Dashboards]
    end
    
    LB --> Nginx
    Nginx --> API1
    Nginx --> API2
    Nginx --> API3
    
    API1 --> AgentService
    API2 --> AgentService
    API3 --> AgentService
    
    AgentService --> SessionService
    AgentService --> OpenAI
    AgentService --> Search
    
    SessionService --> Redis
    SessionService --> PostgreSQL
    
    API1 --> Prometheus
    API2 --> Prometheus
    API3 --> Prometheus
    AgentService --> Jaeger
    Prometheus --> Grafana
    
    style LB fill:#e1f5ff
    style AgentService fill:#fff4e1
    style Redis fill:#ffebee
    style PostgreSQL fill:#e8f5e9
    style OpenAI fill:#f3e5f5
```

---

## Component Interaction

```mermaid
graph LR
    subgraph "Agent Creation"
        Agent[Agent Class] --> Instructions[Instructions<br/>System Prompt]
        Agent --> Output[Output Type<br/>Pydantic Model]
        Agent --> Settings[Model Settings<br/>Reasoning/Verbosity]
        Agent --> Tools[Tools<br/>Functions/Agents]
        Agent --> Guardrails[Guardrails<br/>Validators]
    end
    
    subgraph "Execution"
        Runner[Runner.run] --> Context[Context<br/>Shared Data]
        Runner --> Session[Session<br/>State]
        Runner --> API[OpenAI API<br/>LLM Calls]
    end
    
    subgraph "Results"
        Result[RunResult] --> FinalOutput[final_output<br/>Structured Data]
        Result --> Messages[messages<br/>History]
        Result --> ToolCalls[tool_calls<br/>Executed Tools]
    end
    
    Agent --> Runner
    Runner --> Result
    
    style Agent fill:#e1f5ff
    style Runner fill:#fff4e1
    style Result fill:#e8f5e9
```

---

## Tool Execution Flow

```mermaid
sequenceDiagram
    participant Agent
    participant LLM as OpenAI LLM
    participant Runner
    participant Tool
    
    Agent->>LLM: User prompt + tools
    LLM->>LLM: Decides to call tool
    LLM-->>Runner: tool_calls response
    
    loop For each tool call
        Runner->>Tool: Execute function
        Tool->>Tool: Process (e.g., web search)
        Tool-->>Runner: Return result
        Runner->>LLM: Send tool result
    end
    
    LLM->>LLM: Continue reasoning
    LLM-->>Agent: Final output
```

---

These diagrams are created using Mermaid syntax and can be:
- Rendered in GitHub, VS Code (with Mermaid extension), or documentation sites
- Exported as PNG/SVG for presentations
- Updated as architecture evolves

To render locally:
1. Install VS Code Mermaid extension
2. Preview Markdown files
3. Or use online editor: [mermaid.live](https://mermaid.live)
