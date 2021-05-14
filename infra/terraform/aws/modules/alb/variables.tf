variable "project_name" {
  type = string
  default = "cdr-test"
}

variable "subnets" {
  type = list(any)
}

variable "vpc_id" {
  type = string
}

variable "instance_port" {
  default = {
    i-https   = ["ingress", "443", "TCP", ["0.0.0.0/0"]]
    i-http    = ["ingress", "80", "TCP", ["0.0.0.0/0"]]
    e-default = ["egress", "0", "-1", ["0.0.0.0/0"]]
  }
}

variable "target_port" {
  default = 80
}

variable "target_protocol" {
  default = "HTTP"
}

variable "lb_port" {
  default = [80]
}

variable "lb_protocol" {
  default = ["HTTP"]
}

variable "health_check_path" {
  default = "/"
}

variable "tags" {
  type = map(string)
}

variable "certificate_arn" {
  default = ""
}
