# NFL vs Spread

Try out some NFL models against the spread

## Workflow

Doing things in here is pretty manual...for now.
Here's a rough log of what I've done:

1. Run `analysis/drive_deltas.R` to get `drive_deltas.csv`. Rerun this if you want to get the latest play-by-play
2. Run `main.py` to get the `{week}.json` files
3. Run `aggregate.py` to combine them into one `games_with_ratings.csv`
4. Check out the `.Rmd` analysis file underneath `./analysis`
