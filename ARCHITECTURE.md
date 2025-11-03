# Architecture Diagram - Trading Analytics Platform

## Draw.io Instructions

This file contains instructions to create the architecture diagram in draw.io.

### Diagram Sections:

## 1. Frontend Layer (Top)
```
┌─────────────────────────────────────────────────────┐
│            Streamlit Dashboard (frontend.py)        │
│  ┌──────────┬──────────┬──────────┬──────────────┐ │
│  │ Overview │ Analytics│ Backtest │ Alerts│Export│ │
│  └──────────┴──────────┴──────────┴──────────────┘ │
│  Interactive Charts (Plotly) | User Controls       │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/WebSocket
                      ▼
```

## 2. Application Layer (Middle)
```
┌─────────────────────────────────────────────────────┐
│      Application Orchestrator (app.py)              │
│  TradingAnalyticsApp                                │
│  - Coordinates all backend services                 │
│  - Provides clean API interface                     │
│  - Manages service lifecycle                        │
└────┬────┬────┬────┬────┬───────────────────────────┘
     │    │    │    │    │
     ▼    ▼    ▼    ▼    ▼
```

## 3. Backend Services Layer (Bottom)
```
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│  Data      │ │  Storage   │ │ Resampling │ │ Analytics  │ │   Alerts   │
│ Ingestion  │ │   Layer    │ │   Engine   │ │   Engine   │ │  Manager   │
│            │ │            │ │            │ │            │ │            │
│ - WebSocket│ │ - SQLite   │ │ - Tick→    │ │ - OLS      │ │ - Rules    │
│ - Binance  │ │ - Redis    │ │   OHLCV    │ │ - Kalman   │ │ - Triggers │
│ - Async    │ │ - Hybrid   │ │ - Multi TF │ │ - Stats    │ │ - Callback │
└────┬───────┘ └─────┬──────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘
     │               │                │               │              │
     └───────────────┴────────────────┴───────────────┴──────────────┘
                                    │
                                    ▼
```

## 4. External Systems (Left/Right)
```
┌─────────────────┐                              ┌─────────────────┐
│  Binance API    │                              │  File System    │
│  wss://fstream  │                              │  - SQLite DB    │
│  .binance.com   │                              │  - CSV Exports  │
└─────────────────┘                              └─────────────────┘
```

## 5. Data Flow Diagram

### Flow 1: Real-Time Ingestion
```
Binance API → WebSocket Client → Tick Data → Storage Layer
                                               ↓
                                          SQLite + Redis
```

### Flow 2: Resampling
```
Storage Layer → Resampling Engine → OHLCV Bars → Storage Layer
(Ticks)         (Background Thread)   (1s/1m/5m)    (Cached)
```

### Flow 3: Analytics Computation
```
User Request → App.compute_pair_analytics() → Storage.get_ohlcv()
                                            → Analytics.ols_regression()
                                            → Analytics.compute_zscore()
                                            → Alert.check_rules()
                                            → Frontend (Charts)
```

### Flow 4: Alert Workflow
```
Analytics Data → Alert Manager → Rule Evaluation → Alert Triggered
                                                  ↓
                                           Callbacks (Log/Notify)
                                                  ↓
                                           Frontend Display
```

## 6. Component Interaction Matrix

| Component | Depends On | Provides To | Communication |
|-----------|-----------|-------------|---------------|
| Frontend | App | User Interface | Method Calls |
| App | All Services | Orchestration | Method Calls |
| Ingestion | Storage | Tick Data | Callback |
| Storage | None | Data Access | Direct |
| Resampling | Storage | OHLCV Data | Background Thread |
| Analytics | None | Calculations | Direct |
| Alerts | None | Notifications | Callback |

## 7. Scaling Strategy Diagram

### Current (Single Machine)
```
┌──────────────────────────────────────┐
│         Single Process               │
│  ┌──────────────────────────────┐   │
│  │ Streamlit App                │   │
│  │  ├─ Backend Services         │   │
│  │  ├─ SQLite DB                │   │
│  │  └─ Redis Cache              │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

### Production (Distributed)
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  API Server  │────▶│  Analytics   │
│  (React)     │     │  (FastAPI)   │     │   Workers    │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                            ▼                     ▼
                     ┌──────────────┐      ┌──────────────┐
                     │  Ingestion   │      │ TimescaleDB  │
                     │  (Kafka)     │      │ + Redis      │
                     └──────────────┘      └──────────────┘
```

## Design Notes for Draw.io

### Colors:
- **Frontend**: Light Blue (#E3F2FD)
- **Application Layer**: Green (#E8F5E9)
- **Backend Services**: Yellow (#FFF9C4)
- **Storage**: Orange (#FFE0B2)
- **External Systems**: Gray (#F5F5F5)

### Shapes:
- **Services**: Rounded rectangles
- **Data flows**: Arrows with labels
- **Databases**: Cylinder shapes
- **External systems**: Dotted border rectangles

### Layout:
- Top-to-bottom for main flow
- Left-to-right for service dependencies
- Group related components with containers

---

## Create in Draw.io:

1. Open draw.io (app.diagrams.net)
2. Create new "Blank Diagram"
3. Add shapes from left panel:
   - Rectangles for components
   - Cylinders for databases
   - Arrows for data flow
4. Arrange as shown above
5. Add text labels
6. Export as:
   - PNG (for README)
   - SVG (for scaling)
   - .drawio (source file)

---

## Key Concepts to Highlight:

1. **Modularity**: Each service is independent
2. **Data Flow**: Clear path from ingestion to visualization
3. **Extensibility**: Easy to add new components
4. **Separation of Concerns**: Frontend/Backend/Storage clearly separated
5. **Scaling Path**: Show current vs future architecture
