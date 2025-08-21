def creer_contenu_broker():
    brokers = [
        {"nom": "Exness", "commission": "$1850", "pays": "السعودية"},
        {"nom": "XM", "commission": "$650", "pays": "الإمارات"},
        {"nom": "IC Markets", "commission": "$800", "pays": "مصر"}
    ]
    
    contenu = f"""
    <!-- Généré le {datetime.datetime.now()} -->
    <h2>آخر التحديثات</h2>
    """
    
    for broker in brokers:
        contenu += f"""
        <div class="broker-card">
            <h3>{broker['nom']}</h3>
            <p>العمولة: {broker['commission']} لكل عميل من {broker['pays']}</p>
        </div>
        """
    
    with open("content/latest.html", "w", encoding="utf-8") as f:
        f.write(contenu)
    
    print("✅ Contenu généré avec succès!")

if __name__ == "__main__":
    creer_contenu_broker()