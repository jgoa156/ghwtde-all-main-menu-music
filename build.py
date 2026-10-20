"""Build the Main Menu Music Collection mod (every game's menu music in one GHWT:DE menu music mod).

  python build.py [--sources DIR] [--measure] [--install GAME] [--package]

  --sources DIR   the source menu music mods, one folder per game (default: MMC_SOURCES or
                  E:/Dev/ghwt/menu-music-all/sources); World Tour's comes from make_wt_source.py
  --measure       measure every track's loudness again with ffmpeg and rewrite <sources>/mmc_levels.json
  --install GAME  copy the mod into GAME/DATA/MODS; Track lines switched off (;Track=) in the installed
                  menumusic.ini stay switched off
  --package       dist/GHWTDE-All-Main-Menu-Music_<version>.zip (the mod folder + README.txt) for GitHub Releases

The mod is always built into dist/Main Menu Music Collection first, with every game switched on.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import json
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mmc_core as core  # noqa: E402
import mmc_level  # noqa: E402

DEFAULT_SOURCES = os.environ.get('MMC_SOURCES', r'E:\Dev\ghwt\menu-music-all\sources')
DIST = os.path.join(HERE, 'dist')
PACKAGE = f'GHWTDE-All-Main-Menu-Music_{core.VERSION}'


def measure_levels(sources):
    """{source folder: {track: gain steps}}: each track's integrated loudness (EBU R128) and sample peak, by ffmpeg."""
    levels = {}
    for s in sources:
        lv = {}
        for c in s.clips:
            with open(c.bank, 'rb') as f:
                f.seek(c.off)
                data = f.read(c.nbytes)
            r = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-f', 'mp3', '-i', 'pipe:0',
                                '-af', 'ebur128=framelog=quiet:peak=sample', '-f', 'null', '-'],
                               input=data, capture_output=True)
            err = r.stderr.decode(errors='replace').splitlines()
            lufs = float([l for l in err if l.strip().startswith('I:')][-1].split()[1])
            peak = float([l for l in err if l.strip().startswith('Peak:')][-1].split()[1])
            lv[c.name] = mmc_level.steps_for(lufs, peak)
            print(f'  {s.code:6s} {c.name:30s} {lufs:6.1f} LUFS  peak {peak:5.1f} dB  -> {lv[c.name] * mmc_level.STEP_DB:+.1f} dB')
        levels[os.path.basename(s.folder)] = lv
    return levels


def install(mod, game):
    """Copy the built mod into GAME/DATA/MODS, keeping the Track lines the player switched off."""
    target = os.path.join(core.check_game_dir(game), core.MOD_DIR)
    off = set()
    old_ini = os.path.join(target, 'menumusic.ini')
    if os.path.isfile(old_ini):
        with open(old_ini, encoding='utf-8', errors='replace') as f:
            off = {m.group(1).strip().lower() for m in re.finditer(r'^\s*;\s*Track\s*=\s*(.+)$', f.read(), re.M)}
    tmp = target + '.building'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(mod, tmp)
    ini = os.path.join(tmp, 'menumusic.ini')
    with open(ini, encoding='utf-8') as f:
        lines = f.read().split('\n')
    kept = 0
    for i, line in enumerate(lines):
        m = re.match(r'^Track=(.+)$', line)
        if m and m.group(1).strip().lower() in off:
            lines[i] = ';' + line
            kept += 1
    with open(ini, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines))
    if os.path.isdir(target):
        shutil.rmtree(target)
    os.replace(tmp, target)
    print(f'installed {target} ({kept} tracks kept switched off)')


def readme(sources, info):
    lines = [
        f'Main Menu Music Collection {core.VERSION} for Guitar Hero World Tour: Definitive Edition',
        '=' * 78,
        'By WitchDoctoR',
        '',
        'The main menu music of every Guitar Hero game below, in one menu music mod, shuffled. The DE loads only one',
        'menu music mod, so every game lives in this one and you switch off the ones you do not want.',
        '',
        'INSTALL',
        '  Copy the "Main Menu Music Collection" folder into DATA\\MODS in your game folder (the one with',
        '  GHWT_Definitive.exe). Disable any other menu music mod: the game loads only one.',
        '',
        'SWITCHING GAMES OFF',
        '  Open DATA\\MODS\\Main Menu Music Collection\\menumusic.ini. Each game is a block of Track lines under its',
        '  name. Put a ; at the start of each Track line of a game to leave it out of the shuffle; remove the ; to',
        '  bring it back. Leave the QBName line as it is (it stops World Tour\'s songs playing twice).',
        '',
        'LOUDNESS',
        '  The games mix their menu songs up to 8 dB apart. Every track is levelled to about '
        f'{mmc_level.TARGET_LUFS:.0f} LUFS without',
        '  re-encoding (mp3gain\'s method: each MP3 frame\'s gain field moves in 1.5 dB steps).',
        '',
        f'GAMES ({info["tracks"]} tracks)',
    ]
    for s in sources:
        lines.append(f'  {s.name:36s} {s.ntracks:3d} tracks')
    lines += ['', 'CREDITS']
    by_author = {}
    for s in sources:
        by_author.setdefault(s.author or 'unknown', []).append(s.name)
    for author, names in by_author.items():
        lines.append(f'  Menu music mod(s) by {author}: ' + ', '.join(names))
    lines += ['  The collection: WitchDoctoR. The songs belong to their owners; this is a fan mod.', '']
    text = '\r\n'.join(lines)
    text.encode('ascii')
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sources', default=DEFAULT_SOURCES)
    ap.add_argument('--measure', action='store_true')
    ap.add_argument('--install', metavar='GAME')
    ap.add_argument('--package', action='store_true')
    a = ap.parse_args()
    sources, problems = core.find_sources(a.sources)
    if problems or not sources:
        sys.exit(f'Bad sources in {a.sources}: {problems or "none found"}')
    if a.measure:
        with open(os.path.join(a.sources, mmc_level.LEVELS_FILE), 'w', encoding='utf-8') as f:
            json.dump(measure_levels(sources), f, indent=1)
        sources, _ = core.find_sources(a.sources)
    try:
        info = core.build_mod(DIST, sources)
    except core.MenuMusicError as e:
        sys.exit(f'build failed: {e}')
    print(f'built {info["mod"]}: {len(sources)} games, {info["tracks"]} tracks, {info["bytes"] / 1e6:.0f} MB')
    for code, old, new in info['renames']:
        print(f'  renamed {code} {old} -> {new}')
    if a.install:
        install(info['mod'], a.install)
    if a.package:
        zpath = os.path.join(DIST, PACKAGE + '.zip')
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.writestr(f'{PACKAGE}/README.txt', readme(sources, info))
            for root, _, files in os.walk(info['mod']):
                for fn in files:
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(PACKAGE, core.MOD_DIR, os.path.relpath(p, info['mod'])))
        print(f'{zpath}: {os.path.getsize(zpath) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
