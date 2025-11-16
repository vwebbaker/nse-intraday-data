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
    'INFOSYS': 'INFY',
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
    'HEROMOTOCO': 'HERMOT',
    'HERO MOTOCORP': 'HERMOT',
    'HERO': 'HERMOT',
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
    
    # Pattern 0: SYMBOL: TATASTEEL (PRIORITY - Automated format from prompt)
    pattern0 = r'SYMBOL:\s+([A-Z][A-Z0-9]+)'
    matches0 = re.findall(pattern0, text)
    
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
    for s in all_symbols:
        s = s.strip()
        # Remove common suffixes
        s = s.replace(' Ltd', '').replace(' LIMITED', '').replace(' LTD', '')
        s = s.strip()
        
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
