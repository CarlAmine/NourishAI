# NourishAI Data

This folder holds raw documents for ingestion. Each subfolder can contain one or more JSON files.

## recipes/*.json
Expected fields per recipe (flexible):
- id or recipe_id
- title or name
- ingredients (list or comma-separated string)
- instructions or steps (list or string)
- meal_type (list)
- dietary_tags (list)
- cuisine (list)
- nutrition (object with calories, protein_g, carbs_g, fat_g)
- source (string)

## nutrition/*.json
Expected fields per reference:
- id
- title
- text
- nutrients (list)
- source

## ingredients/*.json
Expected fields per ingredient:
- id
- name
- aliases (list)
- notes
- substitutions (list)
- allergens (list)
- nutrition (object with calories, protein_g, carbs_g, fat_g)
- source
