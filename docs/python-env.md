
``` bash
conda env list
```

``` bash
conda activate p-3.12.5-mt-igcl
conda activate p-3.10.14-mt-igcl
```

``` bash
poetry install --no-root

poetry add PACKAGE

# Add manually in file:
poetry lock

```


``` bash
poetry run python manage.py startapp accounts
poetry run python manage.py makemigrations accounts
poetry run python manage.py migrate
```