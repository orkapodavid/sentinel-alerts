# Sentinel Alerts - Events and Alerts Management System

[![Reflex](https://img.shields.io/badge/Built%20with-Reflex-purple)](https://reflex.dev)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Prefect](https://img.shields.io/badge/Prefect-3.x-blue)](https://prefect.io)

A full-stack **Events and Alerts Management System** built with [Reflex](https://reflex.dev), featuring Prefect workflow integration, real-time event monitoring, and a sophisticated rule-based alert engine.

## 🚀 Features

### Alert Management
- **Rule-Based Alerts**: Create flexible alert rules with JSON parameters, importance levels, and custom triggers
- **Real-Time Monitoring**: Live blotter with auto-refresh and color-coded importance indicators
- **Event Acknowledgement**: Track and acknowledge alerts with timestamps and comments
- **Historical Analysis**: Full audit trail with advanced filtering and CSV export

### Prefect Integration
- **Deployment Triggers**: Connect alert rules to Prefect deployments for automated workflow execution
- **State Synchronization**: Real-time flow run status tracking (RUNNING, COMPLETED, FAILED, etc.)
- **UI Integration**: Direct links to Prefect dashboard for detailed flow monitoring
- **Batch Status Updates**: Efficient bulk synchronization of flow states

### Trigger System
- **Extensible Triggers**: Plugin-based architecture for custom alert triggers
- **Built-in Triggers**:
  - CPU Usage Monitor
  - Memory Leak Detector
  - Price Surge Monitor
  - Volume Spike Detector
  - Prefect Deployment Runner

### UI/UX
- **Modern Dashboard**: Clean, responsive design with Tailwind CSS
- **AG Grid Integration**: High-performance data tables with sorting, filtering, and pagination
- **System Logs**: Comprehensive logging with search and filtering
- **Settings Management**: Configure Prefect connection and UI preferences

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | [Reflex](https://reflex.dev) |
| Styling | Tailwind CSS v3 |
| Data Grid | [AG Grid](https://ag-grid.com) via reflex-enterprise |
| Workflow | [Prefect](https://prefect.io) 3.x |
| Language | Python 3.9+ |

## 📁 Project Structure


app/
├── app.py                    # Main application entry point
├── models.py                 # Data models (AlertRule, AlertEvent, LogEntry)
├── alert_runner.py           # Trigger discovery and execution engine
├── components/
│   ├── sidebar.py            # Top navigation bar
│   ├── live_blotter.py       # Real-time events dashboard
│   ├── historical_blotter.py # Event history with filters
│   ├── rule_settings.py      # Rule creation and management
│   ├── settings.py           # Application settings page
│   ├── logs.py               # System logs viewer
│   └── grid_config.py        # AG Grid column definitions
├── states/
│   ├── alert_state.py        # Main application state
│   └── ui_state.py           # UI-specific state
├── services/
│   └── prefect_service.py    # Prefect API integration
└── alert_triggers/
    ├── __init__.py           # BaseTrigger abstract class
    ├── cpu_usage_trigger.py
    ├── memory_leak_trigger.py
    ├── price_surge_trigger.py
    ├── volume_spike_trigger.py
    └── prefect_deployment_trigger.py


## 🚦 Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 18+ (for Reflex frontend)
- Prefect server (optional, for workflow integration)

### Installation

1. **Clone the repository**
   bash
   git clone https://github.com/orkapodavid/sentinel-alerts.git
   cd sentinel-alerts
   

2. **Create virtual environment**
   bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   

3. **Install dependencies**
   bash
   pip install -r requirements.txt
   

4. **Run the application**
   bash
   reflex run
   

5. **Access the dashboard**
   Open `http://localhost:3000` in your browser

### Prefect Setup (Optional)

1. **Start Prefect server**
   bash
   prefect server start
   

2. **Configure connection**
   - Navigate to Settings page
   - Set API URL: `http://localhost:4200/api`
   - Set UI URL: `http://localhost:4200`
   - Click "Test Connection"

## 📊 Data Models

### AlertRule
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | Rule display name |
| parameters | str | JSON configuration |
| importance | str | critical/high/medium/low |
| category | str | General/Market/System/Security |
| period_seconds | int | Check frequency |
| trigger_script | str | Trigger module name |
| prefect_deployment_id | str | Optional Prefect deployment |

### AlertEvent
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| rule_id | int | Foreign key to AlertRule |
| timestamp | datetime | Event occurrence time |
| message | str | Alert message |
| is_acknowledged | bool | Acknowledgement status |
| prefect_flow_run_id | str | Prefect flow run UUID |
| prefect_state | str | Current flow state |

## 🔧 Creating Custom Triggers


from app.alert_triggers import BaseTrigger
from app.models import AlertOutput

class MyCustomTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "My Custom Monitor"
    
    def get_description(self) -> str:
        return "Monitors custom metrics."
    
    def get_default_params(self) -> dict:
        return {"threshold": 100}
    
    async def check(self, params: dict) -> AlertOutput:
        return AlertOutput(
            triggered=True,
            importance="high",
            ticker="CUSTOM",
            message="Alert triggered!",
            metadata={},
            timestamp="2024-01-01 12:00:00"
        )


## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PREFECT_API_URL` | Prefect server API endpoint | `http://localhost:4200/api` |

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using [Reflex](https://reflex.dev)**
