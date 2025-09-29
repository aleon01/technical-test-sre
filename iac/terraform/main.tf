resource "kubernetes_namespace" "tec_test_ns" {
  metadata {
    name = "tec-test-ns"
  }
}

module "python-app" {
  source    = "./modules/app"
  depends_on = [kubernetes_namespace.tec_test_ns]

  namespace = kubernetes_namespace.tec_test_ns.metadata[0].name
}

module "prometheus" {
  source    = "./modules/monitoring/prometheus"
  depends_on = [kubernetes_namespace.tec_test_ns, module.python-app]
  
  namespace = kubernetes_namespace.tec_test_ns.metadata[0].name
}

module "grafana" {
  source    = "./modules/monitoring/grafana"
  depends_on = [kubernetes_namespace.tec_test_ns]
  
  namespace = kubernetes_namespace.tec_test_ns.metadata[0].name
}

module "otel_collector" {
  source = "./modules/monitoring/otel"
  depends_on = [kubernetes_namespace.tec_test_ns, module.grafana]
  
  namespace = kubernetes_namespace.tec_test_ns.metadata[0].name
}


resource "helm_release" "grafana_ui" {
  name             = "grafana"
  repository       = "https://grafana.github.io/helm-charts"
  chart            = "grafana"
  namespace        = kubernetes_namespace.tec_test_ns.metadata[0].name
  create_namespace = false

  values           = [file("${path.module}/grafana.yaml")]
  depends_on = [kubernetes_namespace.tec_test_ns, module.prometheus, module.grafana, module.otel_collector]
}
