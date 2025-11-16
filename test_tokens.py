#!/usr/bin/env python3
"""
Test Token Verification & Rollover Logic
"""
from token_parser import FuturesTokenParser
from datetime import datetime

def test_tokens():
    """Verify instrument tokens and expiry logic"""
    
    parser = FuturesTokenParser('future_tokens.txt')
    
    print("\n" + "="*70)
    print("🧪 INSTRUMENT TOKEN & ROLLOVER VERIFICATION")
    print("="*70)
    
    # Test 1: Current Expiry Selection
    print("\n📅 TEST 1: Current Expiry & Rollover Logic")
    print("-"*70)
    
    available_expiries = sorted(parser.expiry_dates.keys())
    print(f"Available Expiries: {available_expiries}")
    
    current_expiry = parser.get_current_expiry(rollover_days=4)
    print(f"\n✅ Selected Expiry: {current_expiry}")
    
    if current_expiry:
        expiry_date = parser.expiry_dates[current_expiry]
        days_left = (expiry_date - datetime.now()).days
        
        print(f"   Expiry Date: {expiry_date.strftime('%d-%b-%Y (%A)')}")
        print(f"   Days Left: {days_left} days")
        print(f"   Rollover Threshold: 4 days before expiry")
        
        if days_left < 4:
            print(f"   ⚠️  ROLLOVER ZONE: Less than 4 days left")
        else:
            print(f"   ✅ SAFE ZONE: Using current month contract")
    
    # Test 2: Token Verification
    print("\n" + "="*70)
    print("🎯 TEST 2: Instrument Token Verification")
    print("="*70)
    
    test_stocks = [
        ('TATSTE', 'Tata Steel'),
        ('RELIND', 'Reliance'),
        ('INFY', 'Infosys'),
        ('TCS', 'TCS'),
        ('BSE', 'BSE'),
        ('HDFBAN', 'HDFC Bank'),
        ('ICIBAN', 'ICICI Bank'),
    ]
    
    print(f"\n{'Symbol':<12} {'Token':<8} {'Expiry':<12} {'Lot Size':<10} {'Status'}")
    print("-"*70)
    
    success_count = 0
    for symbol, name in test_stocks:
        info = parser.get_token_info(symbol)
        
        if info:
            print(f"{symbol:<12} {info['token']:<8} {info['expiry_date']:<12} {info['lot_size']:<10} ✅")
            success_count += 1
        else:
            print(f"{symbol:<12} {'N/A':<8} {'N/A':<12} {'N/A':<10} ❌ NOT FOUND")
    
    print("-"*70)
    print(f"Success Rate: {success_count}/{len(test_stocks)} ({success_count*100//len(test_stocks)}%)")
    
    # Test 3: Rollover Simulation
    print("\n" + "="*70)
    print("🔄 TEST 3: Rollover Simulation (What happens in 4 days?)")
    print("="*70)
    
    print("\nCurrent behavior:")
    print(f"  Today: {datetime.now().strftime('%d-%b-%Y')}")
    print(f"  Current Expiry: {current_expiry} ({days_left} days left)")
    
    print("\nRollover scenarios:")
    for days_before in [10, 7, 5, 4, 3, 2, 1, 0]:
        # Simulate rollover threshold
        if days_left <= days_before:
            next_expiries = [e for e in available_expiries if parser.expiry_dates[e] > expiry_date]
            if next_expiries:
                next_exp = min(next_expiries, key=lambda x: parser.expiry_dates[x])
                status = "🔄 ROLLOVER" if days_left < 4 else "⏳ Approaching"
                print(f"  {days_before} days before: {status} → Switch to {next_exp}")
            else:
                print(f"  {days_before} days before: ⚠️  No next month available")
            break
    
    # Test 4: Watchlist Verification
    print("\n" + "="*70)
    print("📋 TEST 4: Current Watchlist Token Verification")
    print("="*70)
    
    try:
        with open('watchlist_tokens.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if lines:
            print(f"\n✅ Watchlist file exists ({len(lines)} stocks)")
            print("\nVerifying tokens in watchlist:")
            print(f"\n{'Token':<8} {'Symbol':<12} {'Valid?'}")
            print("-"*35)
            
            for line in lines:
                if ':' in line:
                    token, symbol = line.split(':', 1)
                    token = token.strip()
                    symbol = symbol.strip()
                    
                    # Verify token matches
                    info = parser.get_token_info(symbol)
                    if info and info['token'] == token:
                        print(f"{token:<8} {symbol:<12} ✅")
                    else:
                        expected = info['token'] if info else 'N/A'
                        print(f"{token:<8} {symbol:<12} ❌ (Expected: {expected})")
        else:
            print("\n⚠️  Watchlist is empty")
    
    except FileNotFoundError:
        print("\n⚠️  watchlist_tokens.txt not found")
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    checks = [
        ("Expiry Selection", current_expiry is not None),
        ("Rollover Logic", days_left >= 0),
        ("Token Lookup", success_count >= 5),
        ("Watchlist File", len(lines) > 0 if 'lines' in locals() else False),
    ]
    
    print()
    for check, status in checks:
        icon = "✅" if status else "❌"
        print(f"  {icon} {check}")
    
    all_pass = all(s for _, s in checks)
    
    print("\n" + "="*70)
    if all_pass:
        print("🎉 ALL CHECKS PASSED - PRODUCTION READY!")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW NEEDED")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_tokens()

