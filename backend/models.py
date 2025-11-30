from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base

class EnergyGeneration(Base):
    __tablename__ = "energy_generation"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True) # When the data was recorded
    fuel_type = Column(String, index=True)   # e.g., "sun", "wind", "natural gas"
    value = Column(Float)                    # Megawatt-hours (MWh)
    
    # I would add a composite index or unique constraint in a real app
    # but for now this is sufficient