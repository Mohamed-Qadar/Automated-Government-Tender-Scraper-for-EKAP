# Automated Government Tender Scraper for EKAP

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-v1.40%2B-green.svg)](https://playwright.dev/python/)
[![Pandas](https://img.shields.io/badge/pandas-v2.0%2B-orange.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An automated Python-based scraping system designed to extract real-time public procurement and tender data from the official Turkish EKAP (Electronic Public Procurement Platform) portal. 

This standalone utility automates browser interactions with the EKAP web application to query, extract, filter, and compile tender details into clean, professionally-formatted Excel spreadsheets.

---

## Table of Contents
- [Core Features](#core-features)
- [Technical Stack](#technical-stack)
- [Project Structure](#project-structure)
- [Installation Guide](#installation-guide)
- [Usage Instructions](#usage-instructions)
- [Output Example](#output-example)
- [Anti-Bot & Reliability Mitigations](#anti-bot--reliability-mitigations)
- [Disclaimer](#disclaimer)

---

## Core Features

- **Automated Search & Navigation**: Uses Playwright to programmatically navigate the EKAP search page (`https://ekapv2.kik.gov.tr/ekap/search`) and interact with dynamic Angular SPA components.
- **Dynamic Filtering**: Filters listings in real-time by province (defaulting to **Elazığ**) and filters out inactive records to only capture tenders with the **"Open for Participation"** status.
- **Granular Data Extraction**: Scrapes the following key fields from each tender record:
  - **Tender ID (IKN)** (e.g., `2026/271215`)
  - **Title / Subject** (Subject of the contract)
  - **Ordering Authority** (İdare Adı)
  - **Announcement / Tender Date**
  - **Location / Province** (İl)
  - **Procurement Type** (Alım Türü: Mal, Hizmet, Yapım, vb.)
  - **Procedure Type** (İhale Usulü)
- **Production-Grade Excel Reports**: Leverages `pandas` and `openpyxl` to compile data into styled spreadsheets featuring professional typography, header styling, custom column width autofitting, and zebra-striping.
- **Flexible Execution Modes**: Run in background (headless) mode for automated scripts or headed (visible browser window) mode for testing and debugging.

---

## Technical Stack

- **Core**: Python 3.10+
- **Browser Automation**: [Playwright for Python](https://playwright.dev/python/)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/)
- **Excel Formatting**: [OpenPyXL](https://openpyxl.readthedocs.io/)

---

## Project Structure

```text
Automated-Government-Tender-Scraper-for-EKAP/
├── exports/
│   └── excel/                      # Generated Excel (.xlsx) reports
├── main.py                         # Standalone scraper entry point & CLI controller
├── ekap_scraper.py                 # Core Playwright browser navigation & extraction logic
├── public_source_adapter.py        # Data adapter and parsing layer
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

---

## Installation Guide

Follow these steps to set up the scraper locally.

### 1. Clone the Repository
```bash
git clone https://github.com/Mohamed-Qadar/Automated-Government-Tender-Scraper-for-EKAP.git
cd Automated-Government-Tender-Scraper-for-EKAP
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Web Drivers
Playwright requires its own browser binaries to interact with pages. Install the Chromium browser driver:
```bash
playwright install chromium
```

---

## Usage Instructions

The scraper is fully configurable via Command Line Interface (CLI) arguments.

### Basic Execution (Headless Mode)
Runs the scraper in the background, filters by "Elazığ", and exports data to `exports/excel/`.
```bash
python main.py
```

### Headed Mode (Browser Visible)
Useful for debugging and observing how the browser interacts with the EKAP portal.
```bash
python main.py --visible
```

### Custom Province Filtering
Specify a custom target province using the `--province` flag (supports Turkish character casing mapping automatically).
```bash
python main.py --province "Ankara"
```

### Custom Record Limits
Control the maximum number of tender records to scrape (default is 20).
```bash
python main.py --max 50
```

### Pull All Records (No Location Filters)
Extract all active tenders across all provinces of Turkey.
```bash
python main.py --no-filter
```

---

## Output Example

### Console Output
When executed, the script provides real-time progress updates and prints a summary:

```text
[*] EKAP İhale Botu başlatılıyor...
[*] Mod: Headless
[*] Hedef il: Elazığ
[*] Maksimum ihale: 20
[*] User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
[*] EKAP sayfası açılıyor: https://ekapv2.kik.gov.tr/ekap/search
[*] Angular bileşenlerinin yüklenmesi bekleniyor...
[*] İl filtresi ayarlanıyor: Elazığ
[*] Listeden tıklanacak il: ELAZIĞ
[✓] İl filtresi ayarlandı: Elazığ
[*] Filtrele butonuna tıklanıyor...
[✓] İhale kartları yüklendi
[*] Sayfa 1: 10 ihale kartı bulundu
[*] Filtre (Elazığ + Katılıma Açık): 8/10 ihale
[✓] Excel kaydedildi: C:\...\exports\excel\ekap_ihaleler_Elazig_20260608_131000.xlsx

============================================================
  EKAP İHALE BOT — SONUÇ ÖZETİ
============================================================
  Toplam çekilen ihale sayısı : 10
  Filtrelenen (Elazığ)        : 8

  İlk 3 ihale:
    1. [2026/104321] Hastane Hizmet Alım İhalesi
    2. [2026/105432] Elazığ İl Özel İdaresi Yol Yapım İşleri
    3. [2026/108923] Okul Bakım-Onarım Malzeme Alımı
============================================================
```

### Excel Report Structure
The generated Excel spreadsheet is saved inside `exports/excel/` and contains the following styled structure:

| İhale Kayıt No (İKN) | İhale Başlığı | İdare Adı | İlan Tarihi | Durum | İl | Alım Türü | İhale Usulü |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `2026/104321` | Temizlik Hizmet Alımı | Elazığ Fırat Üniversitesi | 15.06.2026 | Katılıma Açık | Elazığ | Hizmet | Açık |
| `2026/105432` | Köy Yolları Asfaltlama | Elazığ İl Özel İdaresi | 18.06.2026 | Katılıma Açık | Elazığ | Yapım | Açık |

---

## Anti-Bot & Reliability Mitigations

To ensure reliable data access without overloading or triggering security mechanisms on the public portal, the system includes:
- **Automation Controller Hiding**: Removes the standard browser `navigator.webdriver` property to avoid generic detection rules.
- **Randomized User-Agents**: Rotates through a curated pool of modern, real-world user-agent strings.
- **Human-Like Inter-Request Delays**: Avoids rapid bursts of traffic by incorporating random micro-delays between browser actions.
- **Robust Overlay/Popup Handling**: Automatically detects and dismisses cookie consent banners, site popups, and notification modals.

---

## Disclaimer

> [!WARNING]
> **Educational & Research Purposes Only**
>
> This project is designed solely for educational, academic, and research purposes. The developers do not take responsibility for how this scraper is deployed.
> 
> - **Terms of Service**: Automated scraping of public government portals may conflict with local regulations or website terms. Please consult the legal terms of the target platform.
> - **Maintenance**: The EKAP portal is an Angular single-page application. Any changes to the front-end architecture, class names, DOM elements, or API requests may break the scraper. No guarantees are made regarding its long-term reliability.
> - **Resource Preservation**: This utility is built to minimize load on the EKAP servers. Users must run this script with appropriate delays and limits to avoid resource exhaustion of public resources.
