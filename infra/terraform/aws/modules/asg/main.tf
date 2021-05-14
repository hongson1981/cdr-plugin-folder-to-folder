resource "aws_launch_configuration" "default" {
  name_prefix     = var.project_name
  image_id        = var.image_id
  instance_type   = var.instance_type
  key_name        = var.key_name
  security_groups = [aws_security_group.default.id]

  lifecycle {
    create_before_destroy = true
  }

  root_block_device {
    volume_size = 30
    volume_type = "gp2"
  }

}

resource "aws_autoscaling_group" "default" {
  name                      = "${var.project_name}-asg"
  launch_configuration      = aws_launch_configuration.default.name
  min_size                  = var.min_instances
  max_size                  = var.max_instances
  health_check_grace_period = var.health_check_grace_period
  health_check_type         = "ELB"
  desired_capacity          = var.desired_capacity
  vpc_zone_identifier       = var.subnets
  target_group_arns         = var.target_group_arns

  lifecycle {
    create_before_destroy = true
  }

  warm_pool {
    max_group_prepared_capacity = 2
    min_size                    = 1
    pool_state                  = "Stopped"
  }

  dynamic "tag" {
    for_each = var.tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

}

resource "aws_security_group" "default" {
  vpc_id      = var.vpc_id
  name        = "${var.project_name}-sg"
  description = "Control the traffic to ec2 instances"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.tags, map("Name", "${var.project_name}-sg"))
}

resource "aws_security_group_rule" "rule" {
  count             = length(var.instance_port)
  protocol          = element(var.instance_port[element(keys(var.instance_port), count.index)], 2)
  from_port         = element(var.instance_port[element(keys(var.instance_port), count.index)], 1)
  to_port           = element(var.instance_port[element(keys(var.instance_port), count.index)], 1)
  type              = element(var.instance_port[element(keys(var.instance_port), count.index)], 0)
  cidr_blocks       = element(var.instance_port[element(keys(var.instance_port), count.index)], 3)
  security_group_id = aws_security_group.default.id
}

