import json
from pathlib import Path
from datetime import datetime

class BackfillCheckpoint:
    def __init__(self, checkpoint_dir='logs/checkpoints'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    def save_checkpoint(self, symbol, last_processed_date, total_rows, api_calls):
        checkpoint = {
            'symbol': symbol,
            'last_processed_date': last_processed_date.isoformat(),
            'total_rows': total_rows,
            'api_calls': api_calls,
            'timestamp': datetime.now().isoformat()
        }
        path = self.checkpoint_dir / f"{symbol}_checkpoint.json"
        with open(path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    def load_checkpoint(self, symbol):
        path = self.checkpoint_dir / f"{symbol}_checkpoint.json"
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)
    def clear_checkpoint(self, symbol):
        path = self.checkpoint_dir / f"{symbol}_checkpoint.json"
        if path.exists():
            path.unlink()

