resource "kubernetes_deployment" "tec-test-deployment" {
  metadata {
    name      = "tec-test-deployment"
    namespace = var.namespace
    labels = {
      app = "tec-test-python"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "tec-test-python"
      }
    }

    template {
      metadata {
        labels = {
          app = "tec-test-python"
        }
      }

      spec {
        container {
          name  = "tec-test-deployment"
          image = "technical-test:1.0.10" 
          image_pull_policy = "IfNotPresent"

          port {
            container_port = 8080
          }
        }
      }
    }
  }
}
 
resource "kubernetes_service" "tec-test-service" {
  metadata {
    name      = "tec-test-service"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "tec-test-python"
    }
    
    port {
      port        = 80
      target_port = 8080
      node_port   = 30080
    }

    type = "NodePort"
  }
}
