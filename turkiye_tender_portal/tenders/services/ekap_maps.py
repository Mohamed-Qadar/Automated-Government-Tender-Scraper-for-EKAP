"""Static lookup maps for the EKAP v2 public API.

Sourced from EKAP's public frontend configuration. Only used to translate
our clean province names / tender types into the IDs the public search API
expects, and to translate API responses back into our domain values.
"""
from .. import constants

# Our tender_type code -> EKAP "ihaleTuruId"
TENDER_TYPE_TO_EKAP_ID = {
    constants.TENDER_TYPE_MAL: 1,         # Mal
    constants.TENDER_TYPE_YAPIM: 2,       # Yapım
    constants.TENDER_TYPE_HIZMET: 3,      # Hizmet
    constants.TENDER_TYPE_DANISMANLIK: 4, # Danışmanlık
}

# EKAP "ihaleTip" code (string) -> our tender_type code
EKAP_TIP_TO_TENDER_TYPE = {
    "1": constants.TENDER_TYPE_MAL,
    "2": constants.TENDER_TYPE_YAPIM,
    "3": constants.TENDER_TYPE_HIZMET,
    "4": constants.TENDER_TYPE_DANISMANLIK,
}

# our tender_type -> our category
TENDER_TYPE_TO_CATEGORY = {
    constants.TENDER_TYPE_MAL: "mal_alimi",
    constants.TENDER_TYPE_YAPIM: "yapim_ihaleleri",
    constants.TENDER_TYPE_HIZMET: "hizmet_alimi",
    constants.TENDER_TYPE_DANISMANLIK: "danismanlik",
}

# Turkish plate code (1-81) -> EKAP province API id (used in ihaleIlIdList)
PLATE_TO_API_ID = {
    1: 245, 2: 246, 3: 247, 4: 248, 5: 250, 6: 251, 7: 252, 8: 254, 9: 255,
    10: 256, 11: 260, 12: 261, 13: 262, 14: 263, 15: 264, 16: 265, 17: 266,
    18: 267, 19: 268, 20: 269, 21: 270, 22: 272, 23: 273, 24: 274, 25: 275,
    26: 276, 27: 277, 28: 278, 29: 279, 30: 280, 31: 281, 32: 283, 33: 302,
    34: 284, 35: 285, 36: 289, 37: 290, 38: 291, 39: 293, 40: 294, 41: 296,
    42: 297, 43: 298, 44: 299, 45: 300, 46: 286, 47: 301, 48: 303, 49: 304,
    50: 305, 51: 306, 52: 307, 53: 309, 54: 310, 55: 311, 56: 312, 57: 313,
    58: 314, 59: 317, 60: 318, 61: 319, 62: 320, 63: 315, 64: 321, 65: 322,
    66: 324, 67: 325, 68: 249, 69: 259, 70: 288, 71: 292, 72: 258, 73: 316,
    74: 257, 75: 253, 76: 282, 77: 323, 78: 287, 79: 295, 80: 308, 81: 271,
}

# Province name (as in our constants) -> plate code
NAME_TO_PLATE = {name: plate for plate, name in constants.PROVINCES}


def province_name_to_api_id(name):
    plate = NAME_TO_PLATE.get((name or "").strip())
    if plate is None:
        return None
    return PLATE_TO_API_ID.get(plate)


def status_from_description(desc: str) -> str:
    d = (desc or "").lower()
    if "iptal" in d:
        return constants.STATUS_CANCELLED
    if "sözleşme" in d or "sozlesme" in d:
        return constants.STATUS_FINALIZED
    if "tamamlan" in d or "sonuç" in d or "sonuc" in d:
        return constants.STATUS_RESULT
    return constants.STATUS_ACTIVE
