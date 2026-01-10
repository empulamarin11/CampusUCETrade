resource "aws_key_pair" "svc" {
  key_name   = "${local.name}-svc-key"
  public_key = file(var.ssh_public_key_path)

  tags = merge(var.tags, { Name = "${local.name}-svc-key" })
}
