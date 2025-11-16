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
    
    # Pattern 1: **Symbol: TATASTEEL**
    pattern1 = r'\*\*(?:Symbol|Stock)[:\s]+([A-Z0-9& ]+)\*\*'
    matches1 = re.findall(pattern1, text, re.IGNORECASE)
    
    # Pattern 2: Stock Name & Symbol section
    pattern2 = r'(?:Stock Name|Symbol)[:\s]+([A-Z0-9& ]+)'
    matches2 = re.findall(pattern2, text, re.IGNORECASE)
    
    # Combine and normalize
    all_symbols = matches1 + matches2
    normalized = [normalize_symbol(s.strip()) for s in all_symbols]
    
    # Remove duplicates, preserve order
    seen = set()
    result = []
    for sym in normalized:
        if sym not in seen and len(sym) > 2:
            seen.add(sym)
            result.append(sym)
    
    return result
