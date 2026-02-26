import subprocess, sys

def install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install("pandas")
install("numpy") 
install("matplotlib")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_backtest_results(json_data):
    # Create summary table
    summary = pd.DataFrame(json_data["backtest_summary"])
    summary = summary[["strategy", "win_rate", "avg_return_per_trade", 
                      "total_return_compounded", "sharpe_annualized_5m",
                      "max_drawdown", "recent_win_rate_last_288_trades_or_less"]]
    
    # Plot win rates
    plt.figure(figsize=(10,6))
    plt.bar(summary["strategy"], summary["win_rate"])
    plt.title("Win Rates by Strategy")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("win_rates.png")
    
    # Plot cumulative returns
    plt.figure(figsize=(10,6))
    plt.bar(summary["strategy"], summary["total_return_compounded"])
    plt.title("Total Returns by Strategy") 
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("returns.png")
    
    # Get best strategy
    best = json_data["best_strategy"]
    
    # Get actionable signal
    signal = json_data["actionable_signals"]
    
    return {
        "summary": summary.to_dict("records"),
        "best_strategy": {
            "name": best["strategy"],
            "win_rate": best["win_rate"],
            "sharpe": best["sharpe_annualized_5m"]
        },
        "signal": {
            "direction": signal["side"],
            "confidence": signal["confidence"]
        }
    }

if __name__ == "__main__":
    # Read JSON from stdin
    import json
    json_data = json.load(sys.stdin)
    results = analyze_backtest_results(json_data)
    print(json.dumps(results, indent=2))