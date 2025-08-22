from datetime import datetime
import os

def creer_contenu_mis_a_jour():
    brokers = [
        {"nom": "Exness", "commission": "$1850", "url": "https://www.exness.com/ar/a/VOTRE_ID_ICI"},
        {"nom": "XM", "commission": "$650", "url": "https://clicks.pipaffiliates.com/c?c=VOTRE_ID_ICI"},
        {"nom": "IC Markets", "commission": "$800", "url": "https://icmarkets.com/?camp=VOTRE_ID_ICI"},
    ]

    html_snippet = f"<!-- Généré le {datetime.now()} -->\n"
    for b in brokers:
        html_snippet += f"""
        <div class="broker-card">
            <h2>{b['nom']}</h2>
            <p>العمولة: <span class="commission">حتى {b['commission']} لكل عميل</span></p>
            <a class="btn-primary" href="{b['url']}" target="_blank">سجّل الآن</a>
        </div>
        """
    with open("content/latest.html", "w", encoding="utf-8") as f:
        f.write(html_snippet)

if __name__ == "__main__":
    os.makedirs("content", exist_ok=True)
    creer_contenu_mis_a_jour()
    print("✅ Contenu généré.")
