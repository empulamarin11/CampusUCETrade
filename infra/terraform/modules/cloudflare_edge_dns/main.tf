resource "cloudflare_record" "this" {
  zone_id = var.zone_id
  name    = var.subdomain
  type    = "CNAME"
  content = var.target
  proxied = var.proxied
  ttl     = var.ttl
}
