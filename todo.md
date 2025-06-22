# Data
- download all images into a database for faster calling
    - script finished, partially downloaded games
- precompute recommendations for all games for the dialog boxes
- import pax games
    - create a new import script in the same style of @import_data.py and in the same directory which imports all csvs from the @/pax directory.  These csv files contain a list of board game names which match the name column in the BoardGame Model of the @models.py file.  Also add the accompanying models in @models.py and schemas in @schemas.py .  The table will have three columns name, pax, and year.  Add the ability to filter  


# UI 
- Move the filters to the top of the page
- filter by pax games 
- recommend based on multiple games (pro and con)

# App
- Move to a server