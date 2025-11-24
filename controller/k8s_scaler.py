from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class K8sScaler:
    def __init__(self, namespace: str = "default"):
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.namespace = namespace

    def get_replicas(self, deployment_name: str) -> int:
        try:
            dep = self.apps_v1.read_namespaced_deployment(
                name=deployment_name, namespace=self.namespace
            )
            return dep.spec.replicas
        except ApiException as e:
            log.info(f"Error reading deployment '{deployment_name}': {e}")
            return -1

    def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        try:
            body = {"spec": {"replicas": replicas}}
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name, namespace=self.namespace, body=body
            )
            log.info(f"Deployment '{deployment_name}' scaled to {replicas} replicas")
            return True
        except ApiException as e:
            log.info(f"Error scaling deployment '{deployment_name}': {e}")
            return False

    def ensure_replicas(self, deployment_name: str, desired: int):
        current = self.get_replicas(deployment_name)
        if current == -1:
            return
        if current != desired:
            log.info(f"Current replicas: {current}, scaling to {desired}")
            self.scale_deployment(deployment_name, desired)
        else:
            log.info(f"Deployment '{deployment_name}' already at desired replicas: {desired}")


if __name__ == "__main__":
    scaler = K8sScaler(namespace="testing")
    deployment = "fastapi-simple-server"
    desired_replicas = 4

    scaler.ensure_replicas(deployment, desired_replicas)
