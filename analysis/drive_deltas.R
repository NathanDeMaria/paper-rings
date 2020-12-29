library(tidyverse)

REFRESH <- F

# define which seasons shall be loaded
file_name <- 'all_pbp.csv'
pbp <- if (REFRESH) {
  seasons <- seq(1999, 2020)
  pbp <- purrr::map_df(seasons, function(x) {
    readRDS(
      url(
        glue::glue("https://raw.githubusercontent.com/guga31bb/nflfastR-data/master/data/play_by_play_{x}.rds")
      )
    )
  })
  
  pbp %>% write_csv(file_name)
  pbp
} else {
  read_csv(file_name)
}


drive_start_wps <- pbp %>%
  filter(play_id == drive_play_id_started) %>% 
  group_by(season, week, fixed_drive, game_id, home_team, away_team, game_seconds_remaining, score_differential, posteam) %>% 
  summarize(home_start_wp = first(home_wp))
drive_end_wps <- pbp %>%
  filter(play_id == drive_play_id_ended) %>% 
  group_by(fixed_drive, game_id, home_team, away_team, score_differential_post, posteam) %>% 
  summarize(home_end_wp = first(home_wp_post))
drive_deltas <- drive_start_wps %>%
  inner_join(drive_end_wps, by = c("fixed_drive", "posteam", "home_team", "away_team", "game_id")) %>% 
  mutate(posteam_start_wp = if_else(posteam == home_team, home_start_wp, 1 - home_start_wp),
         posteam_end_wp = if_else(posteam == home_team, home_end_wp, 1 - home_end_wp)) %>% 
  mutate(posteam_drive_wpa = posteam_end_wp - posteam_start_wp,
         posteam_drive_success = posteam_drive_wpa >= 0) %>% 
  mutate(defteam = if_else(posteam == home_team, away_team, home_team))

# Get rid of weird things
# - sometimes the first win prob of the game has the home team as near 0 or 1
drive_deltas <- drive_deltas %>% 
  filter(home_start_wp < 0.9, home_start_wp > 0.1)
# Consider also dropping/adjusting for:
# - drives that start near the end of halves (is it fair to "expect" win prob to move on those?)
# - vs. "expected WP change" instead of positive/negative

drive_deltas %>% write_csv('../drive_deltas.csv')
