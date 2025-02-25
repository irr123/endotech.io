# endotech.io

## How to setup it locally

1. `git clone https://github.com/irr123/endotech.io.git`
1. `cd endotech.io`
1. `python3 -m venv ./venv`
1. `source ./venv/bin/python`
1. `pip install -r requirements.txt`

## How to execute

```bash
OPENAI_KEY=<token> ./main.py matcher /mnt/c/Users/ivan/Downloads/OriginalToWatched.xlsx --limit 0
```

`result.csv` will be located in same folder.
