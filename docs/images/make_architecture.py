"""Generates docs/images/architecture.svg (CloudCost Watch target architecture).

Run:  python docs/images/make_architecture.py
Edit the coordinates below and re-run; the SVG is plain and diff-friendly.
"""

from pathlib import Path

W, H = 1560, 1010
INK = "#232F3E"
MUTED = "#5F6B7A"

# AWS architecture icon category colors
NET = "#8C4FFF"
SEC = "#DD344C"
CMP = "#ED7100"
DB = "#C925D1"
MGMT = "#E7157B"
FIN = "#7AA116"
K8S = "#326CE5"

out: list[str] = []


def add(s: str) -> None:
    out.append(s)


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def group(x, y, w, h, label, stroke, fill="none", dash=None, label_fill=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{d}/>')
    lf = label_fill or stroke
    add(f'<rect x="{x}" y="{y}" width="{len(label) * 7.4 + 22}" height="24" rx="6" fill="{lf}"/>')
    add(f'<text x="{x + 11}" y="{y + 16.5}" class="glabel">{esc(label)}</text>')


def tile(cx, cy, color, glyph, label, sub=None, size=52, round_=False):
    h = size / 2
    if round_:
        add(f'<circle cx="{cx}" cy="{cy}" r="{h}" fill="{color}"/>')
    else:
        add(f'<rect x="{cx - h}" y="{cy - h}" width="{size}" height="{size}" rx="10" fill="{color}"/>')
    fs = 15 if len(glyph) <= 4 else 12
    add(f'<text x="{cx}" y="{cy + fs * 0.35}" class="glyph" font-size="{fs}">{esc(glyph)}</text>')
    add(f'<text x="{cx}" y="{cy + h + 17}" class="tlabel">{esc(label)}</text>')
    if sub:
        add(f'<text x="{cx}" y="{cy + h + 32}" class="tsub">{esc(sub)}</text>')


def pill(x, y, w, label, color):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="#fff" stroke="{color}" stroke-width="1.4"/>')
    add(f'<circle cx="{x + 16}" cy="{y + 14}" r="5" fill="{color}"/>')
    add(f'<text x="{x + 28}" y="{y + 18.5}" class="pill">{esc(label)}</text>')


def path(d, color=INK, dashed=False, arrow=True, width=1.8):
    da = ' stroke-dasharray="6 5"' if dashed else ""
    m = f' marker-end="url(#a-{color.strip("#")})"' if arrow else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}{m}/>')


def tag(x, y, text, color=INK):
    w = len(text) * 6.3 + 14
    add(f'<rect x="{x - w / 2}" y="{y - 11}" width="{w}" height="20" rx="10" fill="#fff" stroke="{color}" stroke-width="1"/>')
    add(f'<text x="{x}" y="{y + 3.5}" class="tag" fill="{color}">{esc(text)}</text>')


def step(x, y, n, color):
    add(f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>')
    add(f'<text x="{x}" y="{y + 4.5}" class="step">{n}</text>')


REQ = "#0972D3"   # request path
DATA = "#E07941"  # data / AWS API calls
OPS = "#3F8624"   # delivery

# ---------------------------------------------------------------- header
add(f'<rect width="{W}" height="{H}" rx="18" fill="#FFFFFF"/>')
add(f'<text x="40" y="48" class="title">CloudCost Watch</text>')
add(f'<text x="40" y="72" class="subtitle">Target architecture · FinOps platform on Amazon EKS · ap-southeast-1</text>')

# ---------------------------------------------------------------- groups
group(200, 92, 1220, 838, "AWS Cloud", INK)
group(220, 132, 1040, 778, "Region ap-southeast-1", "#00A4A6", dash="7 5")
group(1272, 300, 136, 172, "Global", MUTED, dash="7 5")
group(240, 272, 830, 578, "VPC 10.20.0.0/16 · 2 AZs", NET, fill="#FBF9FF")
group(258, 312, 174, 520, "Public subnets", FIN, fill="#F3F8EA")
group(450, 312, 440, 520, "Private subnets", "#147EBA", fill="#EEF6FC")
group(470, 340, 400, 464, "Amazon EKS cluster", CMP, fill="#FFFFFF")
group(908, 312, 146, 290, "Database subnets", DB, fill="#FBF1FC")

# ---------------------------------------------------------------- arrows (drawn under tiles)
# request path
path("M126,200 H262", REQ)
path("M316,200 H382", REQ)
path("M410,266 V430 H374", REQ)
path("M372,422 H512", REQ)
path("M374,436 Q440,436 440,410 V392 Q440,384 452,384 H700 V392", REQ)
path("M728,420 H952", REQ)
# jobs -> database (read / write)
for x in (540, 660, 780):
    path(f"M{x},526 V512", DATA, arrow=False)
path("M540,512 H890 V428 H952", DATA)
# jobs -> AWS APIs trunk
for x in (540, 660, 780):
    path(f"M{x},606 V618", DATA, arrow=False)
path("M540,618 H1096", DATA, arrow=False)
path("M1096,300 V646", DATA, arrow=False)
path("M1096,312 H1130", DATA)
path("M1096,422 H1130", DATA)
path("M1096,532 H1130", DATA)
path("M1096,646 H1224 Q1236,646 1236,634 V410 Q1236,398 1248,398 H1310", DATA)
path("M1096,492 Q1110,492 1150,492 H1420 Q1430,492 1430,482 V458", DATA, dashed=True)
# delivery
path("M126,790 H170 V880 H1160 V812", OPS)
path("M580,880 V776", OPS, dashed=True)
path("M1130,740 H874", CMP, dashed=True)

# ---------------------------------------------------------------- outside
tile(100, 200, "#545B64", "user", "Users", "browser", round_=True)
tile(100, 790, "#24292F", "GitHub", "GitHub", "repo + Actions")
tile(1460, 432, "#4A154B", "Slack", "Slack", "optional")

# edge services (regional / global, outside the VPC)
tile(290, 200, NET, "R53", "Route 53", "cost.vuongdomain.click")
tile(410, 200, SEC, "WAF", "AWS WAF", "managed rules")
tile(540, 200, SEC, "ACM", "ACM", "TLS certificate")
tile(660, 200, SEC, "IdP", "Cognito", "sign-in on ALB")

# public subnet
tile(345, 430, NET, "ALB", "Application LB", "HTTPS · Cognito auth")
tile(345, 700, NET, "NAT", "NAT gateway", "egress to AWS APIs")

# EKS workloads
tile(540, 420, K8S, "web", "frontend", "nginx · React")
tile(700, 420, K8S, "api", "api", "FastAPI · HPA 2–6")
tile(540, 552, K8S, "job", "ingest", "CronJob · daily")
tile(660, 552, K8S, "job", "scan", "CronJob · daily")
tile(780, 552, K8S, "job", "notify", "CronJob · hourly")
add('<text x="490" y="660" class="section">Platform add-ons (Helm)</text>')
pill(490, 674, 176, "LB Controller", CMP)
pill(676, 674, 176, "External Secrets", SEC)
pill(490, 714, 176, "Argo CD (GitOps)", OPS)
pill(676, 714, 176, "Prometheus · Grafana", MGMT)
pill(490, 754, 176, "metrics-server", K8S)
pill(676, 754, 176, "Pod Identity agent", K8S)

# database
tile(980, 420, DB, "RDS", "PostgreSQL 17", "Multi-AZ in prod")
add('<text x="981" y="500" class="tsub">encrypted · PITR</text>')
add('<text x="981" y="515" class="tsub">no internet route</text>')

# regional services
tile(1160, 312, SEC, "SM", "Secrets Manager", "DB creds · webhook")
tile(1160, 422, MGMT, "SES", "Amazon SES", "email alerts")
tile(1160, 532, MGMT, "CW", "EC2 · ELB · CW", "scanned (read-only)")
tile(1160, 740, CMP, "ECR", "Amazon ECR", "immutable SHA tags")
tile(1340, 398, FIN, "CE", "Cost Explorer", "API (us-east-1)")

# ---------------------------------------------------------------- labels on arrows
tag(194, 200, "HTTPS", REQ)
tag(470, 422, "/", REQ)
tag(600, 384, "/api", REQ)
tag(840, 420, "SQL · TLS", REQ)
tag(820, 512, "upsert", DATA)
tag(960, 618, "AWS API calls · Pod Identity · via NAT", DATA)
tag(1290, 492, "Slack webhook", DATA)
tag(1000, 740, "pull images", CMP)
tag(380, 880, "git push → CI → OIDC → push image", OPS)
tag(690, 862, "Argo CD syncs manifests", OPS)

step(150, 182, "1", REQ)
step(426, 300, "2", REQ)
step(470, 400, "3", REQ)
step(800, 400, "4", REQ)
step(600, 500, "A", DATA)
step(1096, 666, "B", DATA)
step(230, 862, "C", OPS)

# ---------------------------------------------------------------- legend
ly = 966
add(f'<text x="40" y="{ly}" class="legend-h">Flows</text>')
legend = [
    (REQ, False, "1–4  Request: browser → Route 53 → WAF → ALB (TLS + Cognito) → pods → PostgreSQL"),
    (DATA, False, "A–B  Data jobs: import costs, scan for waste, send alerts"),
    (OPS, False, "C  Delivery: GitHub Actions → ECR, Argo CD deploys from git"),
]
x = 100
for color, dashed, text in legend:
    da = ' stroke-dasharray="6 5"' if dashed else ""
    add(f'<path d="M{x},{ly - 4} H{x + 34}" stroke="{color}" stroke-width="2.4"{da} marker-end="url(#a-{color.strip("#")})"/>')
    add(f'<text x="{x + 44}" y="{ly}" class="legend">{esc(text)}</text>')
    x += 44 + len(text) * 6.55 + 40

# ---------------------------------------------------------------- assemble
colors = {REQ, DATA, OPS, CMP, INK}
markers = "".join(
    f'<marker id="a-{c.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for c in sorted(colors)
)
style = f"""
text {{ font-family: 'Amazon Ember', 'Segoe UI', Helvetica, Arial, sans-serif; }}
.title {{ font-size: 26px; font-weight: 700; fill: {INK}; }}
.subtitle {{ font-size: 14px; fill: {MUTED}; }}
.glabel {{ font-size: 12px; font-weight: 700; fill: #fff; }}
.glyph {{ font-weight: 700; fill: #fff; text-anchor: middle; }}
.tlabel {{ font-size: 13px; font-weight: 600; fill: {INK}; text-anchor: middle; }}
.tsub {{ font-size: 11px; fill: {MUTED}; text-anchor: middle; }}
.pill {{ font-size: 12px; fill: {INK}; }}
.section {{ font-size: 11px; font-weight: 700; fill: {MUTED}; letter-spacing: .5px; text-transform: uppercase; }}
.tag {{ font-size: 11px; font-weight: 600; text-anchor: middle; }}
.step {{ font-size: 12px; font-weight: 700; fill: #fff; text-anchor: middle; }}
.legend-h {{ font-size: 12px; font-weight: 700; fill: {INK}; }}
.legend {{ font-size: 12px; fill: {INK}; }}
"""
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'role="img" aria-label="CloudCost Watch target architecture on AWS">\n'
    f"<title>CloudCost Watch target architecture</title>\n"
    f"<defs><style>{style}</style>{markers}</defs>\n" + "\n".join(out) + "\n</svg>\n"
)
target = Path(__file__).with_name("architecture.svg")
target.write_text(svg, encoding="utf-8", newline="\n")
print(f"wrote {target}")
