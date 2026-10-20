# GHWT:DE All Main Menu Music

By WitchDoctoR. The main menu music of eleven Guitar Hero games in **one** menu music mod for
*Guitar Hero World Tour: Definitive Edition*, shuffled: World Tour, Guitar Hero, Guitar Hero II, Encore: Rocks the
80s, Aerosmith, Metallica, Smash Hits, Van Halen, Guitar Hero 5, Band Hero and Warriors of Rock (105 tracks).

The DE loads only one menu music mod, so every game lives in this one. **To leave a game out**, open
`DATA\MODS\Main Menu Music Collection\menumusic.ini` and put a `;` in front of that game's `Track=` lines (each game is
a commented block); remove the `;` to bring it back.

**Loudness:** the games mix their menu songs up to 8 dB apart; every track is levelled to about -13 LUFS without
re-encoding (`mmc_level.py`, mp3gain's method: each MP3 frame's global_gain moves in 1.5 dB steps).

**World Tour's own songs** are one more game block (`make_wt_source.py` copies them from the DE's stream bank). The
mod's `NoWorldTour` QB empties the DE's built-in `menu_music_songs` list so they don't play twice. The empty array is
written the way the game writes its own (element type 0): an empty *struct* array corrupted the heap when the DE
added the mod's tracks and crashed the game at boot.

## Build

```
python build.py [--sources DIR] [--measure] [--install GAME] [--package]
python verify_mod.py "dist\Main Menu Music Collection" --sources DIR
```

`--install` keeps the games already switched off in the installed `menumusic.ini`. The mod (about 312 MB) is too
large for the repo; release zips go to GitHub Releases. Sources: one DE menu music mod folder per game plus
`mmc_levels.json` (loudness steps, `--measure` with ffmpeg).
