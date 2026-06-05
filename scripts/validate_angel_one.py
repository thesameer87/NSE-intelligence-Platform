import asyncio
import json
import websockets
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv(".env")

WS_URL = "wss://nse-intelligence-mk64.onrender.com/ws/stream"
DATABASE_URL = os.getenv("DATABASE_URL")

async def validate_websocket():
    print("\n--- Connecting to Render WebSocket ---")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected successfully. Waiting for live events...")
            
            # Since we only receive, we just wait for 2 events
            events_captured = []
            try:
                for _ in range(5):
                    msg = await asyncio.wait_for(ws.recv(), timeout=15)
                    data = json.loads(msg)
                    event_type = data.get("event")
                    print(f"\n[WebSocket Frame] {event_type}:")
                    print(json.dumps(data, indent=2))
                    events_captured.append(event_type)
                    
                    if "market_tick" in events_captured and "prediction_update" in events_captured:
                        print("Successfully captured both required event frames!")
                        break
            except asyncio.TimeoutError:
                print("Timeout waiting for frames. Render might be failing ingestion or market closed.")
                
            return events_captured
    except Exception as e:
        print(f"WebSocket Error: {e}")
        return []

async def validate_database():
    print("\n--- Connecting to Supabase Database ---")
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine)
    
    async with async_session() as session:
        print("Querying latest intraday_ticks...")
        result = await session.execute(text("SELECT symbol, timestamp, ltp FROM intraday_ticks ORDER BY timestamp DESC LIMIT 3"))
        rows = result.fetchall()
        print("Recent Ticks:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | LTP: {r[2]}")
            
        print("\nQuerying latest trading_signals...")
        result_sig = await session.execute(text("SELECT symbol, signal, confidence, created_at FROM trading_signals ORDER BY created_at DESC LIMIT 3"))
        sig_rows = result_sig.fetchall()
        print("Recent Signals:")
        if not sig_rows:
            print("  No recent signals generated (confidence threshold likely not met).")
        for r in sig_rows:
            print(f"  {r[0]} | {r[1]} | Conf: {r[2]} | {r[3]}")
            
    await engine.dispose()

async def main():
    print("Starting Angel One Live Integration Validation...")
    events = await validate_websocket()
    await validate_database()
    
    if "market_tick" in events:
        print("\nSUCCESS: Render is successfully authenticating with Angel One and fetching live ticks!")
    else:
        print("\nFAILURE: Did not receive live ticks from Render.")

if __name__ == "__main__":
    asyncio.run(main())
