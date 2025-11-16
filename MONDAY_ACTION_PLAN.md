# 🚀 MONDAY MORNING - COMPLETE ACTION PLAN

**Date:** November 18, 2025  
**Status:** ✅ PRODUCTION READY  
**System:** Professional-Grade High-Probability Futures Trading Engine

---

## 📋 PRE-MARKET CHECKLIST (8:30 - 9:10 AM)

### ⏰ 8:30 AM - Breeze API Setup
```
1. Open browser
2. Go to: https://api.icicidirect.com/apiuser/login
3. Login with credentials
4. Open Developer Tools (F12)
5. Go to: Application → Cookies
6. Find: "session_token"
7. Copy value
8. Edit: config.py
9. Paste in: BREEZE_SESSION_TOKEN = "YOUR_TOKEN_HERE"
10. Save file
```

**⚠️ CRITICAL:** Token expires daily. Must update before 9:15 AM!

---

### ⏰ 8:45 AM - Start Automated Pipeline
```powershell
# Open terminal in project directory
cd C:\Users\Vivek\nse-intraday-data

# Activate virtual environment
.\my_project_env\Scripts\Activate.ps1

# Run master pipeline
python master_trading_pipeline.py
```

**Wait for Phase 1 (Data Collection) to complete...**

Expected output:
```
✅ NSE Snapshot: nse_snapshot_20251118_HHMMSS.json
✅ Global Indices: global_indices_20251118_HHMMSS.json
✅ Pre-open Data: preopen_20251118_HHMMSS.json
✅ analysis_prompt.txt updated with all 3 URLs
```

---

### ⏰ 9:00 AM - AI Analysis Phase

**When prompted, press ENTER to continue...**

```
📋 What will happen:
1. Browser opens automatically (Perplexity.ai)
2. Prompt is copied to clipboard
3. You paste (Ctrl+V) in Perplexity
4. Wait for AI analysis (2-3 minutes)
5. Copy full response (Ctrl+A, Ctrl+C)
6. Return to terminal
7. Press ENTER
8. Script extracts symbols automatically
```

**Expected AI response format:**
```
🎯 RECOMMENDED SYMBOLS (for automated watchlist):
SYMBOL: TATASTEEL
SYMBOL: RELIANCE
SYMBOL: INFY

[Then detailed analysis with 6 factors for each stock...]
```

---

### ⏰ 9:10 AM - Verify Watchlist

```powershell
# Check generated watchlist
type watchlist_tokens.txt
```

**Expected content:**
```
# Watchlist Tokens for Live Monitoring
# Format: token:symbol
# Generated: 2025-11-18 09:10:15

49115:TATSTE
49078:RELIND
49095:INFY
```

**Verify:**
- [ ] 3-5 stocks listed
- [ ] Format: `token:symbol` (correct)
- [ ] All symbols from AI recommendation

---

## 🎯 AI ANALYSIS VALIDATION (9:00 - 9:14 AM)

### For EACH recommended stock, verify AI provided:

**✅ Basic Information:**
- [ ] Symbol clearly stated (SYMBOL: XXX)
- [ ] Trade direction (LONG/SHORT)
- [ ] Futures contract (Nov 2025)
- [ ] Lot size mentioned

**✅ Entry Strategy:**
- [ ] Entry zone (price range)
- [ ] Stop loss (specific level)
- [ ] Target 1 (conservative)
- [ ] Target 2 (aggressive)
- [ ] Risk:Reward ratio (min 1:2)

**✅ Six Factor Analysis:**
- [ ] Factor 1: FII/DII positioning (with numbers)
- [ ] Factor 2: OI + Price action (% changes)
- [ ] Factor 3: Volatility (IV %, expected range)
- [ ] Factor 4: Global context (alignment)
- [ ] Factor 5: Pre-open signals (gap/volume)
- [ ] Factor 6: Technical setup (levels)

**✅ Risk Management:**
- [ ] Risk factors listed (what can go wrong)
- [ ] Trade plan (bullish/bearish scenarios)
- [ ] Probability assessment (%)
- [ ] Conviction level (⭐ rating)

**✅ Confluence Score:**
- [ ] 3-4 factors aligned → High probability (60-70%)
- [ ] 5-6 factors aligned → Very high probability (75-85%)

**❌ If AI response is generic/shallow:**
```
→ Ask for more detail on specific factors
→ Request probability assessment
→ Ask for risk factors analysis
```

---

## 📡 LIVE MONITORING (9:15 AM - 3:30 PM)

### ⏰ 9:14 AM - Start Live Monitoring

**When prompted, press ENTER to begin...**

```
Expected output:
🔗 Connecting to Breeze WebSocket...
✓ Connected!
📊 Monitoring 3 stocks:
   • TATSTE (49115)
   • RELIND (49078)
   • INFY (49095)

📈 Live Tick Data:
[2025-11-18 09:15:02] TATSTE: ₹857.50 | LTP: ₹858.00 | Vol: 125K
[2025-11-18 09:15:03] RELIND: ₹2,863.25 | LTP: ₹2,864.00 | Vol: 89K
...
```

**Verify:**
- [ ] WebSocket connected
- [ ] All 3-5 stocks streaming
- [ ] Tick data updating (every second)
- [ ] CSV files created in `tick_data/` folder

---

## 💰 TRADE EXECUTION (9:15 AM - 3:00 PM)

### Entry Timing Strategy

**🎯 Best Entry Window: 9:20 - 9:45 AM**

**Why?**
- Gap settles down
- Initial volatility absorbed
- Clear direction emerges
- Better risk:reward entries

**❌ Avoid:**
- 9:15 - 9:20 AM (extreme volatility)
- 12:30 - 1:30 PM (lunch lull)
- After 2:30 PM (less time for targets)

---

### Entry Checklist (For EACH Trade)

**Before Entering:**

**☐ Confirm Confluence (3+ factors aligned):**
- [ ] FII/DII positioned correctly
- [ ] OI buildup/unwinding as expected
- [ ] Pre-open gap confirmed/sustained
- [ ] Technical level reached
- [ ] Global sentiment still aligned

**☐ Live Price Action:**
- [ ] Price in entry zone (as per AI)
- [ ] Volume confirming (above average)
- [ ] No immediate reversal signals
- [ ] Order flow bullish/bearish (as needed)

**☐ Risk Management:**
- [ ] Calculate position size (2% capital risk)
- [ ] Max 2-3 lots per stock
- [ ] Stop loss level clear (as per AI)
- [ ] Risk per lot = (Entry - SL) × Lot Size
- [ ] Total risk acceptable

**☐ Trade Setup:**
- [ ] Open ICICI Breeze terminal
- [ ] Select Futures contract (Nov 2025)
- [ ] Enter order (limit/market as appropriate)
- [ ] Place stop loss immediately
- [ ] Set alerts for Target 1 & Target 2

---

### Position Management

**At Target 1 (First Profit Level):**
```
→ Book 50% position
→ Move stop loss to entry (risk-free trade)
→ Let 50% run for Target 2
```

**At Target 2 (Second Profit Level):**
```
→ Book remaining 50%
→ Exit completely
→ Log trade details
```

**If Stop Loss Hit:**
```
→ Exit immediately (no hesitation)
→ Do NOT average down
→ Accept loss (it's part of trading)
→ Move to next setup
```

**Intraday Rule:**
```
→ Exit ALL positions by 2:45 PM
→ Don't carry overnight (intraday only)
→ Book whatever profit/loss exists
```

---

## 📊 MONITORING & ADJUSTMENT

### Real-Time Monitoring

**Watch Tick Data:**
- Price movement (towards entry/target?)
- Volume patterns (increasing/decreasing?)
- Order flow (buying/selling pressure?)

**Cross-Check Confluence:**
- Is OI still building? (check NSE website)
- Any news/events affecting stock?
- Market sentiment changed? (check Nifty)
- Global markets reversed? (check Gift Nifty)

**Adjust If Needed:**
- If confluence breaks → Exit early
- If target reached fast → Book profit
- If ranging near entry → Wait patiently
- If against you → Respect stop loss

---

## 🚨 RISK MANAGEMENT RULES (NON-NEGOTIABLE!)

```
1. Max Risk Per Trade: 2% of capital
   Example: ₹5L capital → Max loss ₹10K per trade

2. Max Position Size: 2-3 lots per stock
   (Based on lot size and stop loss distance)

3. Max Open Positions: 3 stocks simultaneously
   (Don't over-diversify, focus on best setups)

4. Total Capital at Risk: Max 6%
   (3 trades × 2% each = ₹30K on ₹5L capital)

5. ALWAYS Use Stop Loss
   (No exceptions, no "wait and see")

6. NEVER Average Down
   (If wrong, accept it. Don't throw good money after bad)

7. Book Partial Profits
   (50% at Target 1, trail remaining 50%)

8. Time Stop
   (Exit all by 2:45 PM, no overnight positions)

9. Daily Loss Limit: 6% of capital
   (If hit, STOP trading for the day)

10. No Revenge Trading
    (If loss, don't chase it back impulsively)
```

**These rules protect you from catastrophic losses!**

---

## 📝 POST-MARKET REVIEW (After 3:30 PM)

### Trade Analysis

**For EACH trade taken:**

```
Trade Log Template:
------------------
Date: 2025-11-18
Stock: TATASTEEL
Direction: LONG
Lot Size: 3,750 shares
Lots Taken: 2

Entry: ₹858 (planned ₹855-860 ✓)
Stop: ₹842 (as per AI)
Target 1: ₹878 (planned)
Target 2: ₹895 (planned)

Actual Exit: ₹882 (Target 1 reached)
Result: PROFIT
P&L: ₹90,000 (₹24 × 3,750 × 2 lots × 50%)

Confluence Factors:
✓ Factor 1: FII long ₹2,450 cr ✓
✓ Factor 2: OI +23% ✓
✓ Factor 3: IV 38% (high) ✓
✓ Factor 4: Global metals up ✓
✓ Factor 5: Gap +1.2% sustained ✓
✓ Factor 6: Breakout ₹860 ✓

What Went Right:
- All 6 factors aligned (very high probability)
- Gap sustained as predicted
- Entry on pullback to ₹858 (good timing)
- Volume confirmed breakout
- Target 1 reached in 90 minutes

What Went Wrong:
- (If applicable)

Learnings:
- High confluence setups work (6/6 factors)
- Patience paid off (waited for pullback)
- Partial profit booking was wise (locked gains)

Next Time:
- (Any adjustments for similar setups)
```

---

### Review Questions

**Setup Quality:**
- [ ] Did AI analysis have 3+ factor confluence?
- [ ] Was reasoning deep and logical?
- [ ] Were probability estimates reasonable?

**Execution Quality:**
- [ ] Did I wait for proper entry (pullback)?
- [ ] Did I follow stop loss discipline?
- [ ] Did I book partial profits as planned?
- [ ] Did I exit by 2:45 PM?

**Risk Management:**
- [ ] Position size correct (2% risk)?
- [ ] Max 3 stocks open?
- [ ] Total risk under 6%?
- [ ] No averaging down?

**Psychological:**
- [ ] Followed plan (no impulsive trades)?
- [ ] Accepted losses without revenge trading?
- [ ] Stayed disciplined throughout?
- [ ] No FOMO on other stocks?

---

## 📈 WEEKLY PERFORMANCE TRACKING

### Target Metrics (Week of Nov 18-22)

```
Win Rate Target: 60%+
(6 wins out of 10 trades minimum)

Avg Risk:Reward: 1:2+
(Reward should be 2x or more than risk)

Max Drawdown: < 10%
(Capital should not drop more than 10% from peak)

Profit Factor: 2.0+
(Total profits / Total losses should be 2.0+)
```

**Monday Results:**
```
Trades Taken: ___
Wins: ___
Losses: ___
Win Rate: ___%

Total Risk: ₹_____
Total Reward: ₹_____
R:R Ratio: 1:___

Net P&L: ₹_____ (___% of capital)
```

**If Below Targets:**
- Review AI prompt quality
- Check if following recommendations
- Verify risk management adherence
- Consider reducing position size
- Take break if emotional

---

## 🎯 SUCCESS CRITERIA

**A successful Monday means:**

✅ **Process:**
- [ ] Pipeline ran smoothly (no errors)
- [ ] AI analysis was detailed (6 factors)
- [ ] Only took 3+ confluence trades
- [ ] Followed entry/exit plan
- [ ] Respected all risk rules

✅ **Outcome:**
- [ ] Win rate 60%+ (or)
- [ ] Avg R:R 1:2+ (or)
- [ ] Net positive P&L (or)
- [ ] Learned from losing trades

**Remember:** Process > Outcome!  
Even if P&L is negative, if process was perfect, you're successful.  
Over time, good process → good results.

---

## 💡 FINAL REMINDERS

```
🎯 Quality > Quantity
   → Wait for 3+ factor setups
   → Don't trade for the sake of trading

🧠 Trust the AI
   → It's analyzing 6 factors, you're not
   → Follow recommendations unless clear reversal

💰 Manage Risk
   → 2% per trade, always stop loss
   → This protects you from ruin

⏰ Time Management
   → Best entries: 9:20-9:45 AM
   → Exit all: By 2:45 PM

📊 Review Daily
   → What worked? What didn't?
   → Improve for tomorrow

😌 Stay Calm
   → Losses happen (40% of time minimum)
   → Stick to plan, trust probability
```

---

## 🚀 MONDAY QUICK CHECKLIST

```
☐ 8:30 AM → Update Breeze token (config.py)
☐ 8:45 AM → Run master_trading_pipeline.py
☐ 9:00 AM → Paste prompt in Perplexity
☐ 9:10 AM → Verify watchlist (3-5 stocks)
☐ 9:14 AM → Start live monitoring
☐ 9:15 AM → Market opens
☐ 9:20 AM → Look for entry signals
☐ 9:30 AM → Execute high-confluence trades
☐ 12:00 PM → Monitor positions
☐ 2:45 PM → Exit all positions
☐ 4:00 PM → Review & log trades
```

---

## 📞 SUPPORT

**Technical Issues:**
- Check config.py (token updated?)
- Verify internet connection
- Restart pipeline if needed
- Review error messages

**Trading Issues:**
- Review AI analysis (confluence?)
- Check tick data (price action?)
- Verify you followed plan
- Don't panic - stick to rules

---

## ✅ CONFIDENCE CHECK

**Before Starting Trading:**

```
I have:
☐ Updated Breeze session token
☐ Run the automated pipeline
☐ Received detailed AI analysis
☐ Verified 3+ factor confluence for each stock
☐ Created watchlist with valid tokens
☐ Started live monitoring
☐ Reviewed entry/exit plans
☐ Calculated position sizes
☐ Set stop losses ready
☐ Understood risk management rules
☐ Mentally prepared for wins AND losses
☐ Printed/reviewed this action plan

If ALL checked → READY TO TRADE! 🚀
```

---

**Last Updated:** 2025-11-16 23:45 IST  
**Status:** ✅ PRODUCTION READY  
**Next Action:** Monday 8:30 AM - Update Breeze token & START!

---

**Happy Trading! May the probabilities be with you! 📈💰**

