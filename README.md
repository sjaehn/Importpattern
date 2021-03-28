# Importpattern

Tool to import simple drum patterns in a format like:
```
bps = 1.5
bd = " [ t ~ ~ ~ ] [ ~ ~ ~ ~ ] [ t ~ t ~ ] [ t ~ ~ ~ ] "
sn = " [ ~ ~ ~ ~ ] [ t ~ ~ ~ ] [ ~ ~ ~ ~ ] [ t ~ ~ ~ ] "
```

from Tidal or similar to B.SEQuencer presets. The symbols must be those defined for `drumN` in
https://github.com/tidalcycles/Tidal/blob/main/src/Sound/Tidal/Params.hs for a successful import.
An accent note pattern may be added using the symbol `ac`. The import is limited to the size of
the B.SEQuencer pattern (max. 16 instruments, max. 32 steps). 

## Usage 
```
python importpattern.py [options] [parameters] source_file [target_dir]")
```

### Options
`-h, --help`     Print help message

### Parameters
Format: `symbol=value`

#### Symbols
|  |  |
| --- | --- |
| `prefix` | Prefix added to the target name |
| `bps` | Beats per second (default=1.5) |
| `channel` | Midi channel (default=10) |
| `velocity` | MIDI note velocity factor (default=1.0) |
| `accent` | Factor for accented notes (default=1.5) |
| `mode` | 1 = autoplay, 2 = host & MIDI controlled, 3 = host controlled (default=1) |
| `on_key` | Option for MIDI controlled mode. 0 = Restart, 1 = restart and sync 2 = continue (default=0) | 
| `ab,bd,sn,...` | Re-assign instrument symbols to a new code or a new name |

## Resources
### https://github.com/lvm/tidal-drum-patterns
Thanks to LVM. This repository contains almost 500 patterns. Almost all are compatible to B.SEQuencer.

1. Clone or download https://github.com/lvm/tidal-drum-patterns
2. `python importpattern.py prefix=DR_LVM_ "path/to/tidal-drum-patterns/Sound/Tidal/Drum/*.hs" ~/.lv2`