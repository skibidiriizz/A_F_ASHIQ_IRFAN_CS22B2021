# Demo Video

## 📹 Application Demo Recording

**File**: `Recording 2025-11-04 003547.mp4`  
**Location**: Project root directory (local only)  
**Size**: 106.89 MB

### Why Not in Git?

This video file exceeds GitHub's 100 MB file size limit, so it's excluded from version control via `.gitignore`.

### For Company Reviewers

The demo video is included in the project submission package and demonstrates:

✅ **Real-time Data Ingestion**: WebSocket connection to Binance Futures  
✅ **Market Overview**: Candlestick charts with multiple timeframes  
✅ **Pair Analytics**: Hedge ratio calculation, z-score analysis, correlation heatmaps  
✅ **Backtesting**: Mean-reversion strategy execution with PnL tracking  
✅ **Alert System**: Configurable rule-based alerts  
✅ **Data Export**: CSV export functionality  

### Alternative Hosting Options

If you need to share the video online:

1. **YouTube** (Unlisted): Upload to YouTube with unlisted visibility
2. **Google Drive**: Share with view-only link
3. **Dropbox**: Generate shareable link
4. **OneDrive**: Share via Microsoft cloud
5. **Git LFS**: Use Git Large File Storage (requires setup)

### Screenshots Alternative

For GitHub documentation, consider adding screenshots to a `docs/screenshots/` folder instead:
- Dashboard overview
- Real-time charts
- Analytics results
- Backtest results

These can be referenced in the main README.md for visual documentation.

---

**Note**: The application is fully functional and can be demonstrated live by running:
```bash
py -m streamlit run frontend.py
```
