
# Indices.py
from CRUD_Module import CRUD

# Initialize CRUD (loads credentials from .env automatically)
crud = CRUD()

# Create indexes if they don't already exist
print("📚 Creating indexes...")
crud.collection.create_index([("decedent.last", 1)])
crud.collection.create_index([("plot.section", 1)])
print("✅ Index creation complete!")