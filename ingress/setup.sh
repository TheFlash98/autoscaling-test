helm upgrade --install ingress-nginx ingress-nginx   --repo https://kubernetes.github.io/ingress-nginx   --namespace ingress-nginx --create-namespace


helm upgrade ingress-nginx ingress-nginx \
--repo https://kubernetes.github.io/ingress-nginx \
--namespace ingress-nginx \
--set controller.metrics.enabled=true \
--set-string controller.podAnnotations."prometheus\.io/scrape"="true" \
--set-string controller.podAnnotations."prometheus\.io/port"="10254"

kubectl apply --kustomize github.com/kubernetes/ingress-nginx/deploy/prometheus/

kubectl run -it --rm --image=mysql:latest -n testing --restart=Never mysql-client -- mysql -h mysql -pP@ssw0rd
kubectl port-forward prometheus-server-c5d6988c6-lvxwk 9090:9090 -n ingress-nginx
