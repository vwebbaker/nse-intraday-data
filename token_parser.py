"""
NSE Futures Token Parser
Parses futures token file and provides active contract tokens based on expiry logic
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


class FuturesTokenParser:
    
    def __init__(self, token_file="future_tokens.txt"):
        """
        Initialize token parser
        
        Args:
            token_file: Path to futures token file
        """
        self.token_file = Path(token_file)
        self.token_map = {}
        self.expiry_dates = {}
        
        if self.token_file.exists():
            self._load_tokens()
        else:
            print(f"⚠️ Token file not found: {token_file}")
    
    def _load_tokens(self):
        """Load and parse token file"""
        print(f"📂 Loading tokens from: {self.token_file}")
        
        try:
            # Read file with tab separator (more reliable)
            df = pd.read_csv(
                self.token_file, 
                sep='\t',
                dtype={'Token': str, 'ExpiryDate': str},
                on_bad_lines='skip'  # Skip malformed lines
            )
            
            # Filter only stock futures
            df = df[df['InstrumentName'] == 'FUTSTK']
            
            print(f"✓ Found {len(df)} stock futures contracts")
            
            # Build token map: {symbol: {expiry: {token, lot_size, ...}}}
            for _, row in df.iterrows():
                try:
                    symbol = str(row['ShortName']).strip()
                    expiry = str(row['ExpiryDate']).strip()
                    
                    # Skip if essential fields are missing
                    if not symbol or not expiry or symbol == 'nan':
                        continue
                    
                    if symbol not in self.token_map:
                        self.token_map[symbol] = {}
                    
                    # Safe type conversion with error handling
                    try:
                        lot_size = int(float(row['LotSize']))
                    except (ValueError, TypeError):
                        lot_size = 1  # Default fallback
                    
                    try:
                        tick_size = float(row['TickSize'])
                    except (ValueError, TypeError):
                        tick_size = 0.05  # Default fallback
                    
                    try:
                        asset_name = str(row['AssetName']).strip()
                    except:
                        asset_name = symbol
                    
                    self.token_map[symbol][expiry] = {
                        'token': str(row['Token']).strip(),
                        'lot_size': lot_size,
                        'tick_size': tick_size,
                        'asset_name': asset_name,
                        'expiry_date': expiry
                    }
                    
                    # Track expiry dates
                    if expiry not in self.expiry_dates:
                        self.expiry_dates[expiry] = self._parse_expiry_date(expiry)
                
                except Exception as e:
                    # Skip problematic rows
                    continue
            
            print(f"✓ Loaded {len(self.token_map)} unique symbols")
            print(f"✓ Available expiries: {sorted(self.expiry_dates.keys())}")
            
        except Exception as e:
            print(f"❌ Error loading tokens: {e}")
            raise
    
    def _parse_expiry_date(self, expiry_str):
        """
        Parse expiry date string to datetime
        Supports multiple formats:
        - MM/DD/YY (e.g., "11/25/25" = Nov 25, 2025)
        - DDMMYY (e.g., "112525" = 25-Nov-2025)
        """
        try:
            # Format 1: MM/DD/YY (with slashes)
            if '/' in expiry_str:
                month, day, year = expiry_str.split('/')
                month = int(month)
                day = int(day)
                year = 2000 + int(year)
                return datetime(year, month, day)
            
            # Format 2: DDMMYY (without slashes)
            elif len(expiry_str) == 6:
                day = int(expiry_str[0:2])
                month = int(expiry_str[2:4])
                year = 2000 + int(expiry_str[4:6])
                return datetime(year, month, day)
            
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_current_expiry(self, rollover_days=4):
        """
        Get current active expiry based on rollover logic
        
        Args:
            rollover_days: Days before expiry to switch to next month
        
        Returns:
            str: Expiry code (e.g., "112525")
        """
        today = datetime.now()
        
        # Find nearest expiry
        valid_expiries = []
        for expiry_str, expiry_date in self.expiry_dates.items():
            if expiry_date and expiry_date >= today:
                days_left = (expiry_date - today).days
                valid_expiries.append((expiry_str, expiry_date, days_left))
        
        # Sort by expiry date
        valid_expiries.sort(key=lambda x: x[1])
        
        if not valid_expiries:
            print("⚠️ No valid expiries found!")
            return None
        
        # Check if we should rollover
        current_expiry, current_date, days_left = valid_expiries[0]
        
        if days_left < rollover_days:
            # Switch to next month
            if len(valid_expiries) > 1:
                next_expiry = valid_expiries[1][0]
                print(f"🔄 Rollover: {days_left} days to expiry")
                print(f"   Switching from {current_expiry} to {next_expiry}")
                return next_expiry
            else:
                print(f"⚠️ No next month contract available!")
                return current_expiry
        else:
            print(f"✓ Using current month: {current_expiry} ({days_left} days left)")
            return current_expiry
    
    def get_token_info(self, symbol, expiry=None):
        """
        Get token info for a symbol
        
        Args:
            symbol: Stock symbol (e.g., "TATSTE", "RELIND")
            expiry: Expiry code (optional, auto-selects if not provided)
        
        Returns:
            dict: Token info or None if not found
        """
        # Normalize symbol
        symbol = symbol.upper()
        
        # Check if symbol exists
        if symbol not in self.token_map:
            print(f"⚠️ Symbol not found: {symbol}")
            return None
        
        # Auto-select expiry if not provided
        if expiry is None:
            expiry = self.get_current_expiry()
        
        # Get token info
        if expiry in self.token_map[symbol]:
            return self.token_map[symbol][expiry]
        else:
            print(f"⚠️ Expiry {expiry} not available for {symbol}")
            available = list(self.token_map[symbol].keys())
            print(f"   Available expiries: {available}")
            return None
    
    def get_tokens_for_symbols(self, symbols, expiry=None):
        """
        Get token info for multiple symbols
        
        Args:
            symbols: List of symbols
            expiry: Expiry code (optional)
        
        Returns:
            dict: {symbol: token_info}
        """
        result = {}
        
        for symbol in symbols:
            token_info = self.get_token_info(symbol, expiry)
            if token_info:
                result[symbol] = token_info
        
        return result
    
    def search_symbol(self, partial_name):
        """
        Search for symbols containing partial name
        
        Args:
            partial_name: Partial symbol or company name
        
        Returns:
            list: Matching symbols
        """
        partial_upper = partial_name.upper()
        matches = []
        
        for symbol, contracts in self.token_map.items():
            # Check symbol
            if partial_upper in symbol:
                matches.append(symbol)
                continue
            
            # Check asset name
            for contract_info in contracts.values():
                if partial_upper in contract_info['asset_name'].upper():
                    matches.append(symbol)
                    break
        
        return sorted(set(matches))
    
    def get_symbol_from_asset_name(self, asset_name):
        """
        Get symbol from full asset name
        
        Args:
            asset_name: Full company name (e.g., "TATA STEEL LIMITED")
        
        Returns:
            str: Symbol or None
        """
        asset_upper = asset_name.upper()
        
        for symbol, contracts in self.token_map.items():
            for contract_info in contracts.values():
                if contract_info['asset_name'].upper() == asset_upper:
                    return symbol
        
        return None
    
    def list_all_symbols(self):
        """Get list of all available symbols"""
        return sorted(self.token_map.keys())
    
    def print_token_info(self, symbol, expiry=None):
        """Print formatted token information"""
        token_info = self.get_token_info(symbol, expiry)
        
        if token_info:
            print(f"\n{'='*50}")
            print(f"Symbol: {symbol}")
            print(f"{'='*50}")
            print(f"Token:       {token_info['token']}")
            print(f"Asset Name:  {token_info['asset_name']}")
            print(f"Expiry:      {token_info['expiry_date']}")
            print(f"Lot Size:    {token_info['lot_size']}")
            print(f"Tick Size:   {token_info['tick_size']}")
            print(f"{'='*50}\n")
        else:
            print(f"❌ Token info not found for {symbol}")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_token_parser(token_file="future_tokens.txt"):
    """
    Quick loader function
    
    Returns:
        FuturesTokenParser: Initialized parser
    """
    return FuturesTokenParser(token_file)


def get_watchlist_tokens(symbols, token_file="future_tokens.txt"):
    """
    Get tokens for a watchlist of symbols
    
    Args:
        symbols: List of symbols
        token_file: Path to token file
    
    Returns:
        dict: {symbol: token_info}
    """
    parser = FuturesTokenParser(token_file)
    return parser.get_tokens_for_symbols(symbols)


# ============================================================
# TESTING / EXAMPLE USAGE
# ============================================================

def main():
    """Test the token parser"""
    
    print("\n" + "="*70)
    print("🔍 NSE FUTURES TOKEN PARSER TEST")
    print("="*70 + "\n")
    
    # Initialize parser
    parser = FuturesTokenParser("future_tokens.txt")
    
    # Test 1: Get current expiry
    print("\n📅 Current Expiry Check:")
    print("-" * 70)
    current_expiry = parser.get_current_expiry(rollover_days=4)
    
    # Test 2: Get specific token
    print("\n🔎 Token Lookup Test:")
    print("-" * 70)
    test_symbols = ["TATSTE", "RELIND", "INFY", "TCS", "SBIN"]
    
    for symbol in test_symbols:
        token_info = parser.get_token_info(symbol)
        if token_info:
            print(f"✓ {symbol:10s} → Token: {token_info['token']:6s} | "
                  f"Lot: {token_info['lot_size']:>5d} | "
                  f"Expiry: {token_info['expiry_date']}")
    
    # Test 3: Search functionality
    print("\n🔍 Search Test (TATA):")
    print("-" * 70)
    matches = parser.search_symbol("TATA")
    print(f"Found {len(matches)} matches: {matches[:10]}")
    
    # Test 4: Bulk token fetch
    print("\n📋 Watchlist Token Fetch:")
    print("-" * 70)
    watchlist = ["TATSTE", "RELIND", "INFY"]
    tokens = parser.get_tokens_for_symbols(watchlist)
    
    for symbol, info in tokens.items():
        print(f"  {symbol}: {info['token']} (Lot: {info['lot_size']})")
    
    # Test 5: Print detailed info
    print("\n📊 Detailed Token Info:")
    parser.print_token_info("TATSTE")
    
    print("\n" + "="*70)
    print("✅ TOKEN PARSER TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
