from mongodb_storage import MongoDBStorage
        print("\u2717 No profile found for AAPL")
    else:
            print("\n\u2717 No backfill metadata found")
        else:
            print(json.dumps(backfill, indent=2, default=str))
            print("\n\u2713 Backfill metadata:")
        if backfill:
        backfill = profile.get('backfill_metadata', {})
        print(f"  Date range: {profile.get('data_date_range', {})}")
        print(f"  Data points: {profile.get('data_points_count', 0)}")
        print("\u2713 Profile found for AAPL")
    if profile:
    profile = storage.get_profile('AAPL')
    storage = MongoDBStorage(settings.mongodb_uri, settings.mongodb_database, settings.mongodb_collection)
if __name__ == '__main__':

import json
from config import settings

