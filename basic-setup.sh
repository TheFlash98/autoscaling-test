# bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# caddy stuff
kubectl create namespace caddy-system
git clone https://github.com/caddyserver/ingress.git
cd ingress
# generate the yaml file
helm template mycaddy ./charts/caddy-ingress-controller \
  --namespace=caddy-system \
  > mycaddy.yaml
# apply the file
kubectl apply -f mycaddy.yaml -n caddy-system

# cert stuff
cd ..
mkdir mycerts
cd mycerts
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout mykey.pem \
  -out mycert.pem \
  -subj "/CN=test.com/O=test.com"
kubectl create namespace testing
kubectl create secret tls mycerts \
  --cert=mycert.pem \
  --key=mykey.pem \
  -n testing
cd ..

# sql + api stuff
git clone https://github.com/TheFlash98/autoscaling-test.git
cd autoscaling-test
kubectl apply -f mysql/mysql-pv.yaml -n testing
kubectl apply -f mysql/mysql-deployment.yaml -n testing
kubectl apply -f api/api-deployment.yaml -n testing

IP=$(kubectl get services --namespace caddy-system mycaddy-caddy-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "$IP test.com" | sudo tee -a /etc/hosts

kubectl create namespace monitoring
kubectl apply -f monitoring/prom-configmap.yaml -n monitoring
kubectl apply -f monitoring/prom-deploy.yaml -n monitoring
kubectl apply -f monitoring/prom-svc.yaml -n monitoring
kubectl apply -f monitoring/caddy-metrics.yaml -n caddy-system

