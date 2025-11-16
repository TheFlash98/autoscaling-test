import time
from k8s_scaler import K8sScaler
from query_prom import PrometheusClient
from pid_controller import PIDController
import os

def autoscale_loop(deployment_name, pod_pattern, namespace="default"):
    Kp = float(os.getenv("PID_KP", 0.5))
    Ki = float(os.getenv("PID_KI", 0.05))
    Kd = float(os.getenv("PID_KD", 0.1))
    setpoint = float(os.getenv("PID_SETPOINT", 0.01))
    factor = float(os.getenv("SCALING_FACTOR", 20))  # scaling factor

    pid = PIDController(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=setpoint)
    prom = PrometheusClient()
    k8s_scaler = K8sScaler(namespace=namespace)
    min_replicas = 1
    max_replicas = 100

    current_replicas = k8s_scaler.get_replicas(deployment_name)
    print(f"Starting autoscaler for deployment '{deployment_name}' with {current_replicas} replicas")
    last_latency = None
    last_scaled = False  # track if we just scaled

    while True:
        p99_latency = prom.p99_latency("/heroes/{hero_id}", job="fastapi-pods", window="5m")
        if p99_latency is None:
            time.sleep(30)
            continue

        print(f"Current p99 latency: {p99_latency:.3f}s")

        # Check if last scale reduced latency
        if last_scaled and last_latency is not None:
            if p99_latency >= last_latency:
                print(f"Latency did not improve after last scale ({last_latency:.3f}s -> {p99_latency:.3f}s), waiting...")
                time.sleep(15)
                continue  # skip scaling until latency improves

        # Compute control signal
        control = pid.compute(p99_latency)
        adjustment = control * factor
        print(f"p99 latency={p99_latency:.3f}s, control={control:.4f}, adjustment={adjustment:.2f}")

        new_replicas = current_replicas + adjustment
        if abs(adjustment) > 2:  # only scale for significant changes
            new_replicas = max(min_replicas, min(max_replicas, round(new_replicas)))
            print(f"Adjusting replicas from {current_replicas} to {new_replicas}")
            if new_replicas != current_replicas:
                k8s_scaler.scale_deployment(deployment_name, new_replicas)
                last_scaled = True
                last_latency = p99_latency
                current_replicas = new_replicas
            else:
                last_scaled = False
        else:
            last_scaled = False

        time.sleep(30)



    

if __name__ == "__main__":
    autoscale_loop("fastapi-simple-server", "fastapi-simple-server-.*", namespace="testing")