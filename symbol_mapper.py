"""
Map full company names to futures symbols
"""

# Common mappings
SYMBOL_MAP = {
    # Full Name → Short Symbol
    'TATASTEEL': 'TATSTE',
    'TATA STEEL': 'TATSTE',
    'RELIANCE': 'RELIND',
    'RELIANCE INDUSTRIES': 'RELIND',
    'INFOSYS': 'INFTEC',
    'INFY': 'INFTEC',
    'TCS': 'TCS',
    'TATA CONSULTANCY': 'TCS',
    'HDFCBANK': 'HDFBAN',
    'HDFC BANK': 'HDFBAN',
    'ICICIBANK': 'ICIBAN',
    'ICICI BANK': 'ICIBAN',
    'SBIN': 'STABAN',
    'SBI': 'STABAN',
    'STATE BANK': 'STABAN',
    'WIPRO': 'WIPRO',
    'BHARTIARTL': 'BHAAIR',
    'BHARTI AIRTEL': 'BHAAIR',
    'ITC': 'ITC',
    'MARUTI': 'MARUTI',
    'BAJAJ FINANCE': 'BAJFI',
    'BAJFINANCE': 'BAJFI',
    'LT': 'LARTOU',
    'LARSEN': 'LARTOU',
    'ADANIENT': 'ADAENT',
    'ADANI ENTERPRISES': 'ADAENT',
    'ADANIPORTS': 'ADAPOR',
    'SUNPHARMA': 'SUNPHA',
    'TITAN': 'TITIND',
    'ULTRACEMCO': 'ULTCEM',
    'ASIANPAINT': 'ASIPAI',
    'NESTLEIND': 'NESIND',
    'HINDUNILVR': 'HINLEV',
    'KOTAKBANK': 'KOTMAH',
    'AXISBANK': 'AXIBAN',
    'INDUSINDBK': 'INDBA',
    'BSE': 'BSE',
    'BSEIND': 'BSE',
    'HAL': 'HINAER',
    'HINDUSTAN AERONAUTICS': 'HINAER',
    'HEROMOTOCO': 'HERMOT',
    'HERO MOTOCORP': 'HERMOT',
    'HERO': 'HERMOT',
    'MCX': 'MCX',
    'POWERGRID': 'POWGRI',
    'POWER GRID': 'POWGRI',
    'DIXON': 'DIXON',
    'DIXON TECH': 'DIXON',
    'DIXON TECHNOLOGIES': 'DIXON',
    'TVSMOTOR': 'TVSMOT',
    'TVS MOTOR': 'TVSMOT',
    'TVS': 'TVSMOT',
    'IIFL': 'IIFL',
    'IIFL FINANCE': 'IIFL',
}

def normalize_symbol(symbol_or_name):
    """
    Convert any variant to short symbol
    
    Args:
        symbol_or_name: Full name or symbol
    
    Returns:
        str: Short symbol for token lookup
    """
    # Clean input
    cleaned = symbol_or_name.upper().strip()
    cleaned = cleaned.replace(' LIMITED', '').replace(' LTD', '')
    cleaned = cleaned.replace('.', '').replace('-', '')
    
    # Direct lookup
    if cleaned in SYMBOL_MAP:
        return SYMBOL_MAP[cleaned]
    
    # Return as-is (might already be short form)
    return cleaned


def extract_symbols_from_text(text):
    """
    Extract stock symbols from assistant recommendation text
    
    Args:
        text: Assistant's output text
    
    Returns:
        list: List of normalized symbols
    """
    import re
    
    # Pattern 0a: - SYMBOLS: TATASTEEL, RELIANCE, INFY (Comma-separated list)
    pattern0a = r'SYMBOLS?:\s+([A-Z][A-Z0-9,\s]+)'
    matches0a_raw = re.findall(pattern0a, text)
    matches0a = []
    for match in matches0a_raw:
        # Split by comma and clean
        symbols = [s.strip() for s in match.split(',') if s.strip()]
        matches0a.extend(symbols)
    
    # Pattern 0b: SYMBOL: TATASTEEL (with colon, not in table headers)
    pattern0b = r'^SYMBOL:\s+([A-Z][A-Z0-9]+)\s*$'
    matches0b = re.findall(pattern0b, text, re.MULTILINE)
    
    # Pattern 0c: SYMBOL TATASTEEL (without colon, standalone line)
    pattern0c = r'^SYMBOL\s+([A-Z][A-Z0-9]+)\s*$'
    matches0c = re.findall(pattern0c, text, re.MULTILINE)
    
    # Pattern 0d: **🔖 SYMBOL:** RELIANCE (markdown bold with emoji)
    pattern0d = r'\*\*[^\*]*SYMBOL[^\*]*:\*\*\s*([A-Z][A-Z0-9]+)'
    matches0d = re.findall(pattern0d, text)
    
    # Combine all SYMBOL patterns (highest priority)
    matches0 = matches0a + matches0b + matches0c + matches0d
    
    # Pattern 1: **Stock Name & Symbol:** BSE Ltd
    pattern1 = r'\*\*Stock Name & Symbol:\*\*\s+([A-Z][A-Za-z0-9 &]+?)(?:\n|$)'
    matches1 = re.findall(pattern1, text, re.MULTILINE)
    
    # Pattern 2: **Symbol: TATASTEEL**
    pattern2 = r'\*\*(?:Symbol)[:\s]+([A-Z0-9]+)\*\*'
    matches2 = re.findall(pattern2, text)
    
    # Pattern 3: Stock Name: TATASTEEL (without **)
    pattern3 = r'(?:Stock Name|Symbol)[:\s]+([A-Z][A-Za-z0-9 &]+?)(?:\n|,|\()'
    matches3 = re.findall(pattern3, text)
    
    # Pattern 4: STOCK #1: BSE (LONG)
    pattern4 = r'STOCK #\d+:\s+([A-Z][A-Za-z0-9 ]+?)\s+\('
    matches4 = re.findall(pattern4, text)
    
    # Pattern 5: | **Power Grid**    | Long  (Markdown table format)
    pattern5 = r'\|\s*\*\*([A-Z][A-Za-z0-9 ]+?)\*\*\s*\|'
    matches5 = re.findall(pattern5, text)
    
    # Pattern 6: | Power Grid   | Utilities  (table without **)
    pattern6 = r'\|\s+([A-Z][A-Za-z0-9 ]+?)\s+\|\s+(?:Utilities|Manufacturing|Metals|Autos|Finance|NBFC|Banking|IT|Pharma|FMCG)'
    matches6 = re.findall(pattern6, text)
    
    # Combine all matches (Pattern 0 first for priority)
    all_symbols = matches0 + matches1 + matches2 + matches3 + matches4 + matches5 + matches6
    
    # Normalize symbols
    normalized = []
    skip_words = {'ENTRY', 'ZONE', 'STOP', 'LOSS', 'TARGET', 'POSITION', 'SIZE',
                  'SYMBOL', 'STOCK', 'DIRECTION', 'CONTRACT', 'LOT', 'PARAMETER',
                  'VALUE', 'REASONING', 'RISK', 'REWARD'}
    
    for s in all_symbols:
        s = s.strip()
        
        # Skip if contains newlines (malformed match)
        if '\n' in s:
            continue
        
        # Remove common suffixes
        s = s.replace(' Ltd', '').replace(' LIMITED', '').replace(' LTD', '')
        s = s.strip()
        
        # Skip table headers (check if string contains any skip word)
        s_upper = s.upper()
        if any(word in s_upper for word in skip_words):
            continue
        
        # Skip if contains numbers (like "TARGET 1", "STOCK #1")
        if any(char.isdigit() for char in s):
            continue
        
        if s and len(s) > 1:  # Must have at least 2 chars
            normalized.append(normalize_symbol(s))
    
    # Remove duplicates, preserve order
    seen = set()
    result = []
    for sym in normalized:
        if sym not in seen and len(sym) >= 2:
            seen.add(sym)
            result.append(sym)
    
    return result
