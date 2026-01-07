output "instance_id" { value = aws_instance.api_gw.id }
output "public_ip"   { value = aws_eip.api_gw.public_ip }
output "sg_id"       { value = aws_security_group.api_gw.id }
output "key_name"    { value = aws_key_pair.api_gw.key_name }
