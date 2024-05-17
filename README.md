# Program Cloner

Download all Solana programs.

Adapted from https://github.com/riptl/solana-programs.

```shell
python -m venv ./env
source ./env/bin/activate
pip install -r requirements.txt
```

Download all programs:

```shell
python -m cloner clone
```

Sort downloaded programs by the last slot they were invoked:

```shell
python -m cloner sort
```

Profile deployment slots of all Loader V3 programs:

```shell
python -m cloner profile-slots
```