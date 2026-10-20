"""Make a source folder of Guitar Hero World Tour's own menu music, from the DE's stream bank:
python make_wt_source.py <game folder> <sources folder>

World Tour's six menu songs (global_sound_logic's menu_music_songs: Menu_Music_Heartbreaker ... Menu_Music_Everlong)
live in DATA\\STREAMS\\streamall_wtde.fsb.xen with every other stock stream. Their samples are copied as they are into a
source mod folder like the other games' ("(GHWT) Main Menu Music"), with the delay and volume the DE gives them, so the
collection can carry World Tour as one more game block. The collection mod then always clears the DE's own list (its
QB, NO_WT_QB in mmc_core), and World Tour's songs play only from that block.
"""
import os
import struct
import sys

import mmc_core as core

FOLDER = '(GHWT) Main Menu Music'
FSB = 'GHWT_Music_Menu'
# stream, delay (s) and volume (dB) from global_sound_logic's menu_music_songs
TRACKS = [
    ('Menu_Music_Heartbreaker', 0.0, -5),
    ('Menu_Music_HotForTeacher', 0.0, -4),
    ('Menu_Music_NoSleepTilBrooklyn', 12.08, -5),
    ('Menu_Music_Stranglehold', 5.638, -5.5),
    ('Menu_Music_Today', 11.7, -6),
    ('Menu_Music_Everlong', 17.02, -6),
]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    game, sources = sys.argv[1], sys.argv[2]
    bank = os.path.join(game, 'DATA', 'STREAMS', 'streamall_wtde.fsb.xen')
    fsb = core.read_fsb(bank)
    _, index, _ = core.read_dat(bank[:-len('.fsb.xen')] + '.dat.xen')
    picked = []
    for name, _, _ in TRACKS:
        i = index.get(core.qbkey(name))
        if i is None:
            raise core.MenuMusicError(f'{name} is not in {bank}')
        picked.append(fsb['samples'][i])

    out = os.path.join(sources, FOLDER)
    os.makedirs(os.path.join(out, 'Content'), exist_ok=True)
    with open(bank, 'rb') as f:
        h48 = f.read(48)
        headers, data = b'', []
        for s in picked:
            f.seek(s['off'])
            data.append(f.read(s['nbytes']))
            headers += s['header']
    hdr = bytearray(h48)
    struct.pack_into('<III', hdr, 4, len(picked), len(headers), sum(len(d) for d in data))
    with open(os.path.join(out, 'Content', FSB + '.fsb.xen'), 'wb') as f:
        f.write(bytes(hdr) + headers + b''.join(data))
    dat = struct.pack('>II', len(picked), core.qbkey(FSB))
    for i, (name, _, _) in enumerate(TRACKS):
        dat += struct.pack('>II', core.qbkey(name), i) + bytes(12)
    with open(os.path.join(out, 'Content', FSB + '.dat.xen'), 'wb') as f:
        f.write(dat)
    ini = ['[ModInfo]', 'Name=GHWT_Music_Menu', 'Description=Guitar Hero World Tour menu music, from the game itself',
           'Author=Neversoft', 'Version=1.0', '', '[MenuMusicInfo]', f'FSBName={FSB}']
    ini += [f'Track={n}' for n, _, _ in TRACKS]
    for n, delay, vol in TRACKS:
        ini += ['', f'[{n}]', f'Delay={delay}', f'Volume={vol}', 'Offset=0']
    with open(os.path.join(out, 'menumusic.ini'), 'w', newline='\r\n') as f:
        f.write('\n'.join(ini) + '\n')
    print(f'{out}: {len(picked)} tracks, {sum(len(d) for d in data) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
