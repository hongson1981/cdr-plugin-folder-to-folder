# vpc
variable "project" {
  default = "cdr-plugin"
}

variable "vpc_id" {
  default = "vpc-dddb1aa4"
}

variable "vpc_cidr" {
  default = "172.31.0.0/16"
}

variable "cidr_block" {
  default = "0.0.0.0/0"
}

variable "public_subnets" {
  default = ["subnet-4192ee1b", "subnet-2ad9db62", "subnet-3d7c4e5b"]
}

# common
variable "common_tags" {
  default = {
    "Name": "cdr-gw-sdk",
    "Delete": "No",
    "Scope": "cdr-plugin-f2f",
    "Owner": "Dharam",
    "Team": "k8-proxy"
  } 
}

# glasswall cloud sdk
variable "sdk_image_id" {
  default = "ami-0f9ca86402ab7ce91"
}

variable "sdk_lb_sgs" {
  default = {
    i-http   = ["ingress", "8080", "TCP", ["0.0.0.0/0"]]
    e-default = ["egress", "0", "-1", ["0.0.0.0/0"]]
  }
}

variable "sdk_desired_capacity" {
  default = 2
}

variable "sdk_min_instances" {
  default = 2
}

variable "sdk_max_instances" {
  default = 4
}

variable "sdk_lb_port" {
  default = 8080
}

variable "sdk_target_port" {
  default = 8080
}

