from utils.hash_str import _hash_str


def hash_req_res(url, domain, method, headers=None) -> str:
    full_url = f"{method}:{url}"

    url_prefix = _hash_str(full_url)
    domain_hash = _hash_str(domain)

    return url_prefix, domain_hash
