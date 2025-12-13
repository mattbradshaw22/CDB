from CRUD_Module import CRUD

crud = CRUD()  # no ARGS uses .env

# Example insert (graves / names)
from datetime import date

doc = {

    "cemetery": "howard street",
    "section": "1007",
    "lot": "29",
    "decedent": {"first": "Bruce","middle": "H", "last": "Simpson"},
    "death_date": date(2025, 11, 23).isoformat(),
    "burial_date": date(2025, 12, 2).isoformat(),
    "burial_type": "Cremation",
    "notes": "marble cultured urn",
    "military_veteran": "yes",
    "branch": "Army"
}
new_id = crud.create(doc)

doc = {

    "cemetery": "kizer",
    "section": "2N",
    "lot": "345",
    "decedent": {"first": "Maryellen","middle": "", "last": "Dickie"},
    "birth_date": date(1967, 3,18).isoformat(),
    "death_date": date(2025, 11, 27).isoformat(),
    "burial_date": date(2025, 12, 10).isoformat(),
    "burial_type": "Cremation",
    "notes": "marble cultured urn",

}
new_id2 = crud.create(doc)

# Read it back
rows = crud.read({"_id": new_id})
# Update
#crud.update({"_id": new_id}, {"notes": "Beloved mother and friend"})
# Delete one
#crud.delete({"_id": new_id})