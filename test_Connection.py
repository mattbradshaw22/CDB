from CRUD_Module import CRUD

crud = CRUD()

# Example read (should return list, even if empty)
records = crud.read()
print("Records found:", len(records))