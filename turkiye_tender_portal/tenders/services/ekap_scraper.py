"""
EKAP v2 public tender-search adapter (real data).

Targets the PUBLIC, login-free tender search used by
https://ekapv2.kik.gov.tr/ekap/search  (no login, no e-signature, no CAPTCHA).

Endpoint:  POST https://ekapv2.kik.gov.tr/b_ihalearama/api/Ihale/GetListByParameters

The public API requires lightweight request "signing" headers that the EKAP
frontend itself generates in the browser (an AES-CBC encrypted GUID + timestamp
using a key shipped in EKAP's public frontend config). We replicate exactly what
the public web page does — we do NOT bypass any authentication, paywall or
security control; this is the same anonymous request the public search page makes.

Responsible-use controls:
  * Politeness delay between requests, retry limit, timeout (from settings).
  * Page size capped; we never crawl the whole platform in one run.
  * Every fetch attempt is logged by the caller (tender_fetcher).

Requires: httpx, cryptography  (see requirements.txt)
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import ssl
import time
import uuid
from datetime import date, datetime
from typing import Optional

from django.conf import settings

from .. import constants
from . import ekap_maps
from .public_source_adapter import BasePublicSourceAdapter, FetchParams, RawTender

logger = logging.getLogger("tenders")

BASE_URL = "https://ekapv2.kik.gov.tr"
TENDER_ENDPOINT = "/b_ihalearama/api/Ihale/GetListByParameters"
DETAIL_URL_TMPL = "https://ekapv2.kik.gov.tr/ekap/search/ihale-detay/{id}"

# Key from EKAP's PUBLIC frontend environment config (used by the browser).
_R8FACT_KEY = b"Qm2LtXR0aByP69vZNKef4wMJ"


def tr_title(text: str) -> str:
    """Capitalize Turkish strings correctly (e.g. ELAZIĞ -> Elazığ, İSTANBUL -> İstanbul)."""
    if not text:
        return ""
    words = []
    for word in text.split():
        if not word:
            continue
        first = word[0]
        rest = word[1:]
        
        # Capitalize first char
        if first == 'i':
            first = 'İ'
        elif first == 'ı':
            first = 'I'
        else:
            first = first.upper()
            
        # Lowercase rest of chars
        rest_lower = ""
        for c in rest:
            if c == 'İ':
                rest_lower += 'i'
            elif c == 'I':
                rest_lower += 'ı'
            else:
                rest_lower += c.lower()
        words.append(first + rest_lower)
    return " ".join(words)


def strip_html(html_text: str) -> str:
    """Clean HTML from tender announcements to store readable plain text."""
    if not html_text:
        return ""
    # Replace common HTML block tags with newlines
    text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</tr>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode basic HTML entities
    text = (text.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", '"'))
    # Clean up whitespace line-by-line
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join([line for line in lines if line])


class EkapPublicAdapter(BasePublicSourceAdapter):
    name = constants.SOURCE_EKAP

    def __init__(self):
        self.delay = float(getattr(settings, "FETCH_REQUEST_DELAY", 1.5))
        self.max_retries = int(getattr(settings, "FETCH_MAX_RETRIES", 3))
        self.timeout = int(getattr(settings, "FETCH_TIMEOUT", 30))
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "tr",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/ekap/search",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
            ),
            "api-version": "v1",
        }

    # -- request signing (mirrors the public EKAP frontend) --------------- #
    def _aes_cbc_encrypt(self, plaintext: str, key: bytes, iv: bytes) -> bytes:
        from cryptography.hazmat.primitives import padding as crypto_padding
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        padder = crypto_padding.PKCS7(128).padder()
        padded = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        enc = cipher.encryptor()
        return enc.update(padded) + enc.finalize()

    def _security_headers(self) -> dict:
        guid = str(uuid.uuid4())
        iv = os.urandom(16)
        ts_ms = str(int(time.time() * 1000))
        r8id = base64.b64encode(self._aes_cbc_encrypt(guid, _R8FACT_KEY, iv)).decode()
        ts_enc = base64.b64encode(self._aes_cbc_encrypt(ts_ms, _R8FACT_KEY, iv)).decode()
        siv = base64.b64encode(iv).decode()
        return {
            "X-Custom-Request-Guid": guid,
            "X-Custom-Request-Siv": siv,
            "X-Custom-Request-Ts": ts_enc,
            "X-Custom-Request-R8id": r8id,
        }

    def _ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        # Some gov.tr endpoints need a relaxed cipher level.
        try:
            ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        except ssl.SSLError:
            pass
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    # -- payload ---------------------------------------------------------- #
    def _build_payload(self, params: FetchParams) -> dict:
        province_ids = []
        if not params.is_all_turkiye and params.province:
            api_id = ekap_maps.province_name_to_api_id(params.province)
            if api_id:
                province_ids = [api_id]
            else:
                logger.warning("EKAP: bilinmeyen il '%s'", params.province)

        type_ids = []
        if params.tender_type:
            tid = ekap_maps.TENDER_TYPE_TO_EKAP_ID.get(params.tender_type)
            if tid:
                type_ids = [tid]

        def _d(d):
            return d.strftime("%Y-%m-%d") if isinstance(d, date) else None

        kw = (params.keyword or "").strip()
        take = min(int(params.limit or 50), 100)

        return {
            "searchText": kw,
            "filterType": None,
            "ikNdeAra": False,
            "ihaleAdindaAra": True,
            "ihaleIlanindaAra": bool(kw),
            "teknikSartnamedeAra": False,
            "idariSartnamedeAra": False,
            "benzerIsMaddesindeAra": False,
            "isinYapilacagiYerMaddesindeAra": False,
            "nitelikTurMiktarMaddesindeAra": False,
            "ihaleBilgilerindeAra": False,
            "sozlesmeTasarisindaAra": False,
            "teklifCetvelindeAra": False,
            "searchType": "GirdigimGibi",
            "iknYili": None,
            "iknSayi": None,
            "ihaleTarihSaatBaslangic": _d(params.date_from),
            "ihaleTarihSaatBitis": _d(params.date_to),
            "ilanTarihSaatBaslangic": None,
            "ilanTarihSaatBitis": None,
            "yasaKapsami4734List": [],
            "ihaleTuruIdList": type_ids,
            "ihaleUsulIdList": [],
            "ihaleUsulAltIdList": [],
            "ihaleIlIdList": province_ids,
            "ihaleDurumIdList": [],
            "idareIdList": [],
            "ihaleIlanTuruIdList": [],
            "teklifTuruIdList": [],
            "asiriDusukTeklifIdList": [],
            "istisnaMaddeIdList": [],
            "okasBransKodList": [],
            "okasBransAdiList": [],
            "titubbKodList": [],
            "gmdnKodList": [],
            "orderBy": "ihaleTarihi",   # sort by tender date
            "siralamaTipi": "desc",     # newest first
            "paginationSkip": 0,
            "paginationTake": take,
        }

    # -- HTTP with retry/backoff ----------------------------------------- #
    def _post(self, client, payload: dict):
        last = None
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = {**self.headers, **self._security_headers()}
                resp = client.post(
                    f"{BASE_URL}{TENDER_ENDPOINT}",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                time.sleep(self.delay)  # politeness
                return resp.json()
            except Exception as exc:  # noqa: BLE001
                last = exc
                wait = self.delay * attempt
                logger.warning(
                    "EKAP isteği %s/%s başarısız: %s (%.1fs sonra tekrar)",
                    attempt, self.max_retries, exc, wait,
                )
                time.sleep(wait)
        raise RuntimeError(f"EKAP isteği tüm denemelerde başarısız: {last}")

    def _fetch_detail(self, client, hash_id: str) -> Optional[dict]:
        url = f"{BASE_URL}/b_ihalearama/api/IhaleDetay/GetByIhaleIdIhaleDetay"
        body = json.dumps({"ihaleId": hash_id})
        headers = {**self.headers, **self._security_headers()}
        
        # Apply politeness delay
        time.sleep(self.delay)
        
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = client.post(url, content=body, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                wait = self.delay * attempt
                logger.warning("EKAP detay isteği %s/%s başarısız: %s (%.1fs sonra tekrar)",
                               attempt, self.max_retries, exc, wait)
                time.sleep(wait)
        logger.error("EKAP detay isteği tüm denemelerde başarısız: %s", hash_id)
        return None

    # -- parsing ---------------------------------------------------------- #
    @staticmethod
    def _parse_dt(value) -> Optional[date]:
        if not value:
            return None
        text = str(value)
        for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(text[:len(fmt) + 7].strip(), fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "")).date()
        except ValueError:
            return None

    def _to_raw(self, item: dict, detail: Optional[dict] = None) -> RawTender:
        # Default fallback values from the list search
        tid = item.get("id")
        ikn = item.get("ikn") or str(tid or "")
        title = item.get("ihaleAdi") or ""
        authority = item.get("idareAdi") or ""
        province = item.get("ihaleIlAdi") or ""
        district = ""
        ttype = ekap_maps.EKAP_TIP_TO_TENDER_TYPE.get(str(item.get("ihaleTip", "")), "")
        category = ekap_maps.TENDER_TYPE_TO_CATEGORY.get(ttype, "diger")
        procedure = item.get("ihaleUsulAciklama") or ""
        tdate = self._parse_dt(item.get("ihaleTarihSaat"))
        announcement_date = tdate
        work_location = province
        short_desc = title
        status = ekap_maps.status_from_description(item.get("ihaleDurumAciklama"))
        raw_payload = detail or item

        if detail and isinstance(detail, dict) and "item" in detail:
            det_item = detail["item"]
            
            # Use richer fields from detail
            ikn = det_item.get("ikn") or ikn
            title = det_item.get("ihaleAdi") or title
            
            # Idare fields
            idare = det_item.get("idare") or {}
            authority = idare.get("adi") or det_item.get("ihaleBilgi", {}).get("idareAdi") or authority
            
            # Province / District
            raw_prov = idare.get("il", {}).get("adi") or det_item.get("ihaleBilgi", {}).get("ihaleIlAdi") or province
            if raw_prov:
                province = tr_title(raw_prov)
            
            raw_dist = idare.get("ilce", {}).get("ilceAdi") or ""
            if raw_dist and raw_prov:
                prov_upper = raw_prov.upper()
                dist_upper = raw_dist.upper()
                if dist_upper.startswith(prov_upper):
                    raw_dist = raw_dist[len(raw_prov):].strip()
                district = tr_title(raw_dist)
            
            # Tender Type / Category mapping from details
            tip_desc = det_item.get("ihaleBilgi", {}).get("ihaleTipiAciklama") or ""
            if "mal" in tip_desc.lower():
                ttype = constants.TENDER_TYPE_MAL
            elif "hizmet" in tip_desc.lower():
                ttype = constants.TENDER_TYPE_HIZMET
            elif "yapım" in tip_desc.lower() or "yapim" in tip_desc.lower():
                ttype = constants.TENDER_TYPE_YAPIM
            elif "danışmanlık" in tip_desc.lower() or "danismanlik" in tip_desc.lower():
                ttype = constants.TENDER_TYPE_DANISMANLIK
            
            if ttype:
                category = ekap_maps.TENDER_TYPE_TO_CATEGORY.get(ttype, "diger")
            
            # Procedure
            procedure = det_item.get("ihaleBilgi", {}).get("ihaleUsulAciklama") or procedure
            
            # Dates
            # Announcement date is from ilanList[0]
            ilan_list = det_item.get("ilanList") or []
            if ilan_list:
                first_ilan = ilan_list[0]
                announcement_date = self._parse_dt(first_ilan.get("ilanTarihi")) or announcement_date
                
                # Strip HTML for short description
                veri_html = first_ilan.get("veriHtml") or ""
                if veri_html:
                    short_desc = strip_html(veri_html)
            
            # Tender date
            raw_tdate = det_item.get("ihaleBilgi", {}).get("ihaleTarihSaat")
            if raw_tdate:
                tdate = self._parse_dt(raw_tdate) or tdate
            
            # Work Location
            work_location = det_item.get("ihaleBilgi", {}).get("isinYapilacagiYer") or work_location
            
            # Status
            status = ekap_maps.status_from_description(det_item.get("ihaleBilgi", {}).get("ihaleDurumAciklama"))

        return RawTender(
            tender_no=ikn,
            title=title,
            authority_name=authority,
            province=province,
            district=district,
            tender_type=ttype,
            category=category,
            tender_procedure=procedure,
            announcement_date=announcement_date,
            tender_date=tdate,
            deadline_date=tdate,  # set deadline to tender date
            work_location=work_location,
            short_description=short_desc,
            official_url=DETAIL_URL_TMPL.format(id=tid) if tid else f"{BASE_URL}/ekap/search",
            source=constants.SOURCE_EKAP,
            status=status,
            extra=raw_payload,
        )

    # -- public API ------------------------------------------------------- #
    def fetch(self, params: FetchParams) -> list[RawTender]:
        import httpx

        payload = self._build_payload(params)
        logger.info("EKAP fetch payload il=%s tür=%s take=%s",
                    payload["ihaleIlIdList"], payload["ihaleTuruIdList"],
                    payload["paginationTake"])

        with httpx.Client(verify=self._ssl_context(), http2=False) as client:
            data = self._post(client, payload)

            items = data.get("list", []) if isinstance(data, dict) else []
            total = data.get("totalCount") if isinstance(data, dict) else None
            logger.info("EKAP yanıt: %s kayıt (toplam %s)", len(items), total)

            results = []
            for it in items:
                tid = it.get("id")
                detail_data = None
                if tid:
                    logger.info("EKAP detay çekiliyor: %s", tid)
                    detail_data = self._fetch_detail(client, tid)
                
                raw_tender = self._to_raw(it, detail_data)
                results.append(raw_tender)

        # Local district filter (district not provided by list endpoint).
        if params.district:
            d = params.district.strip().lower()
            results = [r for r in results if d in (r.title + r.work_location + r.district).lower()]
        return results
