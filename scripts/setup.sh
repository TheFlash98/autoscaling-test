kubectl drain <node_name> --ignore-daemonsets --delete-emptydir-data
sudo systemctl stop kubelet
sudo rm /var/lib/kubelet/cpu_manager_state
sudo vi /etc/kubernetes/kubelet-config.yaml # EDIT CONFIG NOW
sudo systemctl daemon-reload
sudo systemctl start kubelet
kubectl uncordon <node_name>
cat /sys/fs/cgroup/cpuset.cpus
