bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

helm upgrade --install ingress-nginx ingress-nginx   --repo https://kubernetes.github.io/ingress-nginx   --namespace ingress-nginx --create-namespace
helm upgrade ingress-nginx ingress-nginx \
--repo https://kubernetes.github.io/ingress-nginx \
--namespace ingress-nginx \
--set controller.metrics.enabled=true \
--set-string controller.podAnnotations."prometheus\.io/scrape"="true" \
--set-string controller.podAnnotations."prometheus\.io/port"="10254"
kubectl apply --kustomize github.com/kubernetes/ingress-nginx/deploy/prometheus/ -n ingress-nginx

kubectl create namespace caddy-system
helm install \
  --namespace=caddy-system \
  --repo https://caddyserver.github.io/ingress/ \
  --atomic \
  mycaddy \
  caddy-ingress-controller

helm upgrade \
  --namespace=caddy-system \
  --repo https://caddyserver.github.io/ingress/ \
  --atomic \
  --set ingressController.config.email=sarthak.k@nyu.edu \
  --set ingressController.config.onDemandTLS=true \
  mycaddy \
  caddy-ingress-controller

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout mykey.pem \
  -out mycert.pem \
  -subj "/CN=test.com/O=test.com"

kubectl create secret tls mycerts \
  --cert=mycert.pem \
  --key=mykey.pem \
  -n testing



git clone https://github.com/TheFlash98/autoscaling-test.git
cd autoscaling-test
kubectl create namespace testing
kubectl apply -f mysql/mysql-pv.yaml -n testing
kubectl apply -f mysql/mysql-deployment.yaml -n testing
kubectl apply -f api/api-deployment.yaml -n testing

kubectl drain <node_name> --ignore-daemonsets --delete-emptydir-data
sudo systemctl stop kubelet
sudo rm /var/lib/kubelet/cpu_manager_state
sudo vi /etc/kubernetes/kubelet-config.yaml # EDIT CONFIG NOW
sudo systemctl daemon-reload
sudo systemctl start kubelet
kubectl uncordon <node_name>
cat /sys/fs/cgroup/cpuset.cpus
