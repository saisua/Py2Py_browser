import hashlib


def hash_req_res(url, domain, method, headers=None) -> str:
    full_url = f"{method}:{url}"

    url_prefix = hashlib.md5(full_url.encode()).hexdigest()
    domain_hash = hashlib.md5(domain.encode()).hexdigest()

    return url_prefix, domain_hash
