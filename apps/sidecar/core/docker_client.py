import subprocess
import sys
import os
import threading
from apps.sidecar.core.logger import get_logger

# Try importing docker SDK
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

logger = get_logger("sidecar.docker")

class MockDockerClient:
    def __init__(self):
        self.is_mock = True

    def run_container(self, image: str, command: str, env: dict = None):
        """
        Simulates running a container by executing the local python script.
        """
        logger.info(f"Starting MOCK container from image: {image}")
        
        # For MVP simulation, we map the 'image' concept to our local script paths
        if "contex-brain" in image and "daily-brief" in command:
            script_path = "packages/skills/daily-brief/main.py"
            logger.info(f"Simulating execution of {script_path}")
            
            # Run in a separate thread/process to not block API
            def _run():
                try:
                    run_env = os.environ.copy()
                    # Ensure packages is in PYTHONPATH for Mock execution
                    cwd = os.getcwd()
                    run_env["PYTHONPATH"] = f"{cwd}:{cwd}/packages:" + run_env.get("PYTHONPATH", "")
                    
                    if env:
                        run_env.update(env)
                    
                    # If env is provided, it should take precedence over system env
                    # We already updated run_env with env above, so we don't need to do anything else
                    # unless we want to force system env (which we don't for API keys)
                    pass
                    
                    # Use Popen to capture stdout/stderr in real-time
                    process = subprocess.Popen(
                        [sys.executable, script_path],
                        env=run_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1
                    )

                    # Helper to read stream
                    def log_stream(stream, level_method):
                        for line in iter(stream.readline, ''):
                            if line:
                                level_method(f"[CONTAINER] {line.strip()}")
                        stream.close()

                    # Create threads to read stdout/stderr concurrently
                    t_out = threading.Thread(target=log_stream, args=(process.stdout, logger.info))
                    t_err = threading.Thread(target=log_stream, args=(process.stderr, logger.error))
                    
                    t_out.start()
                    t_err.start()
                    
                    process.wait()
                    t_out.join()
                    t_err.join()

                    if process.returncode == 0:
                        logger.info("Container finished successfully")
                    else:
                        logger.error(f"Container failed with exit code {process.returncode}")

                except Exception as e:
                    logger.error(f"Container execution failed: {e}")

            threading.Thread(target=_run).start()
            return "mock-container-id-123"
        
        return None

class RealDockerClient:
    def __init__(self):
        self.is_mock = False
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Successfully connected to Docker Daemon.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker Daemon: {e}")
            raise

    def run_container(self, image: str, command: str, env: dict = None):
        """
        Runs a real Docker container.
        """
        logger.info(f"Starting REAL container from image: {image}")
        
        try:
            # Determine networking mode
            # For Linux, use "host" mode to access localhost.
            # For Mac/Windows, use "host.docker.internal".
            extra_hosts = {}
            if sys.platform != "linux":
                extra_hosts = {"host.docker.internal": "host-gateway"}
            
            # Mount skills directory for hot-reloading/access
            # Assuming we are running from project root
            cwd = os.getcwd()
            volumes = {
                f"{cwd}/packages/skills": {'bind': '/app/skills', 'mode': 'ro'}
            }

            # Prepare Environment
            container_env = env if env else {}
            if "GOOGLE_API_KEY" in os.environ:
                container_env["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
            
            # Replace localhost with host.docker.internal for Mac/Win if needed
            if sys.platform != "linux" and "SIDECAR_URL" in container_env:
                container_env["SIDECAR_URL"] = container_env["SIDECAR_URL"].replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")

            # Run container detached
            container = self.client.containers.run(
                image,
                command=f"python3 /app/skills/{command}/main.py", # Assuming command maps to directory
                environment=container_env,
                volumes=volumes,
                extra_hosts=extra_hosts,
                detach=True,
                auto_remove=True 
            )
            
            # Spawn a thread to follow logs
            def _follow_logs():
                try:
                    for line in container.logs(stream=True, follow=True):
                        logger.info(f"[CONTAINER] {line.decode('utf-8').strip()}")
                except Exception as e:
                    # Container might have stopped
                    pass
            
            threading.Thread(target=_follow_logs).start()
            
            return container.id

        except Exception as e:
            logger.error(f"Failed to run real container: {e}")
            raise e

# Factory to choose client
def get_docker_client():
    use_mock = os.getenv("USE_MOCK_DOCKER", "true").lower() == "true"
    
    if not use_mock and DOCKER_AVAILABLE:
        try:
            return RealDockerClient()
        except:
            logger.warning("Failed to initialize RealDockerClient. Falling back to Mock.")
            return MockDockerClient()
    else:
        if not use_mock:
            logger.warning("Docker SDK not installed. Falling back to Mock.")
        return MockDockerClient()

# Singleton instance
docker_client = get_docker_client()
