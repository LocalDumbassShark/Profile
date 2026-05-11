import os
import json
from pathlib import Path

PROFILES_DIR = Path("profiles")
USER_DIR = Path("user")
TEMPLATE_FILE = Path("template.html")
INDEX_FILE = Path("index.html")

USER_DIR.mkdir(exist_ok=True)

template = TEMPLATE_FILE.read_text(encoding="utf-8")


def favicon_url(url: str) -> str:
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
    except Exception:
        return ""


def display_url(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").rstrip("/")


def build_profile(profile: dict) -> str:
    page = template

    accent_color = profile.get("color", "#5865f2")
    bg_color = profile.get("background_color", "#0f0f13")
    bg_image = profile.get("background_image", "")
    bg_image_css = f"url('{bg_image}')" if bg_image else "none"

    display_name = profile.get("display_name") or profile.get("discordName", "Unknown")
    discord_name = profile.get("discordName", "")

    page = page.replace("{{ACCENT_COLOR}}", accent_color)
    page = page.replace("{{BACKGROUND_COLOR}}", bg_color)
    page = page.replace("{{BACKGROUND_IMAGE}}", bg_image_css)
    page = page.replace("{{DISPLAY_NAME}}", display_name)
    page = page.replace("{{DISCORD_NAME}}", discord_name)

    # Avatar
    custom_avatar = profile.get("custom_avatar", "")
    if custom_avatar:
        avatar_html = f'<img class="avatar" src="{custom_avatar}" alt="avatar" onerror="this.style.display=\'none\'">'
    else:
        initials = display_name[:2].upper()
        avatar_html = f'<div class="avatar-placeholder">{initials}</div>'
    page = page.replace("{{AVATAR_HTML}}", avatar_html)

    # Bio
    bio = profile.get("bio", "")
    if bio:
        bio_html = f'<p class="bio">{bio}</p>'
    else:
        bio_html = ""
    page = page.replace("{{BIO_HTML}}", bio_html)

    # Fields
    fields_html = ""
    for field, label in [("age", "Age"), ("pronouns", "Pronouns")]:
        if field in profile:
            fields_html += f'''
            <div class="field">
              <div class="field-label">{label}</div>
              <div class="field-value">{profile[field]}</div>
            </div>'''
    if fields_html:
        fields_html = f'<div class="fields">{fields_html}</div>'
    page = page.replace("{{FIELDS_HTML}}", fields_html)

    # Links
    links = profile.get("links", [])
    if links:
        links_inner = ""
        for url in links:
            favicon = favicon_url(url)
            shown = display_url(url)
            links_inner += f'''
            <a class="link-item" href="{url}" target="_blank" rel="noopener noreferrer">
              <img class="link-favicon" src="{favicon}" alt="" onerror="this.style.display='none'">
              {shown}
            </a>'''
        links_html = f'<div class="links-title">Links</div><div class="links">{links_inner}</div>'
    else:
        links_html = ""
    page = page.replace("{{LINKS_HTML}}", links_html)

    return page


profiles_data = []

for json_file in PROFILES_DIR.glob("*.json"):
    try:
        profile = json.loads(json_file.read_text(encoding="utf-8"))
        user_id = json_file.stem

        html = build_profile(profile)
        out_path = USER_DIR / f"{user_id}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"Built profile for {user_id}")

        profiles_data.append({
            "id": user_id,
            "name": profile.get("display_name") or profile.get("discordName", "Unknown"),
        })
    except Exception as e:
        print(f"Error building {json_file.name}: {e}")

# Build index page
index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Profiles</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f13; color: #f2f2f2; padding: 3rem 1rem; }
    h1 { font-size: 28px; font-weight: 600; text-align: center; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; max-width: 800px; margin: 0 auto; }
    .card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1rem; text-align: center; text-decoration: none; color: #f2f2f2; transition: background 0.15s; }
    .card:hover { background: rgba(255,255,255,0.1); }
    .card-name { font-size: 15px; font-weight: 500; }
  </style>
</head>
<body>
  <h1>Profiles</h1>
  <div class="grid">
"""

for p in sorted(profiles_data, key=lambda x: x["name"].lower()):
    index_html += f'    <a class="card" href="user/{p["id"]}.html"><div class="card-name">{p["name"]}</div></a>\n'

index_html += """  </div>
</body>
</html>
"""

INDEX_FILE.write_text(index_html, encoding="utf-8")
