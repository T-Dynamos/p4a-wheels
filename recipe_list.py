import importlib
import inspect
from pathlib import Path
import pythonforandroid
from pythonforandroid.recipe import (
    Recipe,
    PyProjectRecipe,
    MesonRecipe,
    RustCompiledComponentsRecipe,
)

P4A_PATH = Path(pythonforandroid.__file__).resolve().parent
RECIPES_DIR = P4A_PATH / "recipes"

BASES = (PyProjectRecipe, MesonRecipe, RustCompiledComponentsRecipe)

BLACKLIST = {"libcairo", "scipy", "pydantic-core"}  # add more if needed


def find_recipes():
    for recipe_dir in RECIPES_DIR.iterdir():
        if recipe_dir.is_dir() and (recipe_dir / "__init__.py").exists():
            yield recipe_dir.name


def load_recipe(recipe_name):
    try:
        module = importlib.import_module(f"pythonforandroid.recipes.{recipe_name}")
    except ModuleNotFoundError as e:
        return None
    except Exception as e:
        return None

    try:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Recipe) and obj is not Recipe:
                return obj
    except Exception as e:
        print(f"[WARN] {recipe_name}: inspection failed ({e})")
    return None


def main():
    print(f"Scanning recipes from: {RECIPES_DIR}\n")
    matches = []
    skipped = []

    for name in sorted(find_recipes()):
        if name in BLACKLIST:
            skipped.append(name)
            continue

        cls = load_recipe(name)
        if not cls:
            skipped.append(name)
            continue

        base = next((b.__name__ for b in BASES if issubclass(cls, b)), None)
        if base:
            matches.append((name, cls.__name__, base))

    print(f"Matching recipes ({len(matches)}):\n")

    names = []

    for name, cls_name, base in sorted(matches):
        print(f"- {name} → {cls_name}")
        names.append(name)

    # yes bad code
    r = f'RECIPES="{ " ".join(names).strip() }"\n'
    with open("run.sh") as f: lines = [l for l in f if not l.strip().startswith("RECIPES=")]
    with open("run.sh","w") as f: f.writelines([r]+lines)

if __name__ == "__main__":
    main()
