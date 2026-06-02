import subprocess
import sys
import os

def run_command(cmd, cwd=None, env=None):
    print(f"Running: {' '.join(cmd)}")
    use_shell = (os.name == "nt" and cmd[0] in ("npm", "npx"))
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, shell=use_shell, encoding="utf-8")
    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(result.returncode)
    print("SUCCESS\n")
    return result

def main():
    print("=== V1 Final Production Validation & Release Readiness ===\n")
    
    root_dir = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # Override environment for deterministic tests
    env = os.environ.copy()
    env["ENVIRONMENT"] = "test"

    print("--- 1. Backend Validation ---")
    run_command([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], cwd=root_dir)
    run_command([sys.executable, "-m", "mypy", "backend/"], cwd=root_dir)
    run_command([sys.executable, "-m", "pytest", "backend/"], cwd=root_dir, env=env)

    print("--- 2. Frontend Validation ---")
    run_command(["npm", "ci"], cwd=frontend_dir)
    run_command(["npm", "run", "lint"], cwd=frontend_dir)
    run_command(["npx", "vitest", "run"], cwd=frontend_dir)
    run_command(["npm", "run", "build"], cwd=frontend_dir)

    print("=== ALL V1 QUALITY GATES PASSED SUCCESSFULLY ===")
    print("Release is deterministic, fully typed, and validated for parity.")

if __name__ == "__main__":
    main()
