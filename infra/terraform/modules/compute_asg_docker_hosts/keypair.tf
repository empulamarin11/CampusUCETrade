resource "aws_key_pair" "this" {
  key_name   = "${var.name}-key"
  public_key = file(var.ssh_public_key_path)

  tags = merge(var.tags, { Name = "${var.name}-key" })
}
