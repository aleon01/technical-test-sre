resource "helm_release" "otel_collector" {
  name             = "otel-collector"
  repository       = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart            = "opentelemetry-collector"
  namespace        = var.namespace
  create_namespace = false
  
  values           = [file("${path.module}/otel-collector.yaml")]
}
