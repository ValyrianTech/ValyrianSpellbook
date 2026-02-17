import socket

domains = [
    "selfielink.com",
    "selfiefuse.com",
    "duosnap.com",
    "snaptogether.com",
    "picpair.com",
    "dualselfie.com",
    "twinshot.com",
    "echoselfie.com",
    "selfiebridge.com",
    "fanfusion.com",
    "snapwithme.com",
    "starselfie.com",
    "genselfie.com",
    "snapsynth.com",
    "creatorcam.com"
]

def check_domain(domain):
    try:
        socket.gethostbyname(domain)
        return False  # resolves → domain taken or in use
    except socket.gaierror:
        return True  # no DNS → probably available

for d in domains:
    available = check_domain(d)
    if available:
        print(f"[AVAILABLE] {d}")
    else:
        print(f"[TAKEN]     {d}")
