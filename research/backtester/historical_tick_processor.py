import pandas as pd
from typing import Generator, Dict, Any

class HistoricalTickProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = pd.DataFrame()

    def load_data(self):
        self.data = pd.read_csv(self.file_path, parse_dates=['timestamp'])
        self.data.sort_values('timestamp', inplace=True)

    def stream_ticks(self) -> Generator[Dict[str, Any], None, None]:
        for _, row in self.data.iterrows():
            yield row.to_dict()

    def get_time_slice(self, start_time: str, end_time: str) -> pd.DataFrame:
        mask = (self.data['timestamp'] >= start_time) & (self.data['timestamp'] <= end_time)
        return self.data.loc[mask]