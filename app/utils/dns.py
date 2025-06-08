import dns.resolver

def resolve_srv(domain):
    try:
        answers = dns.resolver.resolve(f"_minecraft._tcp.{domain}", 'SRV')
        for rdata in answers:
            return str(rdata.target).rstrip('.'), rdata.port
    except:
        return domain, None
