resource "helm_release" "loki" {
  name       = "loki"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki-stack"
  namespace  = var.namespace
  create_namespace = false

  values = [file("${path.module}/loki_value.yaml")]

}

resource "helm_release" "tempo" {
  depends_on       = [helm_release.loki]
  name             = "tempo"
  repository       = "https://grafana.github.io/helm-charts"
  chart            = "tempo"
  namespace        = var.namespace
  create_namespace = false

  values           = [file("${path.module}/tempo.yaml")]
}