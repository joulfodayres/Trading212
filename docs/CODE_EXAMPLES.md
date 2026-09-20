# Trading 212 Bot - Code Examples

## Frontend Examples

### 1. Using the API Client

```typescript
// src/api/client.ts
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'https://trading212-4ojx.onrender.com'

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 2. Creating a Strategy

```typescript
// Example: Create Grid Trading Strategy
async function createGridStrategy() {
  try {
    const response = await apiClient.post('/v1/strategies', {
      name: 'Grid Trading 1%',
      description: 'Compra em -1% e vende em +1%',
      initial_investment: 10.0, // €10 per position
    })

    const strategyId = response.data.id
    console.log('Strategy created:', strategyId)

    // Add parameters for position -1
    await apiClient.post(`/v1/strategies/${strategyId}/parameters`, {
      pos: '-1',
      param1: -1.0, // Buy at -1%
      param2: 1.0,  // Sell at +1%
    })

    // Add parameters for position 0
    await apiClient.post(`/v1/strategies/${strategyId}/parameters`, {
      pos: '0',
      param1: -1.0,
      param2: 1.0,
    })

    // Add parameters for position 1
    await apiClient.post(`/v1/strategies/${strategyId}/parameters`, {
      pos: '1',
      param1: -1.0,
      param2: 1.0,
    })

    // Enable strategy (now it's valid)
    await apiClient.put(`/v1/strategies/${strategyId}`, {
      enabled: true,
    })

    return strategyId
  } catch (error) {
    console.error('Error creating strategy:', error)
    throw error
  }
}
```

### 3. Syncing Portfolio and Enabling Automation

```typescript
async function syncAndEnableAutomation(strategyId: string) {
  try {
    // 1. Sync all positions from T212
    const syncResponse = await apiClient.post('/isins/sync')
    console.log(`Synced ${syncResponse.data.synced} ISINs`)

    // 2. Get list of ISINs
    const isinsResponse = await apiClient.get('/isins')
    const isins = isinsResponse.data

    // 3. Enable automation for each ISIN with the strategy
    for (const isin of isins) {
      await apiClient.put(`/isins/${isin.id}/automation`, {
        automation_enabled: true,
        strategy_id: strategyId,
      })
      console.log(`Enabled automation for ${isin.ticker}`)
    }

    // 4. Enable global automation
    await apiClient.put('/v1/automation/enable')
    console.log('Global automation enabled')

  } catch (error) {
    console.error('Error in automation setup:', error)
    throw error
  }
}
```

### 4. Hook for Global Automation Control

```typescript
// src/hooks/useGlobalAutomation.ts
import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'

interface AutomationStatus {
  grid_trading_enabled: boolean
  scheduler_running: boolean
  cycle_count: number
  last_cycle_duration: number
}

export function useGlobalAutomation() {
  const [status, setStatus] = useState<AutomationStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/v1/automation/global-status')
      setStatus(response.data)
    } catch (error) {
      console.error('Error fetching automation status:', error)
    }
  }, [])

  const enable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await apiClient.put('/v1/automation/enable')
      setStatus(response.data)
    } catch (error) {
      console.error('Error enabling automation:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const disable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await apiClient.put('/v1/automation/disable')
      setStatus(response.data)
    } catch (error) {
      console.error('Error disabling automation:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  return { status, loading, fetchStatus, enable, disable }
}
```

### 5. Strategy Selection Component

```typescript
// Component to select strategy and enable automation for an ISIN
interface StrategySelectProps {
  isinId: string
  onSuccess: () => void
}

export function StrategySelect({ isinId, onSuccess }: StrategySelectProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategyId, setSelectedStrategyId] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load strategies
    apiClient.get('/v1/strategies').then((res) => {
      // Only valid strategies
      setStrategies(res.data.filter((s: Strategy) => s.is_valid))
    })
  }, [])

  const handleEnable = async () => {
    if (!selectedStrategyId) return

    setLoading(true)
    try {
      await apiClient.put(`/isins/${isinId}/automation`, {
        automation_enabled: true,
        strategy_id: selectedStrategyId,
      })
      onSuccess()
    } catch (error) {
      console.error('Error enabling automation:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4">
      <select
        value={selectedStrategyId}
        onChange={(e) => setSelectedStrategyId(e.target.value)}
        disabled={loading}
      >
        <option value="">Seleciona estratégia</option>
        {strategies.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name} (€{s.initial_investment})
          </option>
        ))}
      </select>
      <button onClick={handleEnable} disabled={loading || !selectedStrategyId}>
        {loading ? 'A carregar...' : 'Ativar Automação'}
      </button>
    </div>
  )
}
```

---

## Backend Examples

### 1. Automation Engine - 3-Phase Cycle

```python
# services/automation_engine.py (simplified)

class AutomationEngine:
    async def run_cycle(self) -> bool:
        """3-phase automation cycle"""
        try:
            # Phase 1: Initial Setup
            await self._phase_1_initial_setup()
            
            # Phase 2: Monitor Orders
            await self._phase_2_monitor_orders()
            
            # Phase 3: Handle Fills & Rebalance
            await self._phase_3_handle_fills()
            
            return True
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            return False

    async def _phase_1_initial_setup(self):
        """Create initial BUY/SELL pairs"""
        isins = self.db.query(ISIN).filter(
            ISIN.automation_enabled == True,
            ISIN.initial_trade == True
        ).all()

        for isin in isins:
            strategy = self.db.query(Strategy).get(isin.strategy_id)
            current_price = await self.t212_service.get_price(isin.ticker)
            
            # Get strategy parameters for current trades_balance
            params = self._get_strategy_params(strategy, isin.trades_balance)
            
            # Calculate prices
            buy_price = current_price * (1 + params.param1 / 100)
            sell_price = current_price * (1 + params.param2 / 100)
            
            # Calculate quantities
            qty = strategy.initial_investment / buy_price
            
            # Place BUY order
            buy_order = await self.t212_service.place_limit_order(
                ticker=isin.ticker,
                side='BUY',
                quantity=qty,
                price=buy_price
            )
            
            # Place SELL order
            sell_order = await self.t212_service.place_limit_order(
                ticker=isin.ticker,
                side='SELL',
                quantity=-qty,  # Negative for sell
                price=sell_price
            )
            
            # Link orders
            self.db.query(Order).filter(
                Order.t212_order_id == buy_order['id']
            ).update({'related_order_id': sell_order['id']})
            
            # Mark initial setup done
            isin.initial_trade = False
            self.db.commit()

    async def _phase_2_monitor_orders(self):
        """Monitor pending orders"""
        orders = self.db.query(Order).filter(
            Order.automation_status == 'W'  # Watch status
        ).all()

        for order in orders:
            # Poll T212 for order status
            t212_order = await self.t212_service.get_order(order.t212_order_id)
            
            # Update local order
            order.status = t212_order['status']
            order.filled_quantity = t212_order['filledQuantity']
            
            # If filled, mark as executed
            if t212_order['status'] == 'FILLED':
                order.automation_status = 'E'
                self.db.commit()

    async def _phase_3_handle_fills(self):
        """Handle filled orders and rebalance"""
        orders = self.db.query(Order).filter(
            Order.status == 'FILLED',
            Order.automation_status == 'E'
        ).all()

        for order in orders:
            isin = order.isin
            
            # Update portfolio position
            position = await self.t212_service.get_position(isin.ticker)
            isin.quantity = position['quantity']
            isin.current_price = position['current_price']
            
            # Adjust trades_balance
            if order.side == 'BUY':
                isin.trades_balance -= 1  # Move to lower grid
            else:  # SELL
                isin.trades_balance += 1  # Move to higher grid
            
            # Cancel related order
            related = self.db.query(Order).filter(
                Order.id == order.related_order_id
            ).first()
            if related:
                await self.t212_service.cancel_order(related.t212_order_id)
                related.automation_status = 'C'
            
            # Get new strategy parameters for new trades_balance
            strategy = isin.strategy
            new_params = self._get_strategy_params(strategy, isin.trades_balance)
            
            # Place new BUY/SELL pair at new grid level
            current_price = position['current_price']
            buy_price = current_price * (1 + new_params.param1 / 100)
            sell_price = current_price * (1 + new_params.param2 / 100)
            qty = strategy.initial_investment / buy_price
            
            buy_order = await self.t212_service.place_limit_order(
                ticker=isin.ticker,
                side='BUY',
                quantity=qty,
                price=buy_price
            )
            
            sell_order = await self.t212_service.place_limit_order(
                ticker=isin.ticker,
                side='SELL',
                quantity=-qty,
                price=sell_price
            )
            
            # Link and save new orders
            self.db.add(Order(
                isin_id=isin.id,
                t212_order_id=buy_order['id'],
                side='BUY',
                quantity=qty,
                automation_status='W'
            ))
            self.db.add(Order(
                isin_id=isin.id,
                t212_order_id=sell_order['id'],
                side='SELL',
                quantity=-qty,
                automation_status='W'
            ))
            
            self.db.commit()

    def _get_strategy_params(self, strategy: Strategy, trades_balance: int):
        """Get strategy parameters for current trades_balance"""
        exact_params = self.db.query(StrategyParameter).filter(
            StrategyParameter.strategy_id == strategy.id,
            StrategyParameter.pos == str(trades_balance)
        ).first()
        
        if exact_params:
            return exact_params
        
        # Fallback logic
        if trades_balance > 0:
            # Use max pos <= trades_balance
            return self.db.query(StrategyParameter).filter(
                StrategyParameter.strategy_id == strategy.id,
                StrategyParameter.pos.cast(Integer) <= trades_balance
            ).order_by(
                StrategyParameter.pos.cast(Integer).desc()
            ).first()
        elif trades_balance < 0:
            # Use min pos >= trades_balance
            return self.db.query(StrategyParameter).filter(
                StrategyParameter.strategy_id == strategy.id,
                StrategyParameter.pos.cast(Integer) >= trades_balance
            ).order_by(
                StrategyParameter.pos.cast(Integer).asc()
            ).first()
        else:
            # Zero must exist
            params = self.db.query(StrategyParameter).filter(
                StrategyParameter.strategy_id == strategy.id,
                StrategyParameter.pos == '0'
            ).first()
            if not params:
                raise ValueError(f"Strategy {strategy.id} missing pos=0 parameters")
            return params
```

### 2. Strategy Validation

```python
# routes/strategies.py

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from models.db import Strategy, StrategyParameter

router = APIRouter(prefix="/api/v1", tags=["strategies"])

def _check_strategy_valid(db: Session, strategy_id: str) -> bool:
    """Check if strategy has required parameters"""
    required_positions = {'-1', '0', '1'}
    existing_positions = set()
    
    params = db.query(StrategyParameter).filter(
        StrategyParameter.strategy_id == strategy_id
    ).all()
    
    for param in params:
        existing_positions.add(param.pos)
    
    return required_positions.issubset(existing_positions)

@router.put("/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).get(strategy_id)
    if not strategy:
        raise HTTPException(404, "Strategy not found")
    
    # If trying to enable, validate
    if update_data.get('enabled') and not _check_strategy_valid(db, strategy_id):
        raise HTTPException(
            400,
            "Cannot enable strategy. Missing parameters for pos: -1, 0, 1"
        )
    
    # Update strategy
    for key, value in update_data.items():
        if hasattr(strategy, key):
            setattr(strategy, key, value)
    
    db.commit()
    return strategy
```

### 3. Portfolio Sync Endpoint

```python
# routes/isins.py

@router.post("/isins/sync")
async def sync_portfolio(db: Session = Depends(get_db)):
    """Sync all positions from T212 to isins table"""
    t212_service = get_t212_service()
    
    try:
        # Fetch positions from T212
        positions = await t212_service.get_positions()
        
        synced = 0
        created = 0
        updated = 0
        
        for position in positions:
            isin_obj = db.query(ISIN).filter(
                ISIN.isin == position['instrumentIsin']
            ).first()
            
            if not isin_obj:
                # Create new ISIN
                isin_obj = ISIN(
                    isin=position['instrumentIsin'],
                    ticker=position['ticker'],
                    name=position['instrumentName'],
                    currency=position['currency'],
                    quantity=position['quantity'],
                    current_price=position['currentPrice'],
                    average_price_paid=position['averagePricePaid'],
                    quantity_available_for_trading=position['quantityAvailableForTrading'],
                    quantity_in_pies=position['quantityInPies'],
                    instrument_json=position,  # Store full data
                    position_created_at=position['createdAt'],
                )
                db.add(isin_obj)
                created += 1
            else:
                # Update existing
                isin_obj.quantity = position['quantity']
                isin_obj.current_price = position['currentPrice']
                isin_obj.average_price_paid = position['averagePricePaid']
                isin_obj.instrument_json = position
                updated += 1
            
            synced += 1
        
        db.commit()
        
        return {
            "success": True,
            "synced": synced,
            "created": created,
            "updated": updated,
            "errors": 0
        }
    
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Database Examples

### 1. Creating Initial App Parameters

```sql
-- Create singleton app_parameters entry
INSERT INTO app_parameters (id, scheduler_interval_seconds, grid_trading_enabled)
VALUES (
  '00000000-0000-0000-0000-000000000001'::uuid,
  15,  -- 15 seconds default
  true
);

-- Later: Update interval
UPDATE app_parameters
SET scheduler_interval_seconds = 20
WHERE id = '00000000-0000-0000-0000-000000000001'::uuid;

-- Later: Disable automation
UPDATE app_parameters
SET grid_trading_enabled = false
WHERE id = '00000000-0000-0000-0000-000000000001'::uuid;
```

### 2. Creating Strategies and Parameters

```sql
-- Create strategy
INSERT INTO strategies (id, name, description, initial_investment, enabled)
VALUES (
  gen_random_uuid(),
  'Grid Trading 1%',
  'Buys at -1% and sells at +1%',
  10.0,
  false
)
RETURNING id;

-- Add parameters (replace strategy_id)
INSERT INTO strategy_parameters (strategy_id, pos, param1, param2)
VALUES
  ('strategy-id', '-1', -1.0, 1.0),
  ('strategy-id', '0', -1.0, 1.0),
  ('strategy-id', '1', -1.0, 1.0);

-- Enable strategy
UPDATE strategies
SET enabled = true
WHERE id = 'strategy-id';
```

### 3. Linking ISIN to Strategy and Orders

```sql
-- Update ISIN with strategy
UPDATE isins
SET strategy_id = 'strategy-id',
    automation_enabled = true,
    initial_trade = true
WHERE ticker = 'VWRL';

-- Create orders for grid trading
INSERT INTO orders (isin_id, t212_order_id, side, quantity, status, automation_status, type)
VALUES
  ('isin-id', 123456, 'BUY', 10.5, 'CONFIRMED', 'W', 'LIMIT'),
  ('isin-id', 123457, 'SELL', -10.5, 'CONFIRMED', 'W', 'LIMIT');

-- Link orders
UPDATE orders
SET related_order_id = (
  SELECT id FROM orders WHERE t212_order_id = 123457
)
WHERE t212_order_id = 123456;
```

---

**Last Updated:** 2026-09-20
