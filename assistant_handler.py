import pyperclip
import webbrowser
import time
from pathlib import Path
from datetime import datetime
from token_parser import FuturesTokenParser
from symbol_mapper import extract_symbols_from_text

class AssistantHandler:
    
    def __init__(self, recommendations_folder="recommendations", token_file="future_tokens.txt"):
        self.recommendations_folder = Path(recommendations_folder)
        self.recommendations_folder.mkdir(exist_ok=True)
        self.token_parser = FuturesTokenParser(token_file)
    
    def send_to_assistant(self, prompt_file="analysis_prompt.txt"):
        """Send analysis prompt to assistant"""
        
        prompt = Path(prompt_file).read_text()
        
        # Copy to clipboard
        pyperclip.copy(prompt)
        print("\n✅ Analysis prompt copied to clipboard!")
        
        # Open Perplexity
        webbrowser.open("https://www.perplexity.ai/")
        print("✅ Browser opened - Paste (Ctrl+V) and send!")
        
        print("\n⏳ Waiting for you to get assistant's response...")
        print("   💡 Copy assistant's full response when ready")
        input("\n   Press ENTER after copying response...")
        
        # Get response from clipboard
        response = pyperclip.paste()
        
        return response
    
    def save_recommendations(self, response):
        """Save assistant's recommendations"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rec_file = self.recommendations_folder / f"recommendations_{timestamp}.txt"
        
        with open(rec_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("📊 AI STOCK RECOMMENDATIONS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n")
            f.write("="*70 + "\n\n")
            f.write(response)
        
        print(f"\n✅ Recommendations saved: {rec_file}")
        
        return rec_file
    
    def extract_and_generate_tokens(self, rec_file):
        """Extract symbols and generate futures tokens"""
        
        # Read recommendation file
        with open(rec_file, 'r', encoding='utf-8') as f:
            recommendation_text = f.read()
        
        # Extract symbols using symbol_mapper
        symbols = extract_symbols_from_text(recommendation_text)
        
        if not symbols:
            print("⚠️ No symbols found in recommendations")
            return []
        
        print(f"\n📋 Extracted Symbols: {symbols}")
        
        # Generate futures tokens using token_parser
        tokens = []
        for symbol in symbols:
            token_info = self.token_parser.get_token_info(symbol)
            if token_info:
                tokens.append({
                    'symbol': symbol,
                    'token': token_info['token'],
                    'lot_size': token_info['lot_size'],
                    'asset_name': token_info['asset_name']
                })
                print(f"   ✓ {symbol:10s} → Token: {token_info['token']}")
            else:
                print(f"   ✗ {symbol:10s} → Token not found")
        
        # Save to file for tick fetcher (format: token:symbol)
        tokens_file = Path("watchlist_tokens.txt")
        with open(tokens_file, 'w') as f:
            f.write("# Generated Watchlist - Futures Tokens\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for item in tokens:
                # Format: token:symbol (as expected by live_tick_monitor.py)
                f.write(f"{item['token']}:{item['symbol']}\n")
        
        print(f"\n✅ Tokens saved: {tokens_file}")
        print("\n📌 Watchlist Ready for Live Monitoring:")
        for item in tokens:
            print(f"   {item['symbol']:10s} | Token: {item['token']:6s} | Lot: {item['lot_size']:>4d}")
        
        return tokens


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main execution flow"""
    print("\n" + "="*70)
    print("🤖 AI-ASSISTED TRADING SETUP")
    print("="*70 + "\n")
    
    handler = AssistantHandler()
    
    # Step 1: Send prompt to AI
    print("STEP 1: Send analysis prompt to AI assistant")
    print("-" * 70)
    response = handler.send_to_assistant()
    
    # Step 2: Save recommendations
    print("\n" + "="*70)
    print("STEP 2: Save AI recommendations")
    print("="*70)
    rec_file = handler.save_recommendations(response)
    
    # Step 3: Extract symbols and generate tokens
    print("\n" + "="*70)
    print("STEP 3: Generate watchlist tokens")
    print("="*70)
    tokens = handler.extract_and_generate_tokens(rec_file)
    
    if tokens:
        print("\n" + "="*70)
        print("✅ SETUP COMPLETE!")
        print("="*70)
        print(f"\n📋 Watchlist ready with {len(tokens)} stocks")
        print("📍 Next step: Run live_tick_monitor.py to start monitoring\n")
        print("Command: python live_tick_monitor.py\n")
    else:
        print("\n⚠️ No tokens generated. Check recommendations file.\n")


if __name__ == "__main__":
    main()
