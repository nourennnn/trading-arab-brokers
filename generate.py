#!/usr/bin/env python3
# generate.py
import os, datetime, re, textwrap, hashlib, openai, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

openai.api_key = os.environ["OPENAI_API_KEY"]

TODAY     = datetime.date.today()
POST_DIR  = Path("posts")
POST_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------
# 1. Demander un sujet + titre en arabe
# ------------------------------------------------------------------
prompt_topic = (
    "أنت خبير تسويق بالعمولة في مجال التداول. "
    "أعطني فكرة مقال جديد مثير باللغة العربية يشرح كيفية الربح من برنامج شراكة وسيط معين (Exness أو XM أو IC Markets). "
    "يجب أن يكون العنوان جذاباً ويحتوي على رقم أو وعد بربح واضح. "
    "أجب بصيغة JSON مضغوطة: {\"title\":\"...\"}"
)
resp = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user", "content": prompt_topic}],
    temperature=0.8
)
title_ar = json.loads(resp.choices[0].message.content)["title"]
safe_slug = re.sub(r"[^\w\u0600-\u06FF]+", "-", title_ar).strip("-")
fname = f"{TODAY.isoformat()}-{safe_slug}.html"
out_path = POST_DIR / fname

# ------------------------------------------------------------------
# 2. Rédiger l’article complet en arabe
# ------------------------------------------------------------------
prompt_article = f"""
أنت خبير تسويق بالعمولة في مجال الفوركس.
اكتب مقالاً طويلاً باللغة العربية الفصحى يتكون من 800-1500 كلمة عن:
"{title_ar}"

المتطلبات:
- مقدمة مشوقة
- عناوين فرعية واضحة
- تضمين روابط الإحالة التالية داخل النص بشكل طبيعي:
  - Exness: https://www.exness.com/a/12345
  - XM: https://clicks.pipaffiliates.com/c?c=67890
  - IC Markets: https://icmarkets.com/?camp=54321
- استخدام تقنيات SEO (كلمات مفتاحية: الربح من الفوركس، برنامج شراكة Exness، أفضل وسيط تداول)
- خاتمة تحفيزية
- لا تستخدم أي CSS أو HTML داخل المقال، فقط Markdown أو نص عادي.
"""
resp2 = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user", "content": prompt_article}],
    temperature=0.7,
    max_tokens=2200
)
body_md = resp2.choices[0].message.content.strip()

# ------------------------------------------------------------------
# 3. Convertir en HTML simple RTL
# ------------------------------------------------------------------
env = Environment(loader=FileSystemLoader("."), autoescape=True)
tpl = env.from_string("""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <meta name="description" content="{{ description }}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body{font-family:'Cairo',sans-serif;background:#f8f9fa}
    .content{white-space:pre-line;line-height:1.9}
  </style>
</head>
<body>
<div class="container py-5">
  <h1 class="mb-4">{{ title }}</h1>
  <p class="text-muted">{{ date }}</p>
  <div class="content">{{ body }}</div>
  <hr>
  <a href="/">← العودة إلى الصفحة الرئيسية</a>
</div>
</body>
</html>""")

html = tpl.render(
    title=title_ar,
    description="مقال شامل حول الربح من التداول وبرامج الشراكة.",
    date=TODAY.strftime("%d/%m/%Y"),
    body=body_md
)
out_path.write_text(html, encoding="utf-8")

# ------------------------------------------------------------------
# 4. Mettre à jour index.html (liste des articles)
# ------------------------------------------------------------------
index_tpl = env.from_string("""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>مدونة التداول بالعمولة</title>
  <meta name="description" content="مقالات يومية حول الربح من برامج الشراكة في الفوركس">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>body{font-family:'Cairo',sans-serif;background:#f8f9fa}</style>
</head>
<body>
<div class="container py-5">
  <h1 class="mb-4">آخر المقالات</h1>
  <ul class="list-group">
    {% for art in articles %}
      <li class="list-group-item">
        <a href="posts/{{ art.file }}" class="text-decoration-none fw-bold">{{ art.title }}</a>
        <br><small class="text-muted">{{ art.date }}</small>
      </li>
    {% endfor %}
  </ul>
</div>
</body>
</html>""")
existing = sorted(POST_DIR.glob("*.html"), key=lambda p: p.name, reverse=True)
articles = []
for p in existing:
    m = re.match(r"(\d{4}-\d{2}-\d{2})", p.name)
    if m:
        date_obj = datetime.datetime.strptime(m.group(1), "%Y-%m-%d").date()
        title_in_file = re.search(r"<title>(.*?)</title>", p.read_text(encoding="utf-8")).group(1)
        articles.append({
            "file": p.name,
            "title": title_in_file,
            "date": date_obj.strftime("%d/%m/%Y")
        })
Path("index.html").write_text(index_tpl.render(articles=articles), encoding="utf-8")
print("✅ Article généré :", out_path.name)
