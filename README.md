# Importpattern

Tool to import simple drum patterns in a format like:
```
bps = 1.5
bd = " [ t ~ ~ ~ ] [ ~ ~ ~ ~ ] [ t ~ t ~ ] [ t ~ ~ ~ ] "
sn = " [ ~ ~ ~ ~ ] [ t ~ ~ ~ ] [ ~ ~ ~ ~ ] [ t ~ ~ ~ ] "
```

from Tidal or similar to B.SEQuencer presets.

## Usage 
```
python importpattern.py [options] [parameters] source_file [target_dir]")
```

### Options
`-h, --help`     Print help message

### Parameters
Format: `symbol=value`

#### Symbols
`prefix`      Prefix added to the target name

`bps`         Beats per second (default=90)

`ab,bd,sn,...` Re-assign instrument symbols to a new code or a new name