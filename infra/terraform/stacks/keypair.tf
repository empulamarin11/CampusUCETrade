# infra/terraform/stacks/keypair.tf

resource "aws_key_pair" "svc" {
  # LOGIC: 
  # Create this key ONLY IF:
  # 1. var.ssh_key_name is null (user didn't provide an existing key like "vockey")
  # 2. AND var.ssh_public_key_path is NOT empty
  count = var.ssh_key_name == null && var.ssh_public_key_path != "" ? 1 : 0

  key_name   = "${local.name}-svc-key"
  public_key = file(var.ssh_public_key_path)

  tags = merge(var.tags, { Name = "${local.name}-svc-key" })
}