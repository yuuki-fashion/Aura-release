import os
import urllib.parse
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wimjkvkprixuumnuabjd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_KEY else None

BRANDS = list(dict.fromkeys([
    "08sircus", "1PIU1UGUALE3", "3.1 Phillip Lim", "4℃", "A BATHING APE", "A.P.C.", "A.PRESSE", "ABAHOUSE", 
    "Acne Studios", "ACQUA DI PARMA", "ACRONYM", "ADAM ET ROPÉ", "ADDICTION", "adidas", "Aēsop", "Aeta", 
    "Afternoon Tea LIVING", "agnès b.", "AHKAH", "AKIRANAKA", "ALAÏA", "ALBION", "ALDEN", "alexanderwang", 
    "ALEXANDRE DE PARIS", "AMBUSH", "Ami Paris", "AMIRI", "AMPHI", "ANATOMICA", "ANAYI", "ANNA SUI", 
    "ANREALAGE", "ANTEPRIMA", "ANYA HINDMARCH", "ARC’TERYX", "ASICS", "ASPESI", "ASTRAT", "ATELIER BETON", 
    "atmos", "ATON", "AURALEE", "A|X ARMANI EXCHANGE", "B.A", "Baccarat", "BALENCIAGA", "BALLSEY", 
    "Bally", "BALMAIN", "Barbour", "BAPE", "BATONER", "BAUM", "BAUM UND PFERDGARTEN", "BEAMS", 
    "BEAMS BOY", "BEAMS F", "BEAUTY&YOUTH UNITED ARROWS", "beautiful people", "BELVEST", "BERLUTI", 
    "BIOTOP", "BIRKENSTOCK", "BISONTE", "BlackEyePatch", "BLAMINK", "BOBBI BROWN", "BODHI", "BOGLIOLI", 
    "BORSALINO", "BOSS", "BOTTEGA VENETA", "BOUCHERON", "BRANDALISED", "BRIEFING", "BRUNELLO CUCINELLI", 
    "Brooks Brothers", "BURBERRY", "BVLGARI", "BYREDO", "C.P. COMPANY", "CA4LA", "CABaN", "Calvin Klein", 
    "CAMPER", "CANADA GOOSE", "CANALI", "CANDY STRIPPER", "CANESSA", "CAPRICE", "CARHARTT", "Cartier", 
    "Casio", "CASABLANCA", "CASEY CASEY", "CELINE", "CFCL", "Champion", "CHANEL", "CHAUMET", "Chloé", 
    "Christian Louboutin", "Church’s", "CITIZEN", "CLANE", "CLARINS", "Clarks", "clé de peau Beauté", 
    "CLINIQUE", "COACH", "COCCOFIORE", "COLUMBIA", "COMME des GARÇONS", "COMME des GARÇONS HOMME", 
    "COMME des GARÇONS SHIRT", "COMOLI", "CONVERSE", "Cote&Ciel", "CULLNI", "DAIRIKU", "DAIWA", 
    "DAIWA PIER39", "DANIEL WELLINGTON", "DEAN & DELUCA", "DECORTÉ", "DELVAUX", "DENHAM", "DIESEL", 
    "DIGAWEL", "DIOR", "Diptyque", "DOLCE&GABBANA", "doublet", "Dr. Martens", "DRIES VAN NOTEN", 
    "DRAGON", "DSQUARED2", "dunhill", "e.m.", "EOTOTO", "EBEL", "EDWIN", "ELIXIR", "EMILIO PUCCI", 
    "EMPORIO ARMANI", "ENFÖLD", "ENGINEERED GARMENTS", "Ermenegildo Zegna", "Estée Lauder", "ete", 
    "ETRO", "EYEVAN", "EYEVAN 7285", "F.C.Real Bristol", "F/CE.", "FACETASM", "FANCL", "FEILER", 
    "FENDI", "Ferragamo", "FILA", "foot the coacher", "Francfranc", "FRANK LEDER", "FRED", "FRED PERRY", 
    "FreshService", "FURLA", "G-SHOCK", "GANNI", "GAP", "gelato pique", "GENTLE MONSTER", "GIVENCHY", 
    "GLOBE-TROTTER", "GOLDEN GOOSE", "Goldwin", "GOYARD", "GRAMICCI", "Graphpaper", "GREGORY", 
    "GU", "GUCCI", "GUERLAIN", "Gymphlex", "H&M", "Hender Scheme", "HAMILTON", "Hanes", "HARE", 
    "HARRY WINSTON", "HARUTA", "HELLY HANSEN", "HERMÈS", "HERNO", "HERVE CHAPELIER", "HOKA", 
    "HOLLYWOOD RANCH MARKET", "HUBLOT", "HUF", "HUGO BOSS", "HUMAN MADE", "HUNTER", "HYKE", 
    "HYSTERIC GLAMOUR", "IENA", "IL BISONTE", "INVERALLAN", "IPSA", "ISABEL MARANT", "ISSEY MIYAKE", 
    "IVORY&CO", "IWC SCHAFFHAUSEN", "J.M. WESTON", "JACQUEMUS", "JieDa", "JIL SANDER", 
    "JILL STUART", "JIMMY CHOO", "JINS", "JO MALONE LONDON", "JOHN LAWRENCE SULLIVAN", "JOHN LOBB", 
    "JOHN SMEDLEY", "JOHNSTONS", "JOURNAL STANDARD", "JULIUS", "JUNYA WATANABE", "JW Anderson", 
    "KANEBO", "KAPITAL", "KAPTAIN SUNSHINE", "KATE", "kate spade new york", "KEEN", "KENZO", 
    "KIJIMA TAKAYUKI", "KITH", "KOLOR", "L’OCCITANE", "L.L.Bean", "LA MER", "LACOSTE", "LAD MUSICIAN", 
    "LANCÔME", "LANVIN", "LE LABO", "Lee", "LEMAIRE", "Levi’s", "LILY BROWN", "LOEWE", "LONGCHAMP", 
    "LONGINES", "Loro Piana", "LOUIS VUITTON", "LUNASOL", "Lululemon", "M A S U", "MACKINTOSH", 
    "MADISONBLUE", "Maison Kitsuné", "Maison Margiela", "Maison MIHARA YASUHIRO", "MAISON SPECIAL", 
    "Mame Kurogouchi", "Manhattan Portage", "MARC JACOBS", "MARGARET HOWELL", "MARIHA", "Marimekko", 
    "MARNI", "Martin Margiela", "Master-Piece", "Max Mara", "MEDICOM TOY", "MICHAEL KORS", "MIKIMOTO", 
    "minä perhonen", "MISSONI", "MIU MIU", "MIZUNO", "MM6 Maison Margiela", "MONCLER", "MONTBLANC", 
    "MOSCOT", "MOUSSY", "MUJI", "MÜHLBAUER", "M·A·C", "N.HOOLYWOOD", "nanamica", "NANGA", "NANO universe", 
    "NARS", "NEEDLES", "NEIGHBORHOOD", "NEW BALANCE", "NEW ERA", "NIKE", "niko and …", "NINA RICCI", 
    "NOAH", "nonnative", "OAKLEY", "OFF-WHITE", "OFFICINE UNIVERSELLE BULY", "Old England", 
    "Oliver Peoples", "OMEGA", "On", "Onitsuka Tiger", "OOFOS", "ORCIVAL", "ORIS", "OSAJI", "OUR LEGACY", 
    "OWEN", "P.A.M.", "PANERAI", "Paraboot", "Patagonia", "Paul Smith", "PEACH JOHN", "PELLICO", 
    "PENDLETON", "PHILIPPE MODEL", "PIERRE HARDY", "POLO RALPH LAUREN", "PORTER", "PRADA", "Proenza Schouler", 
    "PUBLIC TOKYO", "PUMA", "RRL", "Ralph Lauren", "RAMIDUS", "Ray-Ban", "READYMADE", "RED WING", 
    "Reebok", "ReFa", "REGAL", "REPRONIZER", "Rick Owens", "RIMOWA", "RMK", "ROLEX", "Ron Herman", 
    "ROPE", "SABON", "SACAI", "SAINT LAURENT", "SALOMON", "SAMANTHA THAVASA", "SANDERS", "SANTA MARIA NOVELLA", 
    "Schott", "SEIKO", "SERGIO ROSSI", "SHIPS", "SHIRO", "SHISEIDO", "shu uemura", "SK-II", "SNIDEL", 
    "Snow Peak", "SOPHNET.", "SSSTEIN", "STAR JEWELRY", "STELLA McCARTNEY", "STONE ISLAND", 
    "STUDIO NICHOLSON", "STUDIOUS", "STÜSSY", "SUQQU", "SWAROVSKI", "TAG Heuer", "TAION", "TASAKI", 
    "TATRAS", "TEÄTORA", "Teva", "THE NORTH FACE", "THE ROW", "THOM BROWNE", "THREE", "TIFFANY & Co.", 
    "Timberland", "TIMEX", "TOD’S", "TOGA", "TOM FORD", "TOM WOOD", "TOMORROWLAND", "TORY BURCH", 
    "TRADITIONAL WEATHERWEAR", "TSUCHIYA KABAN", "TUDOR", "UGG", "uka", "UNDERCOVER", "UNIQLO", 
    "UNITED ARROWS", "UNITED TOKYO", "UNUSED", "URBAN RESEARCH", "VALENTINO", "VALEXTRA", 
    "VAN CLEEF & ARPELS", "VANS", "VERSACE", "VERY", "VIKTOR & ROLF", "VISVIM", "VIVIENNE WESTWOOD", 
    "WACKO MARIA", "WEDGWOOD", "WHITE MOUNTAINEERING", "WILD THINGS", "WIND AND SEA", "WOOLRICH", 
    "WTAPS", "X-GIRL", "Y's", "Y-3", "YAECA", "YOHJI YAMAMOTO", "YOKE", "ZARA", "ZEGNA", "ZOFF", "ZUCCA"
]))

def register_official_sources(brand_name):
    if not supabase:
        return
    prtimes_url = f"https://prtimes.jp/main/html/searchrlp/company_id/0/keyword/{urllib.parse.quote(brand_name)}"
    google_official_url = f"https://www.google.com/search?q={urllib.parse.quote(brand_name + ' 公式 新作 Collection -site:fashion-press.net')}"

    sources = [
        {"product_name": f"{brand_name} 公式プレスリリース (PR TIMES)", "source_url": prtimes_url},
        {"product_name": f"{brand_name} 公式情報・コレクション直接検索", "source_url": google_official_url}
    ]

    for src in sources:
        check_res = supabase.from_('products').select('id').eq('source_url', src['source_url']).execute()
        if not check_res.data:
            data = {
                "brand": brand_name,
                "product_name": src['product_name'],
                "price": "公式参照",
                "image_url": "https://via.placeholder.com/300?text=Official+Source",
                "source_url": src['source_url'],
                "release_date": "NEW"
            }
            supabase.from_('products').insert(data).execute()

if __name__ == "__main__":
    for brand in BRANDS:
        register_official_sources(brand)
