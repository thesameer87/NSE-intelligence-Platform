import asyncio
import os
import lightgbm as lgb
import numpy as np
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.session import async_session_maker
from backend.db.models.prediction import ModelRegistry
from sqlalchemy import select

async def generate_dummy_model(artifact_path: str, objective: str = 'binary'):
    # Create directory if not exists
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    # Generate dummy data
    X = np.random.rand(10, 16)
    y = np.random.randint(0, 2, size=10) if objective == 'binary' else np.random.rand(10)
    
    train_data = lgb.Dataset(X, label=y)
    params = {'objective': objective, 'num_leaves': 2, 'verbose': -1}
    
    print(f"Training dummy {objective} model for {artifact_path}...")
    booster = lgb.train(params, train_data, num_boost_round=1)
    booster.save_model(artifact_path)

async def seed_models():
    models_to_seed = [
        {'name': 'intraday_clf', 'objective': 'binary', 'version': 'v1'},
        {'name': 'intraday_reg', 'objective': 'regression', 'version': 'v1'},
        {'name': 'nextday_clf', 'objective': 'binary', 'version': 'v1'},
        {'name': 'nextday_reg', 'objective': 'regression', 'version': 'v1'},
    ]
    
    async with async_session_maker() as session:
        for model in models_to_seed:
            artifact_path = f"models/{model['name']}/{model['version']}.txt"
            
            # 1. Generate structural artifact
            await generate_dummy_model(artifact_path, model['objective'])
            
            # 2. Upsert Registry
            stmt = select(ModelRegistry).where(
                ModelRegistry.model_name == model['name'],
                ModelRegistry.version == model['version']
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.artifact_path = artifact_path
                existing.active = True
            else:
                new_registry = ModelRegistry(
                    model_name=model['name'],
                    version=model['version'],
                    artifact_path=artifact_path,
                    active=True
                )
                session.add(new_registry)
                
        await session.commit()
        print("Successfully seeded ModelRegistry and artifacts.")

if __name__ == "__main__":
    asyncio.run(seed_models())
