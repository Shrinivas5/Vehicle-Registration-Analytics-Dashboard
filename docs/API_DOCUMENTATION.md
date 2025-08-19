# API Documentation

## Analytics Engine API

### VahanAnalyticsEngine

The core analytics engine providing comprehensive market analysis capabilities.

#### Initialization
```python
from src.database_manager import VahanDatabaseManager
from src.analytics_engine import VahanAnalyticsEngine

db_manager = VahanDatabaseManager()
analytics_engine = VahanAnalyticsEngine(db_manager)
