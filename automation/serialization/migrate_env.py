import shutil
import sys
import os

def migrate(source_env, target_env):
    source_dir = f"../../dashboards/{source_env}"
    target_dir = f"../../dashboards/{target_env}"

    if not os.path.exists(source_dir):
        print(f"Error: Source dir {source_dir} doesn't exist.")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)

    # Copiamos todo de un entorno a otro
    # Aquí podríamos inyectar transformaciones (sed replacements) para IDs de BD
    for filename in os.listdir(source_dir):
        if filename.endswith(".yaml"):
            shutil.copy(os.path.join(source_dir, filename), os.path.join(target_dir, filename))
            print(f"Migrated: {filename} from {source_env} to {target_env}")

    print(f"\nMigración lista en carpeta {target_dir}. Commit a git y ejecuta import_metabase.py en el entorno destino.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python migrate_env.py [source] [target]")
        print("Example: python migrate_env.py dev staging")
        sys.exit(1)

    source = sys.argv[1]
    target = sys.argv[2]
    migrate(source, target)
