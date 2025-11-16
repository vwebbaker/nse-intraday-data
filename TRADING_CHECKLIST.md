# ✅ MONDAY MORNING - TRADING CHECKLIST

**Quick Reference Card for High-Probability Futures Trading**

---

## ⏰ PRE-MARKET (8:30 - 9:10 AM)

```
☐ 8:30 AM → Login to ICICI Breeze (get fresh session token)
☐ 8:35 AM → Update BREEZE_SESSION_TOKEN in config.py
☐ 8:40 AM → Activate virtual environment (my_project_env)
☐ 8:45 AM → Run: python master_trading_pipeline.py
☐ 8:50 AM → Wait for Phase 1 completion (data collection)
☐ 8:55 AM → Verify analysis_prompt.txt has 3 URLs
☐ 9:00 AM → Press ENTER to start AI analysis phase
```

---

## 🤖 AI ANALYSIS PHASE (9:00 - 9:10 AM)

```
☐ Browser opens (Perplexity)
☐ Paste prompt (Ctrl+V)
☐ Send to AI
☐ Wait for detailed analysis (2-3 minutes)
☐ Verify AI output starts with "SYMBOL: XXX" format
☐ Copy FULL response (Ctrl+A, Ctrl+C)
☐ Return to terminal
☐ Press ENTER
☐ Verify watchlist_tokens.txt created
☐ Check: 3-5 symbols with tokens
```

---

## 📋 AI OUTPUT VALIDATION

**Each stock MUST have:**

```
☐ Clear SYMBOL at the top (SYMBOL: TATASTEEL)
☐ Trade Direction (LONG/SHORT)
☐ Entry Zone (specific price range)
☐ Stop Loss (clear exit level)
☐ Target 1 & Target 2 (two levels)
☐ Risk:Reward ratio (minimum 1:2)

☐ Factor 1: Institutional Positioning (FII/DII data)
☐ Factor 2: OI + Price Dynamics (% change)
☐ Factor 3: Volatility Edge (IV % and range)
☐ Factor 4: Global Context (market alignment)
☐ Factor 5: Pre-Open Signals (gap/volume)
☐ Factor 6: Technical Setup (levels/breakout)

☐ Risk Factors (what can go wrong)
☐ Trade Plan (bullish/bearish scenario)
☐ Conviction Level (probability score)
```

**If AI gives generic output → Ask for more detail!**

---

## 🎯 HIGH-PROBABILITY SETUP CRITERIA

**Before taking ANY trade, verify:**

```
☐ 3+ factors aligned (minimum)
☐ 5+ factors aligned (high conviction)

☐ FII/DII positioned in trade direction
☐ OI + Price action confirms (buildup/unwinding)
☐ High volatility (intraday movement potential)
☐ Global sentiment supports direction
☐ Pre-open confirms (gap/volume/orders)
☐ Clear technical levels (entry/exit)

☐ Risk:Reward minimum 1:2
☐ Stop loss level clear and logical
☐ Position size calculated (max 2-3 lots)
```

**If 3+ boxes NOT checked → SKIP THE TRADE**

---

## 📡 LIVE MONITORING (9:15 AM - 3:30 PM)

```
☐ 9:10 AM → Press ENTER to start live monitoring
☐ 9:15 AM → Verify WebSocket connected
☐ 9:20 AM → Check tick data streaming in console
☐ 9:25 AM → Verify CSV files created in tick_data/

☐ Watch for entry signals (as per AI plan)
☐ Monitor real-time price action
☐ Set alerts at key levels (entry/stop/target)
☐ Update stop loss after partial profit booking
☐ Exit all positions by 2:45 PM (intraday only)
```

---

## 💰 RISK MANAGEMENT (CRITICAL!)

```
☐ Max risk per trade: 2% of capital
☐ Max position: 2-3 lots per stock
☐ Max open positions: 3 stocks simultaneously
☐ Total capital at risk: Max 6% (3 trades × 2%)

☐ ALWAYS use stop loss
☐ NEVER average down
☐ Book 50% profit at Target 1
☐ Trail stop loss for remaining 50%
☐ If stop hit → Accept loss, move to next setup

☐ No revenge trading
☐ No over-trading
☐ Quality > Quantity
```

---

## 🚦 TRADE EXECUTION CHECKLIST

**For EACH trade:**

```
Entry Phase:
☐ Verify confluence (3+ factors)
☐ Check live pre-open (gap confirmed?)
☐ Wait for pullback/consolidation (don't chase)
☐ Enter in price zone recommended by AI
☐ Place stop loss immediately
☐ Calculate lot size (risk = 2% capital)
☐ Set Target 1 & Target 2 alerts

Monitoring Phase:
☐ Watch tick-by-tick data
☐ Monitor OI changes (buildup continuing?)
☐ Check for reversal signals
☐ Stay disciplined (don't exit early on noise)

Exit Phase:
☐ Book 50% profit at Target 1
☐ Move stop to entry (risk-free trade)
☐ Trail stop for remaining 50%
☐ Exit by 2:45 PM (intraday rule)
☐ Log trade (entry/exit/P&L/learnings)
```

---

## 🚨 RED FLAGS - DO NOT TRADE IF:

```
❌ Less than 3 factors aligned
❌ AI reasoning is vague/generic
❌ No clear stop loss level
❌ Risk:Reward below 1:1.5
❌ Stock in F&O ban list
❌ Low OI (weak institutional interest)
❌ High news/event risk (earnings, policy)
❌ Global markets extremely volatile
❌ You're not mentally focused
❌ Internet connection unstable
```

**When in doubt, stay out!**

---

## 📊 DAILY REVIEW (POST-MARKET)

```
☐ Review all trades (winners + losers)
☐ Check if setups played out as expected
☐ Analyze what went right/wrong
☐ Update trading journal
☐ Calculate daily P&L
☐ Review CSV data (tick patterns)
☐ Prepare for next day
```

---

## 🎯 SUCCESS METRICS (WEEKLY)

```
Target Metrics:
☐ Win Rate: 60%+ (6 out of 10 trades)
☐ Average R:R: 1:2+ (reward > 2x risk)
☐ Max Drawdown: < 10% of capital
☐ Discipline Score: 100% (followed plan every time)

If NOT meeting targets:
☐ Review prompt quality
☐ Check if following AI recommendations properly
☐ Verify risk management adherence
☐ Consider reducing position size
```

---

## 💡 QUICK TIPS

```
✅ Best entry window: 9:20-9:45 AM (post-gap stabilization)
✅ Avoid lunch time: 12:30-1:30 PM (low liquidity)
✅ Book profits: 2:30-2:45 PM (before close)
✅ Use snapshots: Review tick_data/ for patterns

✅ Trust the process (confluence-based)
✅ Follow the plan (AI provided clear levels)
✅ Manage risk (2% per trade, always stop loss)
✅ Stay disciplined (don't deviate from plan)
```

---

## 🔄 ROLLOVER AWARENESS

```
Current Expiry: 11/25/25 (November 25, 2025)
Days Left: 8 days
Rollover Trigger: 4 days before expiry (Nov 21)

☐ Monitor rollover activity (5 days before expiry)
☐ Check if liquidity shifting to next month
☐ Script auto-selects next expiry when needed
☐ Verify correct contract in watchlist_tokens.txt
```

---

## 🐛 TROUBLESHOOTING GUIDE

| Issue | Solution | Priority |
|-------|----------|----------|
| **No symbols extracted** | Check AI response format (SYMBOL: XXX) | HIGH |
| **Authentication failed** | Update BREEZE_SESSION_TOKEN | CRITICAL |
| **WebSocket disconnected** | Check internet, restart monitor | HIGH |
| **No tick data** | Verify watchlist_tokens.txt format | MEDIUM |
| **Stop loss hit instantly** | Entry timing wrong, wait for pullback | LOW |

---

## 📞 EMERGENCY CONTACTS

```
ICICI Breeze Support: 1800-267-6767
NSE Helpline: 1800-266-0050

Technical Issues:
☐ Check config.py (token updated?)
☐ Check internet connection
☐ Restart pipeline if needed
☐ Verify Git repo accessible

Trading Issues:
☐ Review AI analysis (confluence present?)
☐ Check if stopped out correctly
☐ Verify you followed the plan
☐ Don't panic - stick to risk management
```

---

## ✅ FINAL PRE-TRADE VERIFICATION

**Before market open at 9:15 AM:**

```
☐ BREEZE_SESSION_TOKEN updated
☐ analysis_prompt.txt has 3 URLs (NSE, Global, Pre-open)
☐ AI analysis received and validated
☐ watchlist_tokens.txt contains 3-5 stocks
☐ All tokens valid (verified in console)
☐ Live monitoring script running
☐ WebSocket connected
☐ Tick data streaming visible
☐ CSV files being created
☐ Trading account open
☐ Capital ready
☐ Risk limits set
☐ Mentally prepared
☐ No distractions
```

**If ALL boxes checked → GREEN LIGHT FOR TRADING! 🚀**

---

## 🎓 REMEMBER:

```
"High-Probability Trading = Patience + Confluence + Discipline"

☐ Wait for 3+ factor setups
☐ Trust the AI reasoning
☐ Follow risk management religiously
☐ Quality > Quantity
☐ Small consistent wins > Big risky bets
```

---

**🎯 TARGET: 60%+ win rate with 1:2+ risk:reward**

**Happy Trading! 📈💰**

---

**Print this checklist and keep it on your desk!**

