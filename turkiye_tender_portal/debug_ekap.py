"""
EKAP sayfa yapısını keşfetmek için debug script.
Sayfayı açar, bekler, HTML yapısını analiz eder.
"""
import time, sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"

from playwright.sync_api import sync_playwright

EKAP_URL = "https://ekapv2.kik.gov.tr/ekap/search"

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="tr-TR",
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    page = context.new_page()
    page.on("dialog", lambda d: d.dismiss())

    print("[1] Sayfa aciliyor...")
    page.goto(EKAP_URL, wait_until="domcontentloaded", timeout=60000)
    
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except:
        pass
    
    print("[2] 5 saniye bekleniyor (SPA yuklensin)...")
    time.sleep(5)

    # Sayfadaki tum butonlari listele
    print("\n--- BUTONLAR ---")
    buttons = page.locator("button")
    for i in range(min(buttons.count(), 20)):
        try:
            btn = buttons.nth(i)
            txt = btn.inner_text(timeout=1000).strip().replace("\n", " ")
            vis = btn.is_visible(timeout=500)
            print(f"  [{i}] text='{txt[:60]}' visible={vis}")
        except:
            pass

    # Arama / Ara butonunu bul ve tikla
    print("\n--- ARA BUTONU ARANACAK ---")
    ara_clicked = False
    
    # Angular/SPA icin farkli selector'lar dene
    ara_selectors = [
        "button:has-text('Ara')",
        "button:has-text('ARA')",
        "button:has-text('Arama Yap')",
        "a:has-text('Ara')",
        "span:has-text('Ara')",
        "button[type='submit']",
        "button.btn-search",
        "button.arama-btn",
        "#ara",
        "#search",
        "#btnAra",
        "#btnSearch",
    ]
    for sel in ara_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=500):
                print(f"  BULUNDU: {sel} -> '{el.inner_text(timeout=500).strip()[:40]}'")
                el.click(timeout=3000)
                ara_clicked = True
                print(f"  TIKLANDI!")
                break
        except:
            pass
    
    if not ara_clicked:
        print("  Ara butonu bulunamadi, Enter ile deneyelim...")
        try:
            page.keyboard.press("Enter")
            print("  Enter basildi")
        except:
            pass

    print("[3] Sonuclarin yuklenmesi bekleniyor (8 sn)...")
    time.sleep(8)

    # Sonuc tablosu / listesi icin detayli analiz
    print("\n--- TABLE ELEMANLARI ---")
    tables = page.locator("table")
    print(f"  Toplam table: {tables.count()}")
    for i in range(tables.count()):
        try:
            t = tables.nth(i)
            cls = t.get_attribute("class", timeout=500) or ""
            rows = t.locator("tr").count()
            print(f"  table[{i}] class='{cls}' rows={rows}")
        except:
            pass

    # div/kart bazli sonuclar
    print("\n--- DIV YAPILARINI ARA ---")
    interesting_selectors = [
        "div.search-result",
        "div.result-list",
        "div.ihale",
        "div[class*='result']",
        "div[class*='list']",
        "div[class*='ihale']",
        "div[class*='tender']",
        "div[class*='card']",
        "div[class*='row']",
        "div[class*='item']",
        "div[class*='grid']",
        "app-search-result",
        "app-ihale",
        "app-tender",
        "[class*='sonuc']",
        "[class*='kayit']",
        "tr[class*='ihale']",
        "mat-row",
        "mat-card",
        "ngb-accordion",
        ".ag-row",
        ".p-datatable",
        ".p-datatable-tbody tr",
        ".ui-datatable",
        "p-table",
        ".cdk-row",
    ]
    for sel in interesting_selectors:
        try:
            el = page.locator(sel)
            c = el.count()
            if c > 0:
                first_text = el.first.inner_text(timeout=1000).strip()[:80].replace("\n", " | ")
                print(f"  '{sel}' -> {c} adet, ilk: '{first_text}'")
        except:
            pass

    # Body'nin ana yapisi
    print("\n--- BODY CHILD TAGS ---")
    try:
        tags = page.evaluate("""() => {
            const body = document.body;
            const result = [];
            for (const child of body.children) {
                result.push({
                    tag: child.tagName,
                    cls: (child.className || '').toString().substring(0, 60),
                    id: child.id || '',
                    childCount: child.children.length,
                });
            }
            return result;
        }""")
        for t in tags:
            print(f"  <{t['tag']} id='{t['id']}' class='{t['cls']}' children={t['childCount']}>")
    except Exception as e:
        print(f"  Hata: {e}")

    # Angular component'lerini ara
    print("\n--- ANGULAR COMPONENTLER ---")
    try:
        components = page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const comps = new Set();
            for (const el of all) {
                if (el.tagName.includes('-') && !el.tagName.startsWith('X-')) {
                    comps.add(el.tagName.toLowerCase());
                }
            }
            return [...comps].sort();
        }""")
        for c in components:
            count = page.locator(c).count()
            print(f"  <{c}> x{count}")
    except Exception as e:
        print(f"  Hata: {e}")

    # Son olarak, ana icerik bolgesindeki metni goster
    print("\n--- ANA ICERIK (ilk 2000 karakter) ---")
    try:
        # main veya app-root icerigini al
        for sel in ["main", "app-root", "#app", "#root", ".container", "body"]:
            el = page.locator(sel).first
            if el.count() > 0:
                txt = el.inner_text(timeout=3000)
                # Sadece bos olmayan satirlari goster
                lines = [l.strip() for l in txt.split("\n") if l.strip()]
                output = "\n".join(lines[:50])
                print(f"  [{sel}] ({len(txt)} karakter, {len(lines)} satir)")
                print(output[:2000])
                break
    except Exception as e:
        print(f"  Hata: {e}")

    print("\n[4] Bitti. Tarayici kapatiliyor.")
    context.close()
    browser.close()
