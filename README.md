# GHWT:DE All Main Menu Music

By WitchDoctoR. The main menu music of ten Guitar Hero games in **one** menu music mod for
*Guitar Hero World Tour: Definitive Edition*, shuffled with World Tour's own six: Guitar Hero, Guitar Hero II,
Encore: Rocks the 80s, Aerosmith, Metallica, Smash Hits, Van Halen, Guitar Hero 5, Band Hero and Warriors of Rock
(99 tracks).

**Download:** `GHWTDE-All-Main-Menu-Music_1.0.zip` (302 MB) from the
[Releases page](https://github.com/jgoa156/ghwtde-all-main-menu-music/releases/latest). Copy its
`Main Menu Music Collection` folder into `DATA\MODS` and disable any other menu music mod (the game loads only one).

The DE loads only one menu music mod, so every game lives in this one. **To leave a game out**, open
`DATA\MODS\Main Menu Music Collection\menumusic.ini` and put a `;` in front of that game's `Track=` lines (each game is
a commented block); remove the `;` to bring it back.

**Loudness:** the games mix their menu songs up to 8 dB apart; every track is levelled to about -13 LUFS without
re-encoding (`mmc_level.py`, mp3gain's method: each MP3 frame's global_gain moves in 1.5 dB steps).

**World Tour's own songs** always play: the DE adds a menu music mod's tracks to its six. (Emptying that list from
the mod's `QBName` QB crashed the game at boot; that QB only holds the tracks' fretbar arrays.)

## Build

```
python build.py [--sources DIR] [--measure] [--install GAME] [--package]
python verify_mod.py "dist\Main Menu Music Collection" --sources DIR
```

`--install` keeps the games already switched off in the installed `menumusic.ini`. The mod (about 312 MB) is too
large for the repo; release zips go to GitHub Releases. Sources: one DE menu music mod folder per game plus
`mmc_levels.json` (loudness steps, `--measure` with ffmpeg).
